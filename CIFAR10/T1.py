import matlab.engine
import scipy.io as scio
import cv2
import math
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import xlwt
import matplotlib.image as mpimg
from  openpyxl import  Workbook
import os
import time


def save(data,path):
    wb = Workbook()
    ws = wb.active
    [h, l] = data.shape
    for i in range(h):
        row = []
        for j in range(l):
            row.append(data[i,j])
        ws.append(row)
    wb.save(path)
# Calculate the gradient matrix and the Hessian matrix
def gradient(ckpt_file_path):

    detection_graph=tf.Graph()
    with tf.Session(graph=detection_graph) as sess:
        saver = tf.train.import_meta_graph(ckpt_file_path)
        saver.restore(sess, "../model/normal_cifar/normal_Cifar-19900")
        graph = tf.get_default_graph()
        x_input = graph.get_tensor_by_name('x:0')
        y_input = graph.get_tensor_by_name('y:0')
        keep_prob = graph.get_tensor_by_name('keep_prob:0')
        logits = graph.get_tensor_by_name('logits:0')
        max_index = tf.argmax(logits[0])
        gradient_op = tf.gradients(logits[0][max_index], x_input)
        hess_2 = tf.hessians(logits[0][max_index], x_input)
        gradient = sess.run(gradient_op, {x_input: xx[j], y_input: y, keep_prob: 1})
        hess_2 = sess.run(hess_2, {x_input: xx[j], y_input: y, keep_prob: 1})
        gradient = np.array(gradient)
        gradient = gradient.reshape(1, 3072)
        hess_2 = np.array(hess_2)
        hess_2 = hess_2.reshape(3072, 3072)
        save( gradient,"(1).xlsx")
        save(hess_2, "(2).xlsx")
# result judging
def restore_model_ckpt(ckpt_file_path):

    saver = tf.train.import_meta_graph(ckpt_file_path)
    saver.restore(sess, "../model/normal_Cifar-19900")
    graph = tf.get_default_graph()
    x_input = graph.get_tensor_by_name('x:0')
    y_input = graph.get_tensor_by_name('y:0')
    logits = graph.get_tensor_by_name('logits:0')
    keep_prob = graph.get_tensor_by_name('keep_prob:0')
    y_prediction = tf.argmax(logits, 1)
    b = sess.run(y_prediction, {x_input: x_adv, y_input: y,keep_prob:1})
    return b
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "2"
gpu_options=tf.GPUOptions(allow_growth=True)
sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))

xx = np.load("x.npy")
x_origin = xx[j]
y = np.load("y.npy")
y=y.reshape(1,10)
gradient('../model/normal_Cifar-19900.meta')

origin = np.argmax(y)
adv_example = origin
# p is the constraint
p=2.5


with open("L2.txt", "w") as f:
    f.write(str(p))
p = np.loadtxt("L2.txt")
while (origin==adv_example):
    eng = matlab.engine.start_matlab()
    eng.with_all(nargout=0)
    eng.quit()
    dataFile = 'x.mat'
    data = scio.loadmat(dataFile,verify_compressed_data_integrity=False)
    epsilon=data['x']
    x_adv=xx[j]+epsilon
    adv_example=restore_model_ckpt('../model/normal_Cifar-19900.meta')
    L2 = np.linalg.norm(epsilon)
    p = p + 0.5
    with open("L2.txt", "w") as f:
        f.write(str(p))
if (origin!=adv_example):
    np.save("adv.npy", x_adv)


