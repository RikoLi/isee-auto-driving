# -*- coding: utf-8 -*-
'''
实现Tracker类，基于随机粒子采样进行目标跟踪确定训练集的ROI。
by Riko
'''

import cv2.cv2 as cv
import numpy as np

class Tracker:
    def __init__(self, data_path):
        '''
        Tracker类\n
        data_path: string, 数据集文件夹目录
        '''
        self.data_path = data_path

    def track(self, distrib='uniform'):
        '''
        追踪函数，逐帧寻找目标ROI\n
        distrib: string, 粒子分布种类，默认均匀分布
        '''
        pass

    def drawROI(self):
        '''
        绘制第一帧的ROI位置\n
        '''
        pass