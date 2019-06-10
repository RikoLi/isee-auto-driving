import numpy as np
import keras
from keras.models import Model
from keras.layers import Conv2D, Dense, Input
from keras.layers import LeakyReLU
from keras.layers import MaxPool2D
from keras.layers import BatchNormalization, Dropout
from keras.layers import Flatten
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, TensorBoard

class IconNet:
    def __init__(self, model_path=None):
        self.model_path = model_path
        if self.model_path is not None:
            self.model = self._loadModel()
        else:
            self.model = self._buildNewModel()
    
    def _saveModel(self, save_path='./icon_net.h5'):
        self.model.save(save_path, include_optimizer=False)
    
    def _loadModel(self):
        return keras.models.load_model(self.model_path)

    def _buildNewModel(self):
        '''
        创建新的分类器模型。
        '''
        img_input = Input((128,128,3))
        y = convBlock(img_input, (3,3), 32, 1)
        y = LeakyReLU()(y)
        y = MaxPool2D()(y)
        y = Dropout(0.5)(y)

        y = convBlock(y, (3,3), 64, 1)
        y = LeakyReLU()(y)
        y = MaxPool2D()(y)
        y = Dropout(0.5)(y)

        y = convBlock(y, (3,3), 128, 1)
        y = LeakyReLU()(y)
        y = MaxPool2D()(y)
        y = Dropout(0.5)(y)

        y = convBlock(y, (3,3), 256, 1)
        y = LeakyReLU()(y)
        y = MaxPool2D()(y)
        y = Dropout(0.5)(y)

        y = convBlock(y, (3,3), 512, 1)
        y = LeakyReLU()(y)
        y = MaxPool2D()(y)
        
        y = Flatten()(y)
        y = Dense(4096)(y)
        y = LeakyReLU()(y)
        y = Dense(4096)(y)
        y = LeakyReLU()(y)
        y = Dense(6, activation='softmax')(y)

        return Model(inputs=img_input, outputs=y)

    def loadWeights(self, weight_path='./icon_net_weights.h5'):
        self.model.load_weights(weight_path)

    def train(self, X, Y, batch_size=16, epoches=500, save_interval=1, weight_save_path='./icon_net_weights.h5', log_path='./'):
        opt = Adam(0.00001)
        checkpt = ModelCheckpoint(weight_save_path, save_best_only=True, save_weights_only=True, period=save_interval)
        tb = None
        if log_path is not None:
            tb = TensorBoard(log_dir=log_path, batch_size=batch_size)

        self.model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
        if self.model_path is None:
            self._saveModel()
        self.model.fit(X, Y, batch_size=batch_size, epochs=epoches, callbacks=[checkpt, tb], validation_split=0.2)

    def predict(self, img_input):
        pass


def convBlock(x, kernel_size, channels, strides):
    y = Conv2D(channels, kernel_size, strides=strides, padding='same')(x)
    y = Conv2D(channels, kernel_size, strides=strides, padding='same')(y)
    y = Conv2D(channels, kernel_size, strides=strides, padding='same')(y)
    y = BatchNormalization()(y)
    return y
