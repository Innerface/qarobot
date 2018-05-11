import re


class Node(object):
    def __init__(self):
        self.children = None
        self.badword = None
        # self.isEnd = None


def add_word(root_node, word):
    node = root_node
    for i in range(len(word)):
        if node.children is None:
            node.children = {word[i]: Node()}
        elif word[i] not in node.children:
            node.children[word[i]] = Node()
        node = node.children[word[i]]
    node.badword = word
    # node.isEnd = 1


# 初始化节点
def init():
    root_node = Node()
    # result = u"卧槽\n尼玛\n"
    '''#-------------------------------------------
    #从数据库中读取
    db = DBUtils.DBUtils('localhost','root','4521','test')
    db.set_table("base_badwords")
    result = db.select(['words'])
    for line in result:
       #只匹配中文/英文/数字
      #li = ''.join(re.findall(re.compile(u'[a-zA-Z0-9\u4e00-\u9fa5]'),line[0]))
       #if li:
       #    add_word(root,li.lower())
       add_word(root,line[0].lower())
    return root
    '''
    # 从文件中读取
    with open('sensitiveword.txt', 'r', encoding='gbk') as result:
        for line in result:
            # 只匹配中文/英文/数字
            # li = ''.join(re.findall(re.compile(u'[a-zA-Z0-9\u4e00-\u9fa5]'),line.strip().decode('utf8')))
            # if li:
            #    print li
            #    add_word(root,li.lower())
            if line.strip():
                if not re.match('.*：', line):
                    add_word(root_node, line.strip().lower())
    return root_node


def is_contain(message, root_node):
    for i in range(len(message)):
        p = root_node
        j = i
        while j < len(message) and p.children is not None and message[j] in p.children:
            p = p.children[message[j]]
            j = j + 1
        if p.badword == message[i:j]:
            # print '--word--',p.badword,'-->',message
            yield p.badword
            # if p.isEnd:
            # return message[i:j]
    return 0


if __name__ == '__main__':
    root = init()
    s = '当官靠后台高潮，是依法成立的经营货币信贷业务的金融机构，太子党红色贵族银行'
    results = is_contain(s, root)
    for r in results:
        print(r)
