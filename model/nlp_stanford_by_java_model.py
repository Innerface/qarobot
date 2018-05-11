# Author: YuYuE (1019303381@qq.com) 2018.01.18
import os
from nltk.tree import Tree


# 基础引用类
class StanfordCoreNLP():
    """docstring for StanfordCoreNLP"""

    def __init__(self, jarpath):
        self.root = jarpath
        self.tempsrcpath = os.path.dirname(os.path.abspath(__file__)) + "/data/temp/tempin"
        self.jarlist = ["ejml-0.23.jar", "javax.json.jar", "jollyday.jar", "joda-time.jar", "protobuf.jar",
                        "slf4j-api.jar", "slf4j-simple.jar", "stanford-corenlp-3.8.0.jar", "xom.jar"]
        self.jarpath = ""
        self.buildjars()

    def buildjars(self):
        for jar in self.jarlist:
            self.jarpath += self.root + jar + ";"

    def savefile(self, path, sent):
        fp = open(path, 'w', encoding='utf-8')
        fp.write(sent)
        fp.close()

    def delfile(self, path):
        os.remove(path)


# 分词
class StanfordSegment(StanfordCoreNLP):
    """docstring for StanfordSegment"""

    def __init__(self, path):
        StanfordCoreNLP.__init__(self, jarpath='')
        self.classfier = "edu.stanford.nlp.pipeline.ChineseSegmenterAnnotator"
        self.__buildcmd(path)

    def __buildcmd(self, path):
        self.cmdline = path + 'segment.bat '

    def tagfile(self, words, model='pku', outpath='tempout'):
        self.savefile(self.tempsrcpath, words)
        os.system(self.cmdline + model + ' ' + self.tempsrcpath + ' UTF-8 0 > ' + outpath)
        self.delfile(self.tempsrcpath)
        result = open(outpath, 'r', encoding='utf-8').read()
        return result


# 词性标注
class StanfordPOSTagger(StanfordCoreNLP):
    """docstring for StanfordPOSTagger"""

    def __init__(self, jarpath, modelpath):
        StanfordCoreNLP.__init__(self, jarpath)
        self.modelpath = modelpath
        self.classfier = "edu.stanford.nlp.tagger.maxent.MaxentTagger"
        self.delimiter = "/"
        self.__buildcmd()

    def __buildcmd(self):
        self.cmdline = 'java -mx1g -cp "' + self.jarpath + '" ' + self.classfier + ' -model "' + self.modelpath + '" -tagSeparator ' + self.delimiter

    # 字节流异常
    def tag(self, sent):
        self.savefile(self.tempsrcpath, sent)
        tagtxt = os.popen(self.cmdline + " -textFile " + self.tempsrcpath, 'r').read()
        self.delfile(self.tempsrcpath)
        return tagtxt

    def tagfile(self, words, outpath='tempout'):
        self.savefile(self.tempsrcpath, words)
        os.system(self.cmdline + ' -textFile ' + self.tempsrcpath + ' > ' + outpath)
        self.delfile(self.tempsrcpath)
        result = open(outpath, 'r', encoding='utf-8').read()
        return result


# 命名实体识别
class StanfordNERTagger(StanfordCoreNLP):
    """docstring for StanfordNERTagger"""

    def __init__(self, jarpath, modelpath):
        StanfordCoreNLP.__init__(self, jarpath)
        self.modelpath = modelpath
        self.classfier = "edu.stanford.nlp.ie.crf.CRFClassifier"
        self.__buildcmd()

    def __buildcmd(self):
        self.cmdline = 'java -mx1g -cp "' + self.jarpath + '" ' + self.classfier + ' -loadClassifier "' + self.modelpath + '"'

    def tag(self, sent):
        self.savefile(self.tempsrcpath, sent)
        tagtxt = os.popen(self.cmdline + ' -textFile ' + self.tempsrcpath, 'r').read()
        self.delfile(self.tempsrcpath)
        return tagtxt

    def tagfile(self, words, outpath='tempout'):
        self.savefile(self.tempsrcpath, words)
        os.system(self.cmdline + ' -textFile ' + self.tempsrcpath + ' > ' + outpath)
        self.delfile(self.tempsrcpath)
        result = open(outpath, 'r', encoding='utf-8').read()
        return result


# 句法分析
class StanfordParser(StanfordCoreNLP):
    """docstring for StanfordParser"""

    def __init__(self, modelpath, jarpath, opttype):
        StanfordCoreNLP.__init__(self, jarpath)
        self.modelpath = modelpath
        self.classfier = "edu.stanford.nlp.parser.lexparser.LexicalizedParser"
        self.opttype = opttype
        self.__buildcmd()

    def __buildcmd(self):
        self.cmdline = 'java -mx500m -cp "' + self.jarpath + '" ' + self.classfier + ' -outputFormat "' + self.opttype + '" ' + self.modelpath + ' '

    def parse(self, sent):
        self.savefile(self.tempsrcpath, sent)
        tagtxt = os.popen(self.cmdline + self.tempsrcpath, "r").read()
        self.delfile(self.tempsrcpath)
        return tagtxt

    def tagfile(self, words, outpath='tempout'):
        self.savefile(self.tempsrcpath, words)
        os.system(self.cmdline + self.tempsrcpath + ' > ' + outpath)
        self.delfile(self.tempsrcpath)
        result = open(outpath, 'r', encoding='utf-8').read()
        return result

