# -*- coding: utf-8 -*-
'''
辅助工具。
by Riko
'''
import glob
import random
import os
import cv2.cv2 as cv
import numpy as np
import socket, struct, time

# 检测圆形
# Default parameters p1 = 200, p2 = 90, min = 10
def detectCircles(img, param1=200, param2=90, minRadius=10, maxRadius=130, bias=15):
    roi = img.copy()
    img = cv.bilateralFilter(img, 9, 75, 75) # Smoothing
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # gray = cv.medianBlur(gray, 5)
    # gray = cv.equalizeHist(gray)
    circles = cv.HoughCircles(
        gray, cv.HOUGH_GRADIENT, 1, 20,
        param1=param1, param2=param2, minRadius=minRadius, 
        maxRadius=maxRadius)

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
                ix = c[0] - c[2] - bias
                iy = c[1] - c[2] - bias
                ex = c[0] + c[2] + bias
                ey = c[1] + c[2] + bias
                if ix == -bias and iy == -bias and ex == bias and ey == bias:
                    return None, None, None
                if c[2] > 30: # > 90
                    return 'locked', roi[iy:ey+1, ix:ex+1], [ix, iy, ex, ey]
                else:
                    return 'captured', roi[iy:ey+1, ix:ex+1], [ix, iy, ex, ey]
    else:
        cv.imshow('camera', img)
        return None, None, None

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

# 路标标注
def extractIcon(data_path, save_name, class_id, auto=False):
    datas = glob.glob(data_path+'/*.jpg')
    num = len(datas)
    if not auto:
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
                with open(save_name, 'a') as f:
                    f.write(datas[i]+' '+str(ix)+','+str(iy)+','+str(ex)+','+str(ey)+','+class_id+'\n')
            i += 1
    else:
        for i in range(num):
            img = cv.imread(datas[i])
            status, roi, anchor = detectCircles(img, minRadius=0, bias=15)
            if status == None:
                print('No circles found')
                continue
            try:
                cv.imshow('roi', roi)
                with open(save_name, 'a') as f:
                    f.write(datas[i]+' '+str(anchor[0])+','+str(anchor[1])+','+str(anchor[2])+','+str(anchor[3])+','+class_id+'\n')
                print('Process: {}/{}'.format(i, num))
            except:
                continue
            # 手动控制
            # k = cv.waitKey()
            # if k == ord('n'):
            #     cv.destroyWindow('roi')
            #     continue


# 图像预处理
def preprocess(imgs, new_size=(128,128), is_test=False):
    '''
    图像预处理，减去均值，调整大小，随机旋转。
    '''
    X = []
    for img in imgs:
        # Resize
        tmp = cv.resize(img, new_size)
        # Normalization
        tmp = tmp - np.mean(tmp)
        #tmp = (tmp / 255.0 + 1.0) * 0.5
        if not is_test:
            # Random rotation
            times = np.random.randint(0, 4)
            tmp = np.rot90(tmp, times)
        X.append(tmp)
    X = np.array(X)
    return X


# 推理预测
def predict(net, img, icon_key):
    imgs = [img]
    norm_y = []
    prob = 0
    try:
        X = preprocess(imgs, new_size=(128,128), is_test=True)
        Y = net.model.predict(X)
        y = Y.tolist()[0]
        for each in y:
            norm_y.append(round(each / sum(y), 3))
        max_id = y.index(max(norm_y))
        prob = norm_y[max_id]
        return icon_key[str(max_id)], str(prob)
    except:
        return 'None', str(prob)





