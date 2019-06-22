from utils import *
from model import *

if __name__ == '__main__':
    # 分类标签映射
    icon_key = {
        '0': '10',
        '1': '30',
        '2': '80',
        '3': 'left',
        '4': 'right',
        '5': 'stop'
    }

    # 流地址
    stream_addr = 'http://192.168.1.1:8080/?action=stream.mjpg'
    # stream_addr = 0
    comm_addr = 'http://192.168.1.1:2001'
    
    # 装载模型&权重
    net = IconNet(model_path='./models/6.14/icon_net.h5')
    net.loadWeights('./models/6.14/icon_net_weights.h5')

    # 初始化通信
    comm = Comm('session_0', comm_addr)

    # 初始化标识符
    is_predicted = False
    is_sent = False
    label = 'undefined'
    prob = ''

    stream = cv.VideoCapture(stream_addr)
    cv.namedWindow('camera')
    while True:
        # 捕获流，检测目标ROI
        _, frame = stream.read()
        # frame = cv.resize(frame, (640,480))
        status, roi, anchor = detectCircles(frame)
        cv.putText(frame, 'Current state: '+label, (0,20), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
        
        if status is not None:
            ix = anchor[0]
            iy = anchor[1]
            ex = anchor[2]
            ey = anchor[3]
            if status == 'captured':
                # 分类预测
                is_sent = False
                label, prob = predict(net, roi, icon_key)
                is_predicted = True
                # 绘制ROI
                cv.rectangle(frame, (ix,iy), (ex,ey), (0,0,255), 2)
                cv.putText(frame, 'Captured: '+label+' '+prob, (ix,iy-5), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,255), 2)
            if status == 'locked':
                # 绘制ROI
                cv.rectangle(frame, (ix,iy), (ex,ey), (0,255,0), 2)
                cv.putText(frame, 'Locked: '+label+' '+prob, (ix,iy-5), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
                # 发送指令
                if not is_sent and is_predicted and label != 'undefined':
                    comm.send(label)
                    is_predicted = False
                    is_sent = True

        cv.imshow('camera', frame)
        key = cv.waitKey(5) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            comm.send('30')
    stream.release()
    comm.close()
    cv.destroyAllWindows()
