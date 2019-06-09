# -*- coding: utf-8 -*-
'''
实现Tracker类，基于随机粒子采样进行目标跟踪取得训练集中标识牌部分的图像。
by Riko
'''

import cv2.cv2 as cv
import numpy as np

class Rect:
    def __init__(self, x, y, w, h):
        '''
        Rect类。\n
        x: int, ROI左上角x坐标\n
        y: int, ROI左上角y坐标\n
        w: int, ROI宽度\n
        h: int, ROI高度
        '''
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def showRect(self, img):
        '''绘制ROI。\n
        img: ndarray, 待绘制的图像
        '''
        cv.rectangle(img, (self.x,self.y), (self.x+self.w,self.y+self.h), (0,0,255), 1)

class Particle:
    def __init__(self, x, y, radius):
        '''
        Particle类。\n
        x: 粒子x坐标\n
        y: 粒子y坐标\n
        radius: 粒子半径（显示用）
        '''
        self.x = x
        self.y = y
        self.radius = radius
    
    def createParticles(self, num, x_range, y_range):
        '''
        创建一组满足均匀分布的粒子。\n
        num: int，粒子数量\n
        x_range: tuple，水平分布范围\n
        y_range: tuple，垂直分布范围\n
        return: list，粒子数组
        '''
        particles = []
        for i in range(num):
            px = np.random.randint(x_range[0], x_range[1])
            py = np.random.randint(y_range[0], y_range[1])
            ptc = Particle(px, py, 5)
            particles.append(ptc)
        return particles

    def showParticle(self, img):
        '''
        绘制一个粒子对象。\n
        img: ndarray，待绘制的图像
        '''
        cv.circle(img, (self.x, self.y), self.radius, (0,255,0), -1)

class Tracker:
    def __init__(self, init_roi, img):
        '''
        Tracker类\n
        init_roi: Rect对象，指定了最开始的目标位置\n
        img: ndarray, 进行目标定位的图
        '''
        print('Initial ROI: (%d, %d, %d, %d)' % (init_roi.x, init_roi.y, init_roi.w, init_roi.h))
        self.init_roi = init_roi
        self.img = img
        init_ptc = Particle(self.init_roi.x, self.init_roi.y, 1)
        self.src_feature = self.extractFeature(init_ptc)

    
    def track(self):
        '''
        追踪函数，逐帧寻找目标ROI\n
        return：ROI的左上角坐标与ROI宽高
        '''
        weights = []
        init_ptc = Particle(1, 1, 1)    # 随便生成一个没用的粒子，用来生成后面的均匀分布粒子
        particles = init_ptc.createParticles(1000, (0,640-self.init_roi.w), (0,480-self.init_roi.h))  # 限定生成边界

        for ptc in particles:
            # 提取邻域特征
            new_feature = self.extractFeature(ptc)
            # 计算和选定目标的相似度/权重
            weight = self.computeWeight(self.src_feature, new_feature)
            weights.append(weight)

        # 找出最可能是目标点的粒子
        max_weight = max(weights)
        max_id = weights.index(max_weight)
        obj_ptc = particles[max_id]
        # obj_ptc.showParticle(self.img)

        return [obj_ptc.x, obj_ptc.y, self.init_roi.w, self.init_roi.h]

    def computeWeight(self, src_feature, new_feature):
        '''
        计算特征间cosine相似度/权重。\n
        src_feature: ndarray, 目标特征向量\n
        new_feature: ndarray, 粒子处ROI特征向量
        '''
        # new_f = np.mat(new_feature)
        # src_f = np.mat(src_feature)
        # inner_prd = float(new_f * src_f.T)
        # deno = np.linalg.norm(new_f, 2) * np.linalg.norm(src_f, 2)
        # return (inner_prd / deno + 1.0) * 0.5

        bf = cv.BFMatcher(cv.NORM_L2, crossCheck=True)
        matches = bf.match(src_feature[1], new_feature[1])
        return len(matches)


    def extractFeature(self, particle):
        '''
        抽取图像对应粒子位置处的特征\n
        particle: Particle对象\n
        return: ndarray, 特征向量
        '''
        x = particle.x
        y = particle.y
        w = self.init_roi.w
        h = self.init_roi.h
        # feature = self.img[y:h+y, x:w+x, :]
        # return feature.astype(np.float).reshape(1,-1) / 255.0

        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        sift = cv.xfeatures2d.SIFT_create()
        kp, des = sift.detectAndCompute(gray, None)
        return [kp, des]


if __name__ == '__main__':
    ix = -1
    iy = -1
    ex = -1
    ey = -1
    drawing = False
    init_roi = None
    def drawROI(event, x, y, flags, param):  # 鼠标监听回调
        global ix, iy, ex, ey, drawing, init_roi # 向上一层嵌套外寻找变量
        if event == cv.EVENT_LBUTTONDOWN:
            drawing = True
            print('Top-left corner at (%d, %d)' % (x, y))
            ix = x
            iy = y
        elif event == cv.EVENT_MOUSEMOVE:
            if drawing:
                ex = x
                ey = y
        elif event == cv.EVENT_LBUTTONUP:
            drawing = False
            print('Bottom-right corner at (%d, %d)' % (x, y))
            ex = x
            ey = y
            init_roi = Rect(ix, iy, ex-ix, ey-iy)

    img = cv.imread('./class_10/1.jpg')
    cv.namedWindow('test')
    cv.setMouseCallback('test', drawROI)
    cv.imshow('test', img)

    key = cv.waitKey(0)
    if key == ord('q'):
        cv.destroyAllWindows()
    elif key == ord('t'):
        img = cv.imread('./class_10/24.jpg')
        tracker = Tracker(init_roi, img)
        obj_pos = tracker.track()
        obj_box = Rect(obj_pos[0], obj_pos[1], obj_pos[2], obj_pos[3])
        obj_box.showRect(img)
        cv.namedWindow('object')
        cv.imshow('object', img)
        cv.waitKey()
        cv.destroyAllWindows()