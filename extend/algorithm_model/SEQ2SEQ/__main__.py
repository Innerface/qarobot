import os
import re
import sys
import logging
import argparse
import subprocess
import tensorflow as tf
import yaml
import shutil
import tarfile

from pprint import pformat
from operator import itemgetter
from translate import utils
from translate.translation_model import TranslationModel
from translate.multitask_model import MultiTaskModel

parser = argparse.ArgumentParser()
parser.add_argument('config', help='load a configuration file in the YAML format')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
parser.add_argument('--debug', action='store_true', help='debug mode')

# using 'store_const' instead of 'store_true' so that the default value is `None` instead of `False`
parser.add_argument('--reset', action='store_const', const=True, help="reset model (don't load any checkpoint)")
parser.add_argument('--reset-learning-rate', action='store_const', const=True, help='reset learning rate')
parser.add_argument('--learning-rate', type=float, help='custom learning rate (triggers `reset-learning-rate`)')
parser.add_argument('--purge', action='store_true', help='remove previous model files')

parser.add_argument('--crash-test', action='store_const', const=True, help='build dummy batch with the longest sentences to test the memory usage')

# Available actions (exclusive)
parser.add_argument('--decode', nargs='*', help='translate this corpus (corpus name or list of files for each encoder)')
parser.add_argument('--align', nargs='*', help='translate and show alignments by the attention mechanism')
parser.add_argument('--eval', nargs='*', help='compute BLEU score on this corpus (corpus name or source files and target file)')
parser.add_argument('--train', action='store_true', help='train an NMT model')
parser.add_argument('--save', action='store_true')

# TensorFlow configuration
parser.add_argument('--gpu-id', type=int, help='index of the GPU where to run the computation')
parser.add_argument('--no-gpu', action='store_true', help='run on CPU')

# Decoding options (to avoid having to edit the config file)
parser.add_argument('--beam-size', type=int, help='decode using a beam-search decoder with this beam-size (default: greedy)')
parser.add_argument('--len-normalization', type=float, help='normalize final beam scores by hypothesis length with this weight (default: 1, disable: 0)')
parser.add_argument('--no-early-stopping', action='store_const', dest='early_stopping', const=False, help='disable early stopping (which reduces the beam size each time a new finished hypothesis is found)')
parser.add_argument('--ensemble', action='store_const', const=True, help='build an ensemble of models with the list of checkpoints')
parser.add_argument('--average', action='store_const', const=True, help='average all parameters from the list of checkpoints')
parser.add_argument('--checkpoints', nargs='+', help='load this list of checkpoints instead of latest checkpoint')
parser.add_argument('--output', help='write decoding output to this file (instead of standard output)')
parser.add_argument('--max-steps', type=int, help='maximum training updates before stopping')
parser.add_argument('--max-test-size', type=int, help='only decode the first n lines from the test corpus')
parser.add_argument('--remove-unk', action='store_const', const=True, help='remove UNK symbols from decoding output')
parser.add_argument('--raw-output', action='store_const', const=True, help='write raw decoding output (no post-processing)')
parser.add_argument('--pred-edits', action='store_const', const=True, help='predict edit operations instead of words (useful for automatic post-editing')
parser.add_argument('--model-dir', help='use this directory as model root')
parser.add_argument('--batch-size', type=int, help='number of lines in a batch')
parser.add_argument('--no-fix', action='store_const', dest='fix_edits', const=False, help='disable automatic fixing of edit op sequences')
parser.add_argument('--max-output-len', type=int, help='maximum length of the output sequence (control decoding speed)')

parser.add_argument('--unk-replace', action='store_const', const=True, help='replace UNK symbols from decoding output by using attention mechanism')
parser.add_argument('--lexicon', help='lexicon file used for UNK replacement (default: replace with aligned soruce word)')

parser.add_argument('--temperature', type=float, help='temperature of the output softmax')
parser.add_argument('--attn-temperature', type=float, help='temperature of the attention softmax')

