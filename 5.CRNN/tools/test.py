#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-9-29 下午3:56
# @Author  : Luo Yao
# @Site    : http://github.com/TJCVRS
# @File    : demo_shadownet.py
# @IDE: PyCharm Community Edition
"""
Use shadow net to recognize the scene text
"""
import tensorflow as tf
import os.path as ops
import numpy as np
import cv2
import argparse
import matplotlib.pyplot as plt
try:
    from cv2 import cv2
except ImportError:
    pass

from crnn_model import crnn_model
from global_configuration import config
from local_utils import log_utils, data_utils

logger = log_utils.init_logger()

import subprocess as sp

import json

def init_args():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--video_path', type=str, help='Where you store the image',
                        default='data/test_videos/sample1.mp4')
    parser.add_argument('--weights_path', type=str, help='Where you store the weights',
                        default='model/shadownet/shadownet_2017-10-17-11-47-46.ckpt-199999')

    return parser.parse_args()


def recognize(video_path, weights_path, is_vis=False):
# def recognize():
    """

    :param image_path:
    :param weights_path:
    :param is_vis:
    :return:
    """
    
    z=0

    command = [ "ffmpeg",
                '-loglevel', 'quiet',
                '-i', video_path,
                '-f','image2pipe',
                '-pix_fmt','rgb24',
                '-vcodec','rawvideo','-']
    pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

    cmnd = ['ffprobe', '-print_format', 'json', '-show_entries', 'stream=width,height', '-pretty', '-loglevel', 'quiet', video_path]
    p = sp.Popen(cmnd, stdout=sp.PIPE, stderr=sp.PIPE)

    out, err =  p.communicate()

    video_r = json.loads(out.decode('utf-8'))['streams'][0]
    video_h = video_r['height']
    video_w = video_r['width']


    for i in range (10):
        if z==0:
            raw_image = pipe.stdout.read(video_h*video_w*3)
            image = np.fromstring(raw_image, dtype='uint8')
            image = [image.reshape((video_h,video_w,3))]
            z+=1
        else:
            raw_image = pipe.stdout.read(video_h*video_w*3)
            cap = np.fromstring(raw_image, dtype='uint8')
            cap = cap.reshape((video_h,video_w,3))
            image = np.concatenate((image, [cap]),axis=0)
   
    pipe.stdout.flush()
    pipe.terminate()

    p.terminate()
    # image=image[0]
    inputdata = tf.placeholder(dtype=tf.float32, shape=[1, 10, video_h, video_w, 3], name='input')
    image = np.expand_dims(image, axis=0).astype(np.float32)
    
    
    # image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    # image = cv2.resize(image, (100, 32))    
    # image = np.expand_dims(image, axis=0).astype(np.float32)
    # inputdata = tf.placeholder(dtype=tf.float32, shape=[1, 32, 100, 3], name='input')
    # print(image.shape)


    net = crnn_model.ShadowNet(phase='Test', hidden_nums=256, layers_nums=2, seq_length=27, num_classes=37)

    with tf.variable_scope('shadow'):
        net_out = net.build_shadownet(inputdata=inputdata)

    decodes, _ = tf.nn.ctc_beam_search_decoder(inputs=net_out, sequence_length=27*np.ones(10), merge_repeated=False)

    decoder = data_utils.TextFeatureIO()
    '''
    # config tf session
    sess_config = tf.ConfigProto()
    sess_config.gpu_options.per_process_gpu_memory_fraction = config.cfg.TRAIN.GPU_MEMORY_FRACTION
    sess_config.gpu_options.allow_growth = config.cfg.TRAIN.TF_ALLOW_GROWTH

    # config tf saver
    saver = tf.train.Saver()

    sess = tf.Session(config=sess_config)

    with sess.as_default():

        saver.restore(sess=sess, save_path=weights_path)

        preds = sess.run(decodes, feed_dict={inputdata: image})

        #preds = decoder.writer.sparse_tensor_to_str(preds[0])

        #logger.info('Predict image {:s} label {:s}'.format(ops.split(image_path)[1], preds[0]))
        print(preds)
        if is_vis:
            plt.figure('CRNN Model Demo')
            plt.imshow(cv2.imread(image_path, cv2.IMREAD_COLOR)[:, :, (2, 1, 0)])
            plt.show()

        sess.close()

    return
    '''
if __name__ == '__main__':
    # Inti args
    
    args = init_args()
    if not ops.exists(args.video_path):
        raise ValueError('{:s} doesn\'t exist'.format(args.video_path))
    
    
    # recognize the image
    # recognize()
    recognize(video_path=args.video_path, weights_path=args.weights_path)
    
    

