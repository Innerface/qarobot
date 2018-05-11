# Author: YuYuE (1019303381@qq.com) 2018.01.22
from pyltp import *
import os
from nltk.tree import Tree
from nltk.grammar import DependencyGrammar
from nltk.parse import *

ltp_path = os.path.dirname(os.path.abspath(__file__)) + "/data/ltp_data/"
# ltp相关数据文件配置
cws_model = ltp_path + "cws.model"
ner_model = ltp_path + "ner.model"
parser_model = ltp_path + "parser.model"
pisrl_model = ltp_path + "pisrl.model"
pos_model = ltp_path + "pos.model"


# 分词
def generate_segement(sentence):
    segmentor = Segmentor()
    segmentor.load(cws_model)
    segment_result = segmentor.segment(sentence)
    return segment_result


# 词性标注
def generate_postag(sentence, segment_result=False):
    if segment_result == False:
        segment_result = generate_segement(sentence)
    # 词性标注
    postagger = Postagger()
    postagger.load(pos_model)
    postag_result = postagger.postag(segment_result)
    return postag_result


# 命名实体识别
def generate_recongnize(sentence, segment_result=False, postag_result=False):
    if segment_result == False:
        segment_result = generate_segement(sentence)
    if postag_result == False:
        postag_result = generate_postag(sentence)
    recognizer = NamedEntityRecognizer()
    recognizer.load(ner_model)
    recognize_result = recognizer.recognize(segment_result, postag_result)
    return recognize_result


# 依存句法分析
def generate_parse(sentence, segment_result=False, postag_result=False):
    if segment_result == False:
        segment_result = generate_segement(sentence)
    if postag_result == False:
        postag_result = generate_postag(sentence)
    parser = Parser()
    parser.load(parser_model)
    parse_result = parser.parse(segment_result, postag_result)
    parser.release()  # 释放模型
    return parse_result

def generate_dependency_graph(sentence, segment_result=False, postag_result=False, parse_result=False):
    if segment_result == False:
        segment_result = generate_segement(sentence)
    if postag_result == False:
        postag_result = generate_postag(sentence)
    if parse_result == False:
        parse_result = generate_parse(sentence,segment_result, postag_result)
    arclen = len(parse_result)
    conll = ""
    for i in range(arclen):
        if parse_result[i].head == 0:
            parse_result[i].relation = "ROOT"
        conll += "\t" + segment_result[i] + "(" + postag_result[i] + ")" + "\t" + postag_result[i] + "\t" + str(parse_result[i].head) + "\t" + parse_result[
            i].relation + "\n"
    conlltree = DependencyGraph(conll)
    tree = conlltree.tree()
    # tree.draw()
    return tree

def generate_sementic_role(sentence, segment_result=False, postag_result=False,recognize_result=False, parse_result=False):
    if segment_result == False:
        segment_result = generate_segement(sentence)
    if postag_result == False:
        postag_result = generate_postag(sentence)
    if parse_result == False:
        parse_result = generate_parse(sentence,segment_result, postag_result)
    if recognize_result == False:
        recognize_result = generate_recongnize(sentence,segment_result, postag_result)
    labeller = SementicRoleLabeller()
    labeller.load(os.path.join(ltp_path, 'srl/'))
    roles = labeller.label(segment_result, postag_result, recognize_result, parse_result)
    wordlist = list(segment_result)
    relations = {}
    i = 0
    for role in roles:
        temp = {}
        # print("rel:", wordlist[role.index])
        temp['rel'] = wordlist[role.index]
        for arg in role.arguments:
            if arg.range.start != arg.range.end:
                # print(arg.name, " ".join(wordlist[arg.range.start:arg.range.end]))
                temp[arg.name] = " ".join(wordlist[arg.range.start:arg.range.end])
            else:
                # print(arg.name, wordlist[arg.range.start])
                temp[arg.name] = wordlist[arg.range.start]
        relations[i] = temp
        i += 1
    return relations


# 去停用词分词
def generate_segment_after_remove_stop_words(sentence, path=False, segment_result=False):
    if path == False:
        path = os.path.dirname(os.path.abspath(__file__)) + "/data/chinese/stopwords.dat"
    stopwords = fetch_stop_words(path)
    if segment_result == False:
        segment_result = generate_segement(sentence)
    result = []
    for seg in segment_result:
        if seg not in stopwords:
            result.append(seg)
    return result


# 获取停用词
def fetch_stop_words(path="./data/chinese/stopwords.dat"):
    try:
        if os.path.exists(path) == False:
            raise Exception("file not exists")
        infile = open(path, 'r', encoding='utf-8')
        stopwordslist = []
        for str in infile.read().split('\n'):
            if str not in stopwordslist:
                stopwordslist.append(str)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return stopwordslist


if __name__ == "__main__":
    sentence = "银行是依法成立的经营货币信贷业务的金融机构"
    segment = generate_segement(sentence)
    postag = generate_postag(sentence, segment)
    for seg, pos in zip(segment, postag):
        print(seg, pos)
    nostop = generate_segment_after_remove_stop_words(sentence, False, segment)
    print(nostop)
    recognize_result = generate_recongnize(sentence,segment, postag)
    par = generate_parse(sentence,segment,postag)
    result = generate_sementic_role(sentence,segment,postag,recognize_result,par)
    print(result)
