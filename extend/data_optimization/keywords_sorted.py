# Author: YuYuE (1019303381@qq.com) 2018.03.16
from faq_app.models import Question_auto
import model.nlp_pinyin_hanzi_transfer as ph_transfer
import model.nlp_jieba_model as jieba_model
import model.nlp_stanford_by_java_model as stanford_model
import model.nlp_ltp_model as ltp_model
from gensim import corpora, models, similarities
import jieba
import os


def default_VP():
	return ['是啥', '是什么', '什么是', '是什么意思']


def default_CC():
	return ['的', '和', '与', '跟']

def default_synonyms():
	return {
		"怎么":"如何",
	}


def keywords_sort(words):
	"""
	关键词统一按音节排序
	:param words:
	:return:
	"""
	word_sort = []
	if words:
		words_p = []
		for word in words:
			hp_ = ph_transfer.transfer_hanzi_to_pinyin(word)
			if hp_:
				words_p.append(hp_)
		words_p_s = sorted(words_p)
		for word_p in words_p_s:
			index = words_p.index(word_p)
			word_sort.append(words[index])
	return word_sort


def siphon_keywords_and_sort(sent, method='jieba'):
	"""
	抽取关键词，并作排序
	:param sent:
	:return:
	"""
	keywords_sorted = []
	if sent:
		if method == 'jieba':
			keywords = jieba_model.remove_stop_words_by_jieba(sent)
		else:
			keywords = ltp_model.generate_segment_after_remove_stop_words(sent)
		if keywords:
			keywords_sorted = keywords_sort(keywords)
		else:
			inner_vp = ''
			vps = default_VP()
			for vp in vps:
				if sent.find(vp) != -1:
					inner_vp = vp
			if inner_vp:
				infos = sent.split(inner_vp)
				if infos:
					len_temp = 0
					for info in infos:
						if len(info) > len_temp:
							keywords_sorted = info
							len_temp = len(info)
			else:
				keywords_sorted = sent
	return keywords_sorted


def siphon_sentence_patial(sent):
	"""
	句子成分抽取
	:param sent:
	:return:
	"""
	if sent:
		segment = jieba_model.generate_jieba_cut(sent)
		print(segment)
		segment = ' '.join(segment)
		ner = stanford_model.generate_ner(segment)
	return ner

def gensim_lsi_simi():
	import logging
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

	# 读入文档
	with open(os.path.dirname(os.path.abspath(__file__)) + "/bank_doc_20180309.txt", "r",encoding='utf-8') as f:
		f = f.readlines()
	# 预处理
	stopwords = ["的", "和", "啊"]
	## 1、去停词、字母小写化
	texts = [[word.lower() for word in jieba.lcut(line.strip()) if word not in stopwords] for line in f]
	## 2、去标点
	punctuations = [',', '.', ':', ';', '?', '!', '(', ')', '[', ']', '@', '&', '#', '%', '$', '{', '}', '--', '-', '，',
	                '。', '：', '；', '？', '！', '（', '）', '【', '】', '—', '_', '"', '“', '”', '|', '、', '<', '《', '>', '》',
	                '~', '/']
	texts = [[word for word in ele if word not in punctuations] for ele in texts]
	# 建立一个字典，字典表示这个词以及这个词在texts语料库中出现的次数
	dictionary = corpora.Dictionary(texts)
	# 将整个语料库文档转化为(id,出现次数)
	corpus = [dictionary.doc2bow(text) for text in texts]
	# 训练一个LSI模型
	lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=20)
	# 如何找到最相关的文档，首先建立索引index
	index = similarities.MatrixSimilarity(lsi[corpus])
	for n in range(0, len(f)):
		compare_text = dictionary.doc2bow(jieba.lcut(f[n].strip().lower()))
		query_lsi = lsi[compare_text]
		sims = index[query_lsi]
		for m, ele in enumerate(sims):
			if ele > 0.6 and ele != 1:
				print("{},{},相似度：{}".format(f[n].strip(), f[m].strip(), ele))
	return
