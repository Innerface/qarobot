# Author: YuYuE (1019303381@qq.com) 2018.01.18
import tensorflow as tf
import numpy as np
import sys

# 样本数据
x = np.float32(np.random.rand(3, 100))
y_ = np.dot([[1.00, 2.00, 3.00], [3.00, 2.00, 3.00]], x) + 4.00
# w，b初始化
b = tf.Variable(tf.zeros([1]))
w = tf.Variable(tf.random_uniform([2, 3], -1, 1))
y = tf.matmul(w, x) + b
# 预测值与实际值的平均方差
loss = tf.reduce_mean(tf.square(y - y_))
# 优化器
optimizer = tf.train.GradientDescentOptimizer(0.5)
# 优化器策略,方差最小化
train = optimizer.minimize(loss)
# 初始化变量
init = tf.initialize_all_variables()
# 保存模型
saver = tf.train.Saver()
# 初始化会话
sess = tf.Session()
sess.run(init)


# 封装训练函数
def trainfunc():
    # 开始训练
    for step in range(0, 20001):
        sess.run(train)
        if step % 200 == 0:
            print(step, sess.run(w), sess.run(b), sess.run(loss))
    save_path = saver.save(sess, "./recongnize.ckpt")


def predictfunc():
    saver.restore(sess, "./recongnize.ckpt")
    result = sess.run([w, b])
    print(result)


if __name__ == "__main__":
    if sys.argv[1] == 'train':
        trainfunc()
    else:
        predictfunc()
