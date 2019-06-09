# -*- coding: utf-8 -*-
'''
辅助工具。
by Riko
'''
import glob
import os
import cv2.cv2 as cv
import numpy as np

# 检测圆形
def detectCircles(img):
    roi = img.copy()
    img = cv.bilateralFilter(img, 9, 75, 75) # Smoothing
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray = cv.medianBlur(gray, 5)
    gray = cv.equalizeHist(gray)
    circles = cv.HoughCircles(
        gray, cv.HOUGH_GRADIENT, 1, 20,
        param1=200, param2=100, minRadius=40, 
        maxRadius=150)

    if circles is not None:
        circles = np.int32(np.around(circles))
        rs = []
        for c in circles[0,:]:
            rs.append(c[2])
        max_id = rs.index(max(rs))
        for c in circles[0,:]:
            if rs[max_id] == c[2]:
                # cv.circle(img, (c[0],c[1]), c[2], (0,0,255), 2)
                # cv.circle(img, (c[0],c[1]), 2, (255,0,0), 2)
                # 矩形框选
                ix = c[0] - c[2] - 15
                iy = c[1] - c[2] - 15
                ex = c[0] + c[2] + 15
                ey = c[1] + c[2] + 15
                if c[2] > 60:
                    cv.rectangle(img, (ix,iy), (ex,ey), (0,255,0), 2)
                    cv.putText(img, 'Locked', (ix,iy-5), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
                    cv.imshow('camera', img)
                    return 'locked', roi[iy:ey+1, ix:ex+1]
                else:
                    cv.rectangle(img, (ix,iy), (ex,ey), (0,0,255), 2)
                    cv.putText(img, 'Captured', (ix,iy-5), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,255), 2)
                    cv.imshow('camera', img)
                    return 'captured', roi[iy:ey+1, ix:ex+1]
    else:
        cv.imshow('camera', img)
        return None, None

# 数据集批量重命名
def batchRename(class_name):
    files = glob.glob('new_'+class_name+'/*.jpg')
    l = len(glob.glob('class_'+class_name+'/*.jpg'))
    save_name = []
    cnt = 1
    for f in files:
        name = f.split('.')[0]
        save_name.append(name)
        os.rename(f, 'new_'+class_name+'/'+str(l+cnt)+'.jpg')
        cnt += 1

# 数据集批量大小调整
def batchResize(width, height, data_folder):
    imgs = glob.glob(data_folder+'/*.jpg')
    cnt = 1
    for img in imgs:
        pic = cv.imread(img)
        pic = cv.resize(pic, (width, height))
        cv.imwrite(img, pic)
        print(cnt, '/', len(imgs))
        cnt += 1

# 手动标注路标
def extractIcon(data_path, save_path, class_id):
    datas = glob.glob(data_path+'/*.jpg')
    num = len(datas)
    ix = 0
    iy = 0
    ex = 0
    ey = 0
    i = 0
    roi = None
    drawing = False
    is_next = False
    img = None
    def drawROI(event, x, y, flags, param):  # 鼠标监听回调
        nonlocal ix, iy, ex, ey, drawing, is_next, roi, img # 向上一层嵌套外寻找变量
        if event == cv.EVENT_LBUTTONDOWN:
            drawing = True
            is_next = False
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
            is_next = True
            new_img = img.copy()
            show_img = img.copy()
            roi = new_img[iy:ey+1, ix:ex+1]
            cv.rectangle(show_img, (ix,iy), (ex,ey), (0,0,255), 2)
            cv.imshow('window', show_img)

    cv.namedWindow('window')
    cv.setMouseCallback('window', drawROI)
    while True:
        img = cv.imread(datas[i])
        cv.imshow('window', img)
        
        if i+1 > num:
            print('---Labeling finished!---')
            break
        key = cv.waitKey(0) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s') and is_next:
            is_next = False
            # if not os.path.exists(save_path):
            #     os.mkdir(save_path)
            # cv.imwrite(save_path+'/'+str(i+1)+'.jpg', roi)
            print('Image', str(i+1), '/', str(num), 'is done! x:%d, y:%d, w:%d, h:%d' % (ix, iy, ex-ix, ey-iy))
            with open('new_labels.txt', 'a') as f:
                f.write(data_path+'/'+str(i+1)+'.jpg '+str(ix)+','+str(iy)+','+str(ex)+','+str(ey)+','+class_id+'\n')
        i += 1

class DataLoader:
    def __init__(self, label_txt_path):
        self.label_txt_path = label_txt_path
        self.path = None
        self.labels = None
        self.rois = None
        self._load()

    def _load(self):
        with open(self.label_txt_path, 'r') as f:
            files = f.readlines()
        paths = []
        labels = []
        rois = []
        for f in files:
            paths.append(f.split(' ')[0])
            tmp = f.split(' ')[1]
            labels.append(tmp.split(',')[4])
            rois.append(tmp.split(',')[:4])
        self.paths = paths
        self.labels = labels
        self.rois = rois

    def get(self, get_split=1):
        imgs = []
        cnt = 0
        for i in range(int(get_split*len(self.paths))):
            img = cv.imread(self.paths[i], 1)
            roi = img[int(self.rois[i][1]):int(self.rois[i][3])+1, int(self.rois[i][0]):int(self.rois[i][2])+1]
            imgs.append(roi)
            cnt += 1
            print('Load images: {}/{}'.format(cnt, int(get_split*len(self.paths))))
        return imgs, self.labels

if __name__ == '__main__':
    # batchResize(640, 480, 'class_stop')
    # batchRename('stop')
    class_dict = {
        '10': '0',
        '30': '1',
        '80': '2',
        'left': '3',
        'right': '4',
        'stop': '5'
    }
    data_path = './6.8_stop'     # 原始采集样本文件夹
    save_path = './'  # 提取icon后保存的文件夹
    class_id = class_dict['stop']  # 修改成要保存的类别key
    extractIcon(data_path, save_path, class_id)