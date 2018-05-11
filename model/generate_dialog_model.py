# Author: YuYuE (1019303381@qq.com) 2018.03.16
import hashlib

def is_dialog_set(inp):
	return inp


def recover_dialog_model(inp):
	return inp


def record_dialog_model(inp):
	return inp


def update_dialog_model(inp, dia):
	return inp


def compose_response(inp, cache_id):
	return inp


def transfer_response(inp, response, dia):
	hl = hashlib.md5()
	hl.update(response.encode(encoding='utf-8'))
	md5_ = hl.hexdigest()
	result = {
		"code": 200,
		"data": response,
		"cache": md5_,
		"error": ""
	}
	return result
