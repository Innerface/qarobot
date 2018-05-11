# Author: YuYuE (1019303381@qq.com) 2018.01.23
import extend.data_optimization.keywords_sorted as mdoks
import model.api_of_turing
import model.common_function_model
import model.generate_ai_customer_service as mgaics
import model.generate_dialog_model as mgdm
import model.generate_system_filter as mgsf
import model.generate_word_vector
import model.nlp_jieba_model
import model.nlp_ltp_model
import model.nlp_pinyin_hanzi_transfer
from faq_app.models import Question_auto, db


# 问题别字纠错以及拼音识别
def question_correct(question):
	"""拼音识别"""
	result = ''
	question = model.common_function_model.remove_special_tags(question)
	if model.nlp_pinyin_hanzi_transfer.is_alphabet(question):
		words = model.nlp_pinyin_hanzi_transfer.transfer_continue_pinyin_to_hanzi(question)
		if len(words) > 0:
			result = ''.join(words)
	else:
		result = question
	return result


# 提取关键词
def generate_keywords(question):
	# 去停用词
	if question:
		keywords = model.nlp_jieba_model.remove_stop_words_by_jieba(str(question))
	else:
		keywords = ''
	# print(keywords)
	return keywords


# 组装查询条件
def generate_search_keywords(question, keywords):
	# 取前两个关键词模糊匹配并按点赞数排序
	# 如果去停用词后，关键词超过两个，则只取前两个
	if len(keywords) == 2:
		keywords = ''.join(keywords)
	elif len(keywords) > 2:
		keywords = keywords[0] + keywords[1]
	elif len(keywords) == 1:
		keywords = keywords[0]
	else:
		keywords = question
	return keywords


# 数据库操作剥离，捕捉异常并添加事务回滚
def generate_qa_data_by_question(value='hi', like=False):
	try:
		data = []
		if value.strip() == '':
			return data
		if like:
			data = Question_auto.query.filter(Question_auto.question.like("%" + value + "%")).order_by('-agrees').limit(
				10)
		else:
			data = Question_auto.query.filter_by(question=value)
	except Exception as error:
		Question_auto.roll_back()
		return str(error)
	else:
		return data


# 获取答案，固定jieba分词
def generate_answers(question, keywords):
	if keywords == question and len(question) > 5:
		question_auto = generate_qa_data_by_question(question)
	else:
		question_auto = generate_qa_data_by_question(keywords, True)
	# 如果查询不到结果
	if question_auto.count() < 1:
		question_auto = generate_qa_data_by_question(question, True)
	# 问答相似度计算
	question_origin = question
	question = model.common_function_model.remove_special_tags(question)
	for i in range(question_auto.count()):
		if question_auto[i].question:
			# print(question_auto[i].question)
			ques_ = model.common_function_model.remove_special_tags(question_auto[i].question)
			# print(ques_)
			try:
				simi = model.generate_word_vector.generate_sentence_simi(question, ques_)
			except Exception as error:
				# words = str(error).split('\'')
				if question_origin == question_auto[i].question:
					question_auto[i].simi = '1'
				else:
					question_auto[i].simi = '0'
				continue
			else:
				question_auto[i].simi = str(simi)[0:5]
				del simi
				del ques_
				model.generate_word_vector.clear_mem()
	model.generate_word_vector.clear_mem()
	question_auto = sorted(question_auto, key=lambda qa: qa.simi, reverse=True)
	return question_auto


# 获取最佳答案
def generate_best_answer(question_auto, question, ip='0.0.0.0', user='none'):
	if len(question_auto) > 0:
		best_answer = question_auto[0].answer
	else:
		best_answer = generate_turing_response(question, ip, user)
	return best_answer


# 范围外问题对接图灵机器人
def generate_turing_response(question, loc, user):
	result = model.api_of_turing.generate_turing_response(question, loc, user)
	return result


