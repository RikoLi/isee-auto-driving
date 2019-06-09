from utils import *
from model import *

if __name__ == '__main__':
    # model = IconNet()
    # model.loadWeights('./...')

    is_predicted = False

    steam = cv.VideoCapture(0)
    cv.namedWindow('camera')
    while True:
        _, frame = steam.read()
        status, roi, _ = detectCircles(frame)
        
        # if status is not None:
        #     # 分类预测
        #     label = model.predict(roi)
        # else:
        #     print('Detecting...')


        key = cv.waitKey(5) & 0xFF
        if key == ord('q'):
            break
    cv.destroyAllWindows()
