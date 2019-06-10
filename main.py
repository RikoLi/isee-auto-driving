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
    
    # 装载模型&权重
    net = IconNet(model_path='./models/icon_net.h5')
    net.loadWeights('./models/icon_net_weights.h5')

    # 初始化通信
    comm = Comm(session_name='sess_label')

    # 初始化标识符
    is_predicted = False
    is_sent = False
    label = 'None'

    stream = cv.VideoCapture(0)
    cv.namedWindow('camera')
    while True:
        # 捕获流，检测目标ROI
        _, frame = stream.read()
        status, roi, anchor = detectCircles(frame)
        
        if status is not None:
            ix = anchor[0]
            iy = anchor[1]
            ex = anchor[2]
            ey = anchor[3]
            if status == 'captured':
                # 分类预测
                is_sent = False
                label = predict(net, roi, icon_key)
                is_predicted = True
                # 绘制ROI
                cv.rectangle(frame, (ix,iy), (ex,ey), (0,0,255), 2)
                cv.putText(frame, 'Captured: '+label, (ix,iy-5), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,255), 2)
            if status == 'locked':
                # 绘制ROI
                cv.rectangle(frame, (ix,iy), (ex,ey), (0,255,0), 2)
                cv.putText(frame, 'Locked: '+label, (ix,iy-5), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
                # 发送指令
                if not is_sent and is_predicted and label != 'None':
                    comm.send('car', label)
                    is_predicted = False
                    is_sent = True

        cv.imshow('camera', frame)
        key = cv.waitKey(10) & 0xFF
        if key == ord('q'):
            break
    cv.destroyAllWindows()