def generate_segment(sent):
    """
    分词
    :param sent:
    :return:
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    root =  base_path + "/data/stanford/stanford-segmenter-2017-06-09/"
    stanford_seg = StanfordSegment(root)
    seg_tag = stanford_seg.tagfile(sent, 'ctb')
    return seg_tag

def generate_postag(segment):
    """
    词性标注
    :param segment:
    :return:
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    pos_root = base_path + "/data/stanford/stanford-corenlp-full-2017-06-09/"
    pos_model = pos_root + "models/pos-tagger/chinese-distsim/chinese-distsim.tagger"
    stanford_pos = StanfordPOSTagger(pos_root, pos_model)
    pos_tag = stanford_pos.tagfile(segment)
    return pos_tag

def generate_ner(segment):
    """
    命名实体识别
    :param segment:
    :return:
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    pos_root = base_path + "/data/stanford/stanford-corenlp-full-2017-06-09/"
    ner_model = pos_root + "models/ner/chinese.misc.distsim.crf.ser.gz"
    stanford_ner = StanfordNERTagger(pos_root, ner_model)
    ner_tag = stanford_ner.tag(segment)
    return ner_tag

def generate_partial(segment):
    """
    短语树拆分
    :param segment:
    :return:
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    pos_root = base_path + "/data/stanford/stanford-corenlp-full-2017-06-09/"
    par_model = pos_root + "models/lexparser/chinesePCFG.ser.gz"
    opttype = 'penn'
    parser = StanfordParser(par_model, pos_root, opttype)
    par_tag = parser.tagfile(segment)
    tree = Tree.fromstring(par_tag)
    return tree

def generate_partial_productions(segment):
    """
    短语树拆分
    :param segment:
    :return:
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    pos_root = base_path + "/data/stanford/stanford-corenlp-full-2017-06-09/"
    par_model = pos_root + "models/lexparser/chinesePCFG.ser.gz"
    opttype = 'penn'
    parser = StanfordParser(par_model, pos_root, opttype)
    par_tag = parser.tagfile(segment)
    tree = Tree.fromstring(par_tag)
    pros = tree.productions()
    return pros

def generate_typed_dependencies(segment):
    """
    依存句法分析
    :param segment:
    :return:
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    pos_root = base_path + "/data/stanford/stanford-corenlp-full-2017-06-09/"
    pars_model = pos_root + "models/lexparser/chinesePCFG.ser.gz"
    opttype = 'typedDependencies'
    parser = StanfordParser(pars_model, pos_root, opttype)
    result = parser.tagfile(segment)
    return result


if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    # 分词
    seg_root = base_path + "/data/stanford/stanford-segmenter-2017-06-09/"
    stanford_seg = StanfordSegment(seg_root)
    # sent = u"长城环球通多币借记卡是中国银行发行的银联品牌、具有人民币账户及美元、澳门元、欧元、港币等多种外币账户的白金卡,是中国银行为便利客户在境内外取现和消费而提供的现代化金融支付工具。"
    sent = u"银行是金融机构之一，银行按类型分为：中央银行，政策性银行，商业银行，投资银行，世界银行，它们的职责各不相同"
    print(sent)
    seg_tag = stanford_seg.tagfile(sent, 'ctb')
    print(seg_tag)
    import jieba
    import jieba.posseg as pseg
    word_list = jieba.cut_for_search(sent)
    print(' '.join(word_list))
    words = pseg.cut(sent)
    word_str = ''
    for word,flag in words:
        word_str += word + ' '
    seg_tag = word_str
    print(word_str)
    # 词性标注
    pos_root = base_path + "/data/stanford/stanford-corenlp-full-2017-06-09/"
    pos_model = pos_root + "models/pos-tagger/chinese-distsim/chinese-distsim.tagger"
    stanford_pos = StanfordPOSTagger(pos_root, pos_model)
    pos_tag = stanford_pos.tagfile(seg_tag)
    print(pos_tag)
    # 命名实体识别
    ner_model = pos_root + "models/ner/chinese.misc.distsim.crf.ser.gz"
    stanford_ner = StanfordNERTagger(pos_root, ner_model)
    ner_tag = stanford_ner.tag(seg_tag)
    print(ner_tag)
    # 短语结构树
    par_model = pos_root + "models/lexparser/chinesePCFG.ser.gz"
    opttype = 'penn'
    parser = StanfordParser(par_model, pos_root, opttype)
    par_tag = parser.tagfile(seg_tag)
    print(par_tag)
    tree = Tree.fromstring(par_tag)
    tree.draw()
    # 依存句法
    pars_model = pos_root + "models/lexparser/chinesePCFG.ser.gz"
    opttype = 'typedDependencies'
    parser = StanfordParser(pars_model, pos_root, opttype)
    result = parser.tagfile(seg_tag)
    print('YuYuE')
    print(result)
    result = generate_partial(seg_tag)
    print(result)