# 数据读取类
class DataLoader:
    def __init__(self, label_txt_path, load_split=1):
        self.label_txt_path = label_txt_path
        self.paths = None
        self.labels = None
        self.rois = None
        self._load(load_split)

    def _load(self, load_split):
        with open(self.label_txt_path, 'r') as f:
            files = f.readlines()
        random.shuffle(files)
        read_size = int(len(files) * load_split)
        cnt = 0
        paths = []
        labels = []
        rois = []
        for f in files:
            paths.append(f.split(' ')[0])
            tmp = f.split(' ')[1]
            labels.append(tmp.split(',')[4].replace('\n', ''))
            rois.append(tmp.split(',')[:4])
            cnt += 1
            if cnt == read_size:
                break
        one_hots = []
        for l in labels:
            t = np.zeros((1,6))
            t[0, int(l)] = 1
            one_hots.append(t)
        self.paths = paths
        self.labels = one_hots
        self.rois = rois

    def get(self):
        imgs = []
        cnt = 0
        for i in range(len(self.paths)):
            img = cv.imread(self.paths[i].replace('./', '../'))
            ix = int(self.rois[i][0])
            ex = int(self.rois[i][2])
            iy = int(self.rois[i][1])
            ey = int(self.rois[i][3])
            roi = img[iy:ey+1, ix:ex+1, :]
            imgs.append(roi)
            cnt += 1
            print('Load images: {}/{}'.format(cnt, len(self.paths)))
        return imgs, self.labels

# 通信类
class Comm:
    def __init__(self, session_name, addr):
        self.session_name = session_name
        self.addr = addr
        self.sock = None
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.sock.connect((self.addr.split(':')[1].replace('//',''), int(self.addr.split(':')[2])))
            print('与{}的通信[{}]已建立！'.format(self.addr, self.session_name))
        except Exception as e:
            print(e)

    def _packAndSend(self, command):
        flag = False
        
        speed_buff = command[0].split(',')
        speed_left = command[1].split(',')
        speed_right = command[2].split(',')

        send_buff = struct.pack('5B', int(speed_buff[0],16), int(speed_buff[1],16), int(speed_buff[2],16), int(speed_buff[3],16), int(speed_buff[4],16))
        send_left = struct.pack('5B', int(speed_left[0],16), int(speed_left[1],16), int(speed_left[2],16), int(speed_left[3],16), int(speed_left[4],16))
        send_right = struct.pack('5B', int(speed_right[0],16), int(speed_right[1],16), int(speed_right[2],16), int(speed_right[3],16), int(speed_right[4],16))

        try:
            self.sock.send(send_buff)
            self.sock.send(send_left)
            self.sock.send(send_right)
            flag = True
            # print(send_buff, send_left, send_right)
            return flag
        except Exception as e:
            print('Socket error!', e)
            return flag

    def send(self, msg):
        flag = False
        if msg == '10':
            flag = self._packAndSend(('ff,00,01,00,ff', 'ff,02,01,37,ff', 'ff,02,02,37,ff'))
        elif msg == '30':
            flag = self._packAndSend(('ff,00,01,00,ff', 'ff,02,01,40,ff', 'ff,02,02,42,ff'))
        elif msg == '80':
            flag = self._packAndSend(('ff,00,01,00,ff', 'ff,02,01,50,ff', 'ff,02,02,56,ff'))
        elif msg == 'right':
            flag = self._packAndSend(('ff,00,04,00,ff', 'ff,02,01,00,ff', 'ff,02,02,35,ff'))
            time.sleep(2)
            flag = self._packAndSend(('ff,00,01,00,ff', 'ff,02,01,37,ff', 'ff,02,02,35,ff'))
        elif msg == 'left':
            flag = self._packAndSend(('ff,00,03,00,ff', 'ff,02,01,37,ff', 'ff,02,02,00,ff'))
            time.sleep(2)
            flag = self._packAndSend(('ff,00,01,00,ff', 'ff,02,01,37,ff', 'ff,02,02,35,ff'))
        elif msg == 'stop':
            flag = self._packAndSend(('ff,00,00,00,ff', 'ff,02,01,1d,ff', 'ff,02,01,1d,ff'))

        if flag:
            print('Session: {}, To: {}, Msg: {}'.format(self.session_name, self.addr, msg))

    def close(self):
        self._packAndSend(('ff,00,00,00,ff', 'ff,02,01,1d,ff', 'ff,02,01,1d,ff'))
        self.sock.close()

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
    save_name = 'final_labels.txt'  # 索引txt文件
    class_id = class_dict['stop']  # 修改成要保存的类别key
    extractIcon(data_path, save_name, class_id, auto=True)