# 获取答案，分词工具模式可选
def generate_answer_by_mode(question, keywords, mode='jieba'):
	if keywords == question and len(question) > 5:
		question_auto = generate_qa_data_by_question(question)
	else:
		question_auto = generate_qa_data_by_question(keywords, True)
	# 如果查询不到结果
	if question_auto.count() < 1:
		question_auto = generate_qa_data_by_question(question, True)
	# 问答相似度计算
	question_origin = question
	if mode == 'ltp':
		ques = model.nlp_ltp_model.generate_segment_after_remove_stop_words(question)
		ques = remove_special_tags(ques)
	elif mode == 'jieba':
		ques = model.nlp_jieba_model.generate_jieba_cut(question)
		ques = remove_special_tags(ques)
	# ques = model.nlp_jieba_model.generate_jieba_cut(question)
	# ques = remove_special_tags(ques)
	for i in range(question_auto.count()):
		if question_auto[i].question:
			if mode == 'ltp':
				ques_ = model.nlp_ltp_model.generate_segment_after_remove_stop_words(question_auto[i].question)
				ques_ = remove_special_tags(ques_)
			elif mode == 'jieba':
				ques_ = model.nlp_jieba_model.generate_jieba_cut(question_auto[i].question)
				ques_ = remove_special_tags(ques_)
			# ques_ = model.nlp_jieba_model.generate_jieba_cut(question_auto[i].question)
			# ques_ = remove_special_tags(ques_)
			# print(ques_)
			try:
				simi = model.generate_word_vector.generate_sets_simi(ques, ques_)
			# simi = model.generate_word_vector.generate_sets_simi_by_self(ques, ques_)
			except Exception as error:
				# print(error)
				# words = str(error).split('\'')
				if question_origin == question_auto[i].question:
					question_auto[i].simi = '1'
				else:
					question_auto[i].simi = '0'
				continue
			# raise Exception("Exception:", error)
			else:
				question_auto[i].simi = str(simi)[0:5]
				del simi
				del ques_
	model.generate_word_vector.clear_mem()
	question_auto = sorted(question_auto, key=lambda qa: qa.simi, reverse=True)
	return question_auto


# 剔除特殊字符
def remove_special_tags(sets):
	try:
		# if len(sets) < 1:
		# 	raise Exception("input invaild")
		result = []
		for s in sets:
			temp = model.common_function_model.remove_special_tags(s)
			if temp.strip() != '':
				result.append(temp)
	except Exception as error:
		raise Exception("Exception:", error)
	else:
		return result


# 给出最佳答案
def best_ansewer(question,mode=False):
	if mode == False:
		keywords = generate_keywords(question)
		search_keywords = generate_search_keywords(question, keywords)
		question_auto = generate_answer_by_mode(question, search_keywords)
		# ip = request.remote_addr
		best_answer = generate_best_answer(question_auto, question)
	else:
		best_answer = AI_customer_service(question)
	if best_ansewer == '':
		best_answer = generate_turing_response(question)
	return best_answer


def pre_system_filter(inp):
	"""
	任务：
	1.参数检测，是否缺失必要参数 param_filter
	2.信息校验，是否授权请求 auth_filter
	3.过滤违规敏感词，或者拦截 sensitive_filter
	4.用户黑名单拦截，ip电话等，防恶意攻击 black_list_filter
	:param inp: 请求参数
	:return: dic {
				"success":True,//返回码，是否操作成功
				"data":data
				"error":""//错误信息输出
				}
	"""
	after_param_filter = mgsf.param_filter(inp)
	after_black_filter = mgsf.black_list_filter(after_param_filter)
	after_auth_filter = mgsf.auth_filter(after_black_filter)
	after_sensitive_filter = mgsf.sensitive_filter(after_auth_filter)
	return after_sensitive_filter


def recover_or_record_dialog(inp):
	"""
	任务：
	1.检测是否存在前置对话记录 is_dialog_set
	2.若存在，则从中恢复对话环境，若不存在，则初始化对话环境 recover_dialog_model/record_dialog_model
	3.整合用户画像，或者对话环境
	:param inp:
	:return:dic {
				"success":True,//返回码，是否操作成功
				"data":data
				"error":""//错误信息输出
				}
	"""
	if continue_to_go_or_not(inp) == False:
		return inp
	is_dialog_set = mgdm.is_dialog_set(inp)
	if is_dialog_set:
		model_dialog_info = mgdm.recover_dialog_model(inp)
	else:
		model_dialog_info = mgdm.record_dialog_model(inp)
	return model_dialog_info


def AI_customer_service(inp, dia=None):
	"""
	任务：
	1.文本去噪，去除无意义字词
	2.关键字，命名实体识别
	3.实体关系发现
	4.区分问题类型，信息咨询类还是业务办理类
	5.如果是信息咨询类，进行FAQ语义距离计算，抽取最接近FQA
	6.若无相关FAQ，则进入图谱查找答案，图谱未完成阶段，此步骤跳过
	7.图谱答案不佳，则追溯文档资料
	8.如果有较匹配答案，则推出答案时，并推出推荐主题相关问题或者答案，若没有，则学习中……
	9.如果是业务办理类，则需要还原问题所在的业务流程步骤
	10.重复5，6，7步骤查找详细答案，如果找到较匹配答案，则推出答案，并附带业务流程相关的信息推荐
	11.不管哪种类型，均附带推送平行相关关键词
	12.格式化恢复信息并输出
	:param inp:
	:param dia:
	:return:dic {
				"success":True,//返回码，是否操作成功
				"data":data
				"error":""//错误信息输出
				}
	"""
	main_sent = mgaics.remove_useless_and_correction(inp)
	words_split = mgaics.split_sentence_to_words(main_sent, method='method', mode='HMM')
	keywords = mgaics.siphon_keywords_by_tfidf(words_split)
	ners = mgaics.siphon_ners_by_nlp(main_sent,keywords, method='method', mode='HMM')
	relations = mgaics.siphon_relations_by_nlp(ners, main_sent, method='method', mode='HMM')
	type = mgaics.text_classification(main_sent, keywords)
	response = generate_response(main_sent, keywords, ners, relations, type)
	return response