parser.add_argument('--align-encoder-id', type=int, default=0, help='id of the encoder whose attention outputs we are interested in (only useful in the multi-encoder setting)')

def main(args=None):
    args = parser.parse_args(args)

    # read config file and default config
    with open('config/default.yaml') as f:
        default_config = utils.AttrDict(yaml.safe_load(f))

    with open(args.config) as f:
        config = utils.AttrDict(yaml.safe_load(f))
        
        if args.learning_rate is not None:
            args.reset_learning_rate = True
        
        # command-line parameters have higher precedence than config file
        for k, v in vars(args).items():
            if v is not None:
                config[k] = v

        # set default values for parameters that are not defined
        for k, v in default_config.items():
            config.setdefault(k, v)

    if args.crash_test:
        config.max_train_size = 0

    if not config.debug:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # disable TensorFlow's debugging logs
    decoding_mode = any(arg is not None for arg in (args.decode, args.eval, args.align))

    # enforce parameter constraints
    assert config.steps_per_eval % config.steps_per_checkpoint == 0, (
        'steps-per-eval should be a multiple of steps-per-checkpoint')
    assert decoding_mode or args.train or args.save, (
        'you need to specify at least one action (decode, eval, align, or train)')
    assert not (args.average and args.ensemble)

    if args.train and args.purge:
        utils.log('deleting previous model')
        shutil.rmtree(config.model_dir, ignore_errors=True)

    os.makedirs(config.model_dir, exist_ok=True)

    # copy config file to model directory
    config_path = os.path.join(config.model_dir, 'config.yaml')
    if args.train and not os.path.exists(config_path):
        with open(args.config) as config_file, open(config_path, 'w') as dest_file:
            content = config_file.read()
            content = re.sub(r'model_dir:.*?\n', 'model_dir: {}\n'.format(config.model_dir), content,
                             flags=re.MULTILINE)
            dest_file.write(content)

    # also copy default config
    config_path = os.path.join(config.model_dir, 'default.yaml')
    if args.train and not os.path.exists(config_path):
        shutil.copy('config/default.yaml', config_path)

    # copy source code to model directory
    tar_path =  os.path.join(config.model_dir, 'code.tar.gz')
    if args.train and not os.path.exists(tar_path):
        with tarfile.open(tar_path, "w:gz") as tar:
            for filename in os.listdir('translate'):
                if filename.endswith('.py'):
                    tar.add(os.path.join('translate', filename), arcname=filename)

    logging_level = logging.DEBUG if args.verbose else logging.INFO
    # always log to stdout in decoding and eval modes (to avoid overwriting precious train logs)
    log_path = os.path.join(config.model_dir, config.log_file)
    logger = utils.create_logger(log_path if args.train else None)
    logger.setLevel(logging_level)

    utils.log('label: {}'.format(config.label))
    utils.log('description:\n  {}'.format('\n  '.join(config.description.strip().split('\n'))))

    utils.log(' '.join(sys.argv))  # print command line
    try:  # print git hash
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
        utils.log('commit hash {}'.format(commit_hash))
    except:
        pass

    utils.log('tensorflow version: {}'.format(tf.__version__))

    # log parameters
    utils.debug('program arguments')
    for k, v in sorted(config.items(), key=itemgetter(0)):
        utils.debug('  {:<20} {}'.format(k, pformat(v)))

    if isinstance(config.dev_prefix, str):
        config.dev_prefix = [config.dev_prefix]

    if config.tasks is not None:
        config.tasks = [utils.AttrDict(task) for task in config.tasks]
        tasks = config.tasks
    else:
        tasks = [config]

    for task in tasks:
        for parameter, value in config.items():
            task.setdefault(parameter, value)

        task.encoders = [utils.AttrDict(encoder) for encoder in task.encoders]
        task.decoders = [utils.AttrDict(decoder) for decoder in task.decoders]

        for encoder_or_decoder in task.encoders + task.decoders:
            for parameter, value in task.items():
                encoder_or_decoder.setdefault(parameter, value)

        if args.max_output_len is not None:   # override decoder's max len
            task.decoders[0].max_len = args.max_output_len

    device = None
    if config.no_gpu:
        device = '/cpu:0'
        device_id = None
    elif config.gpu_id is not None:
        device = '/gpu:{}'.format(config.gpu_id)
        device_id = config.gpu_id
    else:
        device_id = 0

    # hide other GPUs so that TensorFlow won't use memory on them
    os.environ['CUDA_VISIBLE_DEVICES'] = '' if device_id is None else str(device_id)

    utils.log('creating model')
    utils.log('using device: {}'.format(device))

    with tf.device(device):
        config.checkpoint_dir = os.path.join(config.model_dir, 'checkpoints')

        if config.weight_scale:
            if config.initializer == 'uniform':
                initializer = tf.random_uniform_initializer(minval=-config.weight_scale, maxval=config.weight_scale)
            else:
                initializer = tf.random_normal_initializer(stddev=config.weight_scale)
        else:
            initializer = None

        tf.get_variable_scope().set_initializer(initializer)

        # exempt from creating gradient ops
        config.decode_only = decoding_mode

        if config.tasks is not None:
            model = MultiTaskModel(**config)
        else:
            model = TranslationModel(**config)

    # count parameters
    # not counting parameters created by training algorithm (e.g. Adam)
    variables = [var for var in tf.global_variables() if not var.name.startswith('gradients')]
    utils.log('model parameters ({})'.format(len(variables)))
    parameter_count = 0
    for var in sorted(variables, key=lambda var: var.name):
        utils.log('  {} {}'.format(var.name, var.get_shape()))
        v = 1
        for d in var.get_shape():
            v *= d.value
        parameter_count += v
    utils.log('number of parameters: {:.2f}M'.format(parameter_count / 1e6))

    tf_config = tf.ConfigProto(log_device_placement=False, allow_soft_placement=True)
    tf_config.gpu_options.allow_growth = config.allow_growth
    tf_config.gpu_options.per_process_gpu_memory_fraction = config.mem_fraction

    def average_checkpoints(main_sess, sessions):
        for var in tf.global_variables():
            avg_value = sum(sess.run(var) for sess in sessions) / len(sessions)
            main_sess.run(var.assign(avg_value))

    with tf.Session(config=tf_config) as sess:
        best_checkpoint = os.path.join(config.checkpoint_dir, 'best')

        params = {'variable_mapping': config.variable_mapping, 'reverse_mapping': config.reverse_mapping}
        if config.ensemble and len(config.checkpoints) > 1:
            model.initialize(config.checkpoints, **params)
        elif config.average and len(config.checkpoints) > 1:
            model.initialize(reset=True)
            sessions = [tf.Session(config=tf_config) for _ in config.checkpoints]
            for sess_, checkpoint in zip(sessions, config.checkpoints):
                model.initialize(sess=sess_, checkpoints=[checkpoint], **params)
            average_checkpoints(sess, sessions)
        elif (not config.checkpoints and decoding_mode and
             (os.path.isfile(best_checkpoint + '.index') or os.path.isfile(best_checkpoint + '.index'))):
            # in decoding and evaluation mode, unless specified otherwise (by `checkpoints`),
            # try to load the best checkpoint
            model.initialize([best_checkpoint], **params)
        else:
            # loads last checkpoint, unless `reset` is true
            model.initialize(**config)

        if args.save:
            model.save()
        elif args.decode is not None:
            model.decode(**config)
        elif args.eval is not None:
            model.evaluate(on_dev=False, **config)
        elif args.align is not None:
            model.align(**config)
        elif args.train:
            try:
                model.train(**config)
            except KeyboardInterrupt:
                sys.exit()


if __name__ == '__main__':
    main()
