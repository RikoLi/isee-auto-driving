# -*- coding: utf-8 -*-
'''
辅助工具。
by Riko
'''
import glob
import os
import cv2.cv2 as cv

# 数据集批量重命名
def batch_rename(class_name):
    files = glob.glob('class_'+class_name+'_add/*.jpg')
    l = len(glob.glob('class_'+class_name+'/*.jpg'))
    save_name = []
    cnt = 1
    for f in files:
        name = f.split('.')[0]
        save_name.append(name)
        os.rename(f, 'class_'+class_name+'_add/'+str(l+cnt)+'.jpg')
        cnt += 1

# 数据集批量大小调整
def batch_resize(width, height, data_folder):
    imgs = glob.glob(data_folder+'/*.jpg')
    cnt = 1
    for img in imgs:
        pic = cv.imread(img)
        pic = cv.resize(pic, (width, height))
        cv.imwrite(img, pic)
        print(cnt, '/', len(imgs))
        cnt += 1

if __name__ == '__main__':
    batch_resize(640, 480, 'class_stop')