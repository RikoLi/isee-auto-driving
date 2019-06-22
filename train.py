import numpy as np
import cv2.cv2 as cv
from model import *
from utils import *

def main():
    # Load data
    data_path = '../yolo3/model_data/final_labels.txt' # Change to your own path
    loader = DataLoader(data_path, load_split=1)
    imgs, Y = loader.get()

    # Preprocessing
    X = preprocess(imgs, new_size=(128,128), is_test=False)
    Y = np.array(Y)
    Y = np.reshape(Y, (-1,6))

    
    
    # Training, choose one training method
    # Train new model
    if True:
        net = IconNet()
        net.train(X, Y, batch_size=16, epoches=100)

    # Train old model
    if False:
        net = IconNet(model_path='./models/icon_net.h5') # Change to your own path
        net.loadWeights('./models/icon_net_weights.h5') # Change to your own path
        net.train(X, Y, batch_size=8, epoches=100)

if __name__ == '__main__':
    main()