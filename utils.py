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

# 手动标注路标
def extract_icon(data_path, save_path):
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
            if not os.path.exists(save_path):
                os.mkdir(save_path)
            cv.imwrite(save_path+'/'+str(i+1)+'.jpg', roi)
            print('Image', str(i+1), 'is done! x:%d, y:%d, w:%d, h:%d' % (ix, iy, ex-ix, ey-iy))
        i += 1

if __name__ == '__main__':
    # batch_resize(640, 480, 'class_stop')
    extract_icon('./class_10', 'class_10_icon')