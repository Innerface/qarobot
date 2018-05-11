# Author: YuYuE (1019303381@qq.com) 2018.01.25
import time
import requests
import json


def get(url, para, headers):
    try:
        r = requests.get(url, params=para, headers=headers)
        json_r = r.json()
        result = {'code': r.status_code, 'data': json_r}
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


def post(url, para, headers):
    try:
        r = requests.post(url, data=para, headers=headers)
        json_r = r.json()
        result = {'code': r.status_code, 'data': json_r}
    except BaseException as error:
        raise Exception("Exception:", error)
    else:
        return result


def post_json(url, para, headers):
    try:
        data = para
        data = json.dumps(data)  # python数据类型转化为json数据类型
        r = requests.post(url, data=data, headers=headers)
        json_r = r.json()
        result = {'code': r.status_code, 'data': json_r}
    except BaseException as error:
        raise Exception("Exception:", error)
    else:
        return result


def http_for_turing(info, loc, user_id):
    api_url = "http://www.tuling123.com/openapi/api"
    api_key = "c3909fb045dd41828a7c51930f9417da"
    param = {'key': api_key, 'info': info, 'loc': loc, 'userid': user_id}
    hearder = {}
    result = post_json(api_url, param, hearder)
    return result


def generate_turing_response(text, loc=False, user_id=False):
    try:
        if len(text) == 0:
            text = "hi"
        if loc == False:
            loc = 'None'
        if user_id == False:
            user_id = time.time()
        response = http_for_turing(text, loc, user_id)
        if response.get('code') != 200:
            raise Exception("Exception:", "api request error")
        else:
            data = response.get('data')
            if data.get('code') == 100000:
                result = data.get('text')
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


def generate_location_from_ip(ip):
    pass


if __name__ == "__main__":
    result = generate_turing_response('你觉得我聪明么', '深圳', 'YuYuE')
    print(result)
