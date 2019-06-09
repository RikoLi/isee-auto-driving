import numpy as np
from model import *
from utils import DataLoader

# Load data
data_path = './new_labels.txt'
loader = DataLoader(data_path)
imgs, labels = loader.get()

# Preprocessing
pass

# Train new model
if False:
    net = IconNet()
    net.buildNewModel()
    # net.train(X, Y)