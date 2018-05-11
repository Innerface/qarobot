# Author: YuYuE (1019303381@qq.com) 2018.02.01
from Pinyin2Hanzi import DefaultHmmParams
from Pinyin2Hanzi import viterbi
from Pinyin2Hanzi import DefaultDagParams
from Pinyin2Hanzi import dag
from pypinyin import pinyin, lazy_pinyin, Style
from Pinyin2Hanzi import all_pinyin
from Pinyin2Hanzi import simplify_pinyin
from Pinyin2Hanzi import is_pinyin

# 初始化
hmmparams = DefaultHmmParams()
dagparams = DefaultDagParams()


# 根据拼音转汉字 HMM模式 sets = ['ni', 'zhi', 'bu', 'zhi', 'dao']
def transfer_pinyin_to_hanzi_by_hmm(sets):
    try:
        result = viterbi(hmm_params=hmmparams, observations=sets, path_num=1, log=True)
        path = ''
        for item in result:
            path = item.path
    except Exception as error:
        raise Exception('error:', error)
    else:
        return path


# 根据拼音转汉字 DAG模式 sets = ['ni', 'zhi', 'bu', 'zhi', 'dao']
def transfer_pinyin_to_hanzi_by_dag(sets):
    try:
        result = dag(dagparams, sets, path_num=1, log=True)
        path = ''
        for item in result:
            path = item.path
    except Exception as error:
        raise Exception('error:', error)
    else:
        return path


# 列举所有规范拼音
def show_all_standard_pinyin_list():
    return all_pinyin()


# 拼音规范化
def pinyin_standardization(param):
    if not pinyin_decide(param):
        param = simplify_pinyin(param)
    return param


# 判断拼音是否规范
def pinyin_decide(param):
    return is_pinyin(param)


# 中文转拼音 model=lazy 不考虑多音字，style拼音风格，默认为首字母
def transfer_hanzi_to_pinyin(param, model='lazy', style=Style.FIRST_LETTER):
    try:
        if param.strip() == '':
            raise Exception('invalid param')
        if model == 'lazy':
            result = lazy_pinyin(param)
        else:
            result = pinyin(param, style=style)
    except Exception as error:
        raise Exception('error:', error)
    else:
        return result


# 判断一个unicode是否是汉字
def is_chinese(uchar):
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return True
    else:
        return False


# 判断一个unicode是否是英文字母
def is_alphabet(uchar):
    if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
        return True
    else:
        return False


# 判断一个unicode是否是数字
def is_number(uchar):
    if u'\u0030' <= uchar <= u'\u0039':
        return True
    else:
        return False


# 判断是否非汉字，数字和英文字符
def is_other(uchar):
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False


# 别字拼音纠正法
def correct_hanzi_by_pinyin_transfer(param, model='dag'):
    try:
        if param.strip() == '':
            raise Exception('invalid param')
        # if re.match(r"[\u4e00-\u9fa5]+",param) == "None":
        if is_alphabet(param):
            return param
        else:
            pinyin = transfer_hanzi_to_pinyin(param)
            if model == 'dag':
                result = transfer_pinyin_to_hanzi_by_dag(pinyin)
            else:
                result = transfer_pinyin_to_hanzi_by_hmm(pinyin)
    except Exception as error:
        raise Exception('error:', error)
    else:
        return result


# 单声母表
def gengerate_single_shengmu_list():
    list_ = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'r', 'z', 'c', 's', 'y', 'w']
    return list_


# 双拼声母表
def gengerate_double_shengmu_list():
    list_ = ['zh', 'ch', 'sh']
    return list_


# 独立韵母
def generate_single_yunmu():
    return ['a', 'o', 'e', 'an', 'en', 'ang', 'ai', 'ei', 'ou']


# 韵母表
def gengerate_yunmu_list():
    return ['a', 'o', 'e', 'ai', 'ei', 'ao', 'ou', 'an', 'en', 'ang', 'eng', 'ong', 'i', 'u', 'v', 'ua', 'uo', 'ia',
            'ie', 'in', 'iang', 'ing', 'iong', 've', 'uai', 'ui', 'iao', 'iu', 'ian', 'uan', 'uang', 'ueng', 'un']


# 全拼切分
def transfer_continue_pinyin_to_hanzi(param, model='dag'):
    try:
        if param.strip() == '':
            raise Exception('invalid param')
        if is_chinese(param):
            return param
        else:
            pinyin = continue_pinyin_split(param)
            # print(pinyin)
            if model == 'dag':
                result = transfer_pinyin_to_hanzi_by_dag(pinyin)
            else:
                result = transfer_pinyin_to_hanzi_by_hmm(pinyin)
    except Exception as error:
        raise Exception('error:', error)
    else:
        return result


def continue_pinyin_split(param):
    # for i in range(len(param)):
    """拼音切分"""
    temp = []
    shengm_ = shengmu_split(param)
    single_ = single_yunmu_split(param)
    if shengm_ and len(single_) == 0:
        temp = shengm_
    elif single_:
        temp.append(single_)
        temp.extend(shengm_)
    return temp


def shengmu_split(param):
    """声母剥离"""
    result = []
    shengmu_list = gengerate_single_shengmu_list()
    double_shengmu_list = gengerate_double_shengmu_list()
    yunmu_list = gengerate_yunmu_list()
    count = 0
    for unit in param:
        count += 1
        if unit in shengmu_list and param[count - 1:count + 1] not in double_shengmu_list:
            for i in [4, 3, 2, 1]:
                # 截取i位字符
                temp = param[count:count + i]
                if temp in yunmu_list:
                    result.append(param[count - 1:count + i])
                    # result = param[count - 1:count + i]
                    break
        elif param[count - 1:count + 1] in double_shengmu_list:
            for i in [4, 3, 2, 1]:
                # 截取i位字符
                temp = param[count + 1:count + 1 + i]
                if temp in yunmu_list:
                    result.append(param[count - 1:count + 1 + i])
                    # result = param[count - 1:count + i]
                    count += i
                    break
    return result


def double_shengmu_dection(param):
    double_shengmu_list = gengerate_double_shengmu_list()
    result = False
    for shengmu_ in double_shengmu_list:
        if shengmu_ in param:
            result = True
            break
    return result


def single_yunmu_split(param):
    """独立韵母剥离"""
    result = []
    yunmu_list = gengerate_yunmu_list()
    for i in [3, 2, 1]:
        # 截取i位字符
        temp = param[0:i]
        if temp in yunmu_list and len(temp) > 0:
            # result.append(param[0:i])
            result = param[0:i]
            break
    return result


if __name__ == '__main__':
    param = '旅行'
    pinyin = transfer_hanzi_to_pinyin(param)
    print(pinyin)
    hmm_ = transfer_pinyin_to_hanzi_by_hmm(pinyin)
    print(hmm_)
    dag_ = transfer_pinyin_to_hanzi_by_dag(pinyin)
    print(dag_)
    param = '新用卡'
    result = correct_hanzi_by_pinyin_transfer(param)
    print(result)
    pinyin = 'xinyongkabanli'
    result = transfer_continue_pinyin_to_hanzi(pinyin)
    print(''.join(result))
    pinyin = 'guozhai'
    result = transfer_continue_pinyin_to_hanzi(pinyin)
    print(result)
