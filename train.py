import numpy as np
import cv2.cv2 as cv
from model import *
from utils import DataLoader

# Load data
data_path = './final_labels.txt'
loader = DataLoader(data_path, load_split=0.01)
imgs, Y = loader.get()
# cv.namedWindow('d', cv.WINDOW_NORMAL)
# cv.imshow('d', imgs[8])
# cv.waitKey()
# cv.destroyAllWindows()

# Preprocessing
X = []
for img in imgs:
    tmp = cv.resize(img, (128,128))
    tmp = tmp - np.mean(tmp)
    tmp = (tmp / 255.0 + 1.0) * 0.5
    X.append(tmp)

# Train new model
if False:
    net = IconNet()
    net.train(X, Y, batch_size=8, epoches=100)

# Train old model
if False:
    net = IconNet(model_path='./icon_net.h5')
    net.loadWeights('./icon_net_weights.h5')
    net.train(X, Y, batch_size=8, epoches=100)