# Author: YuYuE (1019303381@qq.com) 2018.01.18
from nltk.parse.stanford import StanfordParser
from nltk.tokenize import StanfordSegmenter
import os

java_path = "C:/Program Files (x86)/Java/jdk1.8.0_144/bin/java.exe"
os.environ['JAVAHOME'] = java_path


def generate_stanford_parser(sentence, path='D:/NLP/stanford/stanford-corenlp-full-2017-06-09/'):
    stanford_parser_dir = path
    # eng_model_path = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
    zh_model_path = "edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz"
    my_path_to_models_jar = stanford_parser_dir + "stanford-parser-3.8.0-models.jar"
    my_path_to_jar = stanford_parser_dir + "stanford-parser.jar"
    parser = StanfordParser(model_path=zh_model_path, path_to_models_jar=my_path_to_models_jar,
                            path_to_jar=my_path_to_jar)
    result = parser.raw_parse(sentence)
    return result


def generate_stanford_segmenter(sentence, path="D:/NLP/stanford/stanford-corenlp-full-2017-06-09/"):
    segmenter = StanfordSegmenter(
        path_to_jar=path + "stanford-segmenter-3.8.0.jar",
        path_to_slf4j=path + "slf4j-api.jar",
        path_to_sihan_corpora_dict=path + "segmenter/data",
        path_to_model=path + "segmenter/data/pku.gz",
        path_to_dict=path + "segmenter/data/dict-chris6.ser.gz")
    result = segmenter.segment(sentence)
    return result


if __name__ == "__main__":
    sentence = "长城钻石信用卡 与 长城世界之极信用卡，重塑 奢华 定义，再创 顶级之作。八 大 极致 尊荣 服务，只 为 给 您 最 极致 的 礼遇，与 您 共同 镌刻 一生 的 回忆 与 经历。"
    result = generate_stanford_parser(sentence)
    # sentence = "长城钻石信用卡与长城世界之极信用卡，重塑奢华定义，再创顶级之作。八大极致尊荣服务，只为给您最极致的礼遇，与您共同镌刻一生的回忆与经历。"
    # result = generate_stanford_segmenter(sentence)
    for res in result:
        print(res)