def update_client_dialog_info(inp, dia):
	"""
	任务：
	1.客服核心返回的答案信息+用户数据，编码生成区分用户和平台的唯一性id
	2.绑定缓存唯一性id和回复信息
	3.输出绑定唯一性缓存id
	:param inp:
	:param dia:
	:return:dic {
				"success":True,//返回码，是否操作成功
				"data":data
				"error":""//错误信息输出
				}
	"""
	cache_id = mgdm.update_dialog_model(inp, dia)
	response = mgdm.compose_response(inp, cache_id)
	return response


def transfer_result_to_response(inp, response, dia):
	"""
	任务：
	1.从客服引擎返回的答案数据取必要数据，并格式化
	2.组合用户对话唯一性缓存id，推送返回
	:param inp:
	:param dia:
	:return:dic {
				"success":True,//返回码，是否操作成功
				"data":data
				"error":""//错误信息输出
				}
	"""
	response_ = mgdm.transfer_response(inp, response, dia)
	return response_


def continue_to_go_or_not(inp):
	if inp['success'] == True:
		return True
	else:
		return False


def generate_response(main_sent, keywords, ners, relations, type):
	"""
	答案抽取
	:param main_sent:
	:param keywords:
	:param ners:
	:param relations:
	:param type:
	:return:
	第一步：FAQ主题词精确匹配
	第二步：匹配中的候选问答评分
	若
	"""
	main_keywords_set = ''
	best_answer = ''
	if main_sent:
		main_keywords_set = model.nlp_jieba_model.generate_jieba_cut(main_sent)
		main_keywords_set = ' '.join(main_keywords_set)
		main_keywords_set = main_keywords_set.split()
		synonyms_words = mgaics.siphon_synonyms_words(main_keywords_set)
	if keywords:
		like_is = True
		if main_sent == keywords:
			like_is = False
		sets = fetch_sets_by_words(keywords,like_is)
		if sets:
			for i in range(sets.count()):
				if sets[i].question:
					ques_ = mgaics.remove_partial_and_special(sets[i].question)
					print(ques_)
					try:
						ques_keywords_set = model.nlp_jieba_model.generate_jieba_cut(ques_)
						ques_keywords_set = ' '.join(ques_keywords_set)
						ques_keywords_set = ques_keywords_set.split()
						ques_keywords_set = mgaics.replace_synonyms_words(main_keywords_set,ques_keywords_set,synonyms_words)
						simi = model.generate_word_vector.generate_sets_simi(ques_keywords_set, main_keywords_set)
					except Exception as error:
						if main_sent == ques_:
							sets[i].simi = '1'
						else:
							sets[i].simi = '0'
						continue
					else:
						sets[i].simi = str(simi)[0:5]
						del simi
						del ques_
						model.generate_word_vector.clear_mem()
			model.generate_word_vector.clear_mem()
			sets = sorted(sets, key=lambda qa: qa.simi, reverse=True)
			best_answer = generate_best_answer(sets, main_sent)
	return best_answer

def fetch_sets_by_words(keywords,like=False):
	"""
	关键词匹配
	:param keywords:
	:return:
	"""
	try:
		if isinstance(keywords,list):
			keywords = ','.join(keywords)
		data = []
		if keywords.strip() == '':
			return data
		if like:
			data = Question_auto.query.filter(Question_auto.words.like(keywords + "%")).limit(10)
		else:
			data = Question_auto.query.filter_by(words=keywords).limit(10)
		# print(keywords,data)
	except Exception as error:
		Question_auto.roll_back()
		return str(error)
	else:
		return data

def test():
	mdoks.gensim_lsi_simi()

def update_keywords_for_question(num=100):
	data = Question_auto.query.filter_by(words='').limit(num)
	if data:
		model.nlp_jieba_model.load_userdic()
	while data:
		for i in range(data.count()):
			question = data[i].question
			question = mgaics.remove_special_tags(question)
			question = mgaics.remove_modal_particle(question)
			keywords = mdoks.siphon_keywords_and_sort(question)
			if isinstance(keywords,list):
				keywords_str = ','.join(keywords)
			else:
				keywords_str = keywords
			Question_auto.query.filter(Question_auto.id==data[i].id).update({Question_auto.words:keywords_str})
		# break
		db.session.commit()
		data = Question_auto.query.filter_by(words='').limit(num)
	return data
