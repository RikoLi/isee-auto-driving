from utils import *
from model import *

if __name__ == '__main__':
    # model = IconNet()
    # model.loadWeights('./...')

    is_predicted = False
    is_sent = False
    label = 'None'

    stream = cv.VideoCapture(0)
    cv.namedWindow('camera')
    while True:
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
                # label = model.predict(roi)
                label = 'LABEL'
                cv.rectangle(frame, (ix,iy), (ex,ey), (0,0,255), 2)
                cv.putText(frame, 'Captured: '+label, (ix,iy-5), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,255), 2)
                is_predicted = True
            if status == 'locked':
                cv.rectangle(frame, (ix,iy), (ex,ey), (0,255,0), 2)
                cv.putText(frame, 'Locked: '+label, (ix,iy-5), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
                # 发送指令
                if not is_sent and is_predicted:
                    # sendCommand()
                    print('send command...')
                    is_predicted = False
                    is_sent = True
        else:
            print('Detecting...')

        cv.imshow('camera', frame)
        key = cv.waitKey(5) & 0xFF
        if key == ord('q'):
            break
    cv.destroyAllWindows()
