# Author: YuYuE (1019303381@qq.com) 2018.03.16
import re
from itertools import groupby

from extend.data_optimization import keywords_sorted as doks
from model import generate_word_vector as vectormodel
from model import nlp_pinyin_hanzi_transfer as phtransfer


def remove_special_tags(str_):
	"""
	特殊字符处理,可选择性配置
	:param str_:
	:return:
	"""
	r = '[’!"#$%&\'()*+,-./:;<=>?？。！￥……【】、，：；‘’”“@[\\]^_`{|}~]+'
	result = re.sub(r, '', str_)
	return result

def remove_modal_particle(str_):
	"""
	语气助词处理，可选择性配置
	:param str_:
	:return:
	"""
	modal_particle = ['阿','啊','呃','欸','哇','呀','哦','耶','哟','欤','呕','噢','呦','吧','罢','呗','啵','嘞','哩','咧','咯','啰','喽','吗','嘛','呢','呐','噻','嘢']
	for particle in modal_particle:
		if str_.find(particle) != -1:
			str_ = str_.replace(particle,'')
	return str_

def remove_partial_and_special(sent):
	sent = remove_special_tags(sent)
	sent = remove_modal_particle(sent)
	return sent

def replace_synonyms_words(main_sent_set,words,synonyms_words=False):
	"""
	同义词替换
	:param words:
	:return:
	"""
	if words and main_sent_set and synonyms_words:
		words_str = ' '.join(words)
		main_sent_set_str = ' '.join(main_sent_set)
		synonyms = doks.default_synonyms()
		if synonyms:
			for key in synonyms.keys():
				if main_sent_set_str.find(key) != -1 and words_str.find(synonyms[key]) != -1:
					words_str = words_str.replace(synonyms[key],key)

			words = words_str.split()
	return words

def siphon_synonyms_words(main_sent_set):
	"""
	根据问题找到可能的同义词，较上一个方法效率
	:param main_sent_set:
	:return:
	"""
	synonyms_words= False
	if main_sent_set:
		main_sent_set_str = ' '.join(main_sent_set)
		synonyms = doks.default_synonyms()
		if synonyms:
			for key in synonyms.keys():
				if main_sent_set_str.find(key) != -1:
					synonyms_words = True
	return synonyms_words

def groupby_subscript(lst):
	"""
	连续下标分组
	:param lst:
	:return:
	"""
	groups = []
	fun = lambda x: x[1] - x[0]
	for k, g in groupby(enumerate(lst), fun):
		groups.append([v for i, v in g])
	return groups

def remove_useless_and_correction(inp):
	"""
	去除与语义无关的杂项，并做中文纠正
	1.去除多余标点符号
	2.拼音识别
	3.拼音转换
	4.去语气助词
	:param inp:
	:return:
	"""
	step_one_str = remove_special_tags(inp)
	is_with_alphabet = False
	inner_alphabet = ''
	pos_alphabet = []
	i = 0
	for vchar in step_one_str:
		if phtransfer.is_alphabet(vchar):
			is_with_alphabet =True
			inner_alphabet += vchar
			pos_alphabet.append(i)
		i += 1
	if is_with_alphabet:
		groups = groupby_subscript(pos_alphabet)
		if len(groups) > 1:
			increase_or_decrease = 0
			for group in groups:
				item = ''
				for index in group:
					item += step_one_str[index-increase_or_decrease]
				item_to_hanzi = phtransfer.transfer_continue_pinyin_to_hanzi(item)
				item_to_hanzi_ = ''.join(item_to_hanzi)
				eval_item = vectormodel.words_evaluation(item,item_to_hanzi_)
				if eval_item != None and eval_item != item:
					step_one_str = step_one_str.replace(item,item_to_hanzi_)
					increase_or_decrease = len(item) - len(''.join(item_to_hanzi))
		else:
			alphabet_to_hanzi = phtransfer.transfer_continue_pinyin_to_hanzi(inner_alphabet)
			alphabet_to_hanzi_ = ''.join(alphabet_to_hanzi)
			eval_item = vectormodel.words_evaluation(inner_alphabet, alphabet_to_hanzi_)
			if eval_item != None and inner_alphabet != eval_item:
				step_one_str = step_one_str.replace(inner_alphabet,eval_item)
	step_two_str = remove_modal_particle(step_one_str)
	return step_two_str


def split_sentence_to_words(inp, method='method', mode='HMM'):
	return doks.siphon_keywords_and_sort(inp)


def siphon_keywords_by_tfidf(inp):
	return inp


def siphon_ners_by_nlp(inp, keywords, method='method', mode='HMM'):
	return inp


def siphon_relations_by_nlp(ners, sent, method='method', mode='HMM'):
	return ners


def text_classification(inp, keywords=''):
	return inp


def generate_response(inp, keywords='', ners=None, relations=None, type=None):
	"""
	答案抽取模块，基本流程
	1.FAQ匹配
	2.知识图谱
	3.文档
	4.互联网资源
	:param words_split:
	:param keywords:
	:param ners:
	:param relations:
	:param type:
	:return:
	"""
	response = faq_search(keywords,inp)
	return response

def faq_search(keywords,inp):
	return inp
