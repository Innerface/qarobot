# Author: YuYuE (1019303381@qq.com) 2018.03.22
import os
import jieba
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".."))
# print(os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".."))
import model.nlp_stanford_by_java_model as stanford_java
import model.nlp_ltp_model as ltp_handle

def default_sentence_end():
	return ['。']

def special_sentence_end():
	return ['？','！','?','!']

def combina_corpus(str_):
	"""
	整合语料
	:param str_:
	:return:
	"""
	return str_

def serialize_corpus(str_):
	"""
	序列化语料
	:param str_:
	:return:
	"""
	sents = []
	if os.path.exists(str_):
		file_handle = open(str_,'r',encoding='utf-8')
		file_str = file_handle.read()
		sentence_end = default_sentence_end()
		temp_str = ''
		if file_str:
			if file_str.find("\n") != -1 or file_str.find("\r") != -1:
				temp_str = file_str.replace("\n",'')
				temp_str = temp_str.replace("\r",'')
			else:
				temp_str = file_str
			if temp_str != '':
				sents.append(temp_str)
			if sentence_end:
				for end_ in sentence_end:
					for sent in sents:
						if sent.find(end_) != -1:
							temp_sent = sent.split(end_)
							sents.remove(sent)
							sents.extend(temp_sent)
	return sents

def structure_corpus(str_):
	"""
	结构化处理语料
	:param str_:
	:return:
	"""
	splits = jieba.cut(str_, cut_all=False, HMM=True)
	splits_ = ' '.join(splits)
	tree = stanford_java.generate_partial(splits_)
	pros = stanford_java.generate_partial_productions(splits_)
	segment = splits_.split(' ')
	postag = ltp_handle.generate_postag(str_,segment)
	recognize_result = ltp_handle.generate_recongnize(sentence, segment, postag)
	parse_result = ltp_handle.generate_parse(sentence, segment, postag)
	role = ltp_handle.generate_sementic_role(str_,segment,postag,recognize_result,parse_result)
	print(role)
	return

def siphon_ner(sent):
	"""

	:param sent:
	:return:
	"""
	return sent

def siphon_relation(sent):
	"""

	:param sent:
	:return:
	"""
	return sent

if __name__ == "__main__":
	path = "E:/WWW/spider_for_news/file_set/file_set/银行.txt"
	sentences = serialize_corpus(path)
	# f_out = open('out.txt','w',encoding='utf-8')
	for sentence in sentences:
		print(sentence)
		# f_out.write(sentence+'\n')
		structure_corpus(sentence)
		exit()