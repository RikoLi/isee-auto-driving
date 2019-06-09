# -*- coding: utf-8 -*-

'''
从摄像头获取制作训练集的原始图像。
by Riko
'''

import cv2.cv2 as cv
import os

# 摄像机
class Camera:
    def __init__(self, video_stream=0):
        '''
        摄像机类Camera，生成Camera对象。\n
        Parameters:\n
        video_stream: string，视频流地址，默认值为0（本地摄像头）
        '''
        self.video_stream = video_stream

    # 图片逐帧获取
    def sample(self, step=1, save_dir='./video_frames/'):
        '''
        输出视频流，鼠标框选对象进行追踪，按c保存ROI内图像，按q退出。\n
        Parameters:\n
        step: int，保存间隔帧数\n
        save_dir: string，采集结果保存路径
        '''
        # 定位变量初始化
        ix = -1
        iy = -1
        ex = -1
        ey = -1
        drawing = False
        # 绘制ROI的鼠标事件回调函数
        def drawROI(event, x, y, flags, param):           
            nonlocal ix, iy, ex, ey, drawing # 向上一层嵌套外寻找变量
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

        # 获取流
        cap = cv.VideoCapture(self.video_stream)
        cnt = 1 # 采集结果计数
        cntt = 1    # 帧计数

        # 建立显示窗口
        cv.namedWindow('camera', cv.WINDOW_NORMAL)
        # 绑定鼠标事件
        cv.setMouseCallback('camera', drawROI)

        # 逐帧处理
        autoget_flg = False
        while True:
            ret, frame = cap.read()
            roi = frame.copy()

            # 绘制初始roi，用鼠标事件实现
            cv.rectangle(frame, (ix,iy), (ex,ey), (0,0,255), 2)
            roi = roi[iy:ey+1, ix:ex+1]

            # 显示当前帧
            cv.imshow('camera', frame)
            if autoget_flg and (cntt%step==0) and step != 0:
                # 保存图像
                cv.imwrite(save_dir+'/'+str(cnt)+'.jpg', frame)
                print('Image %d is saved!' % (cnt))
                cnt += 1
                cntt = 0
            key = cv.waitKey(1) & 0xFF

            # 控制
            if key == ord('c'): # 按c自动采集
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
                if not autoget_flg:
                    print('-------- Enable auto collecting ! --------')
                    autoget_flg = True
                else:
                    print('-------- Disable auto collecting ! --------')
                    autoget_flg = False
            elif key == ord('s'): # 单张采集
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
                # 保存图像
                cv.imwrite(save_dir+'/'+str(cnt)+'.jpg', frame)
                print('Image %d is saved!' % (cnt))
                cnt += 1
                cntt = 0
            elif key == ord('q'):   # 按q退出
                break

            cntt += 1
    
    pass



if __name__ == '__main__':
    cam = Camera(0)
    cam.sample(step=1, save_dir='6.8_stop')