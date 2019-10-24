[中文](../README.md)|[English](./EN_README.md)

# UGV Auto-Driving via Real-Time Traffic Sign Detection

2018-2019, Spring & Summer, final project of Comprehensive Experiment of Photoelectric Information & Artificial Intelligence.

## Content

UGV auto-driving via real-time traffic sign detection.

## Prerequisites

* Python 3.6.4
* Numpy 1.15.4
* Tensorflow 1.12.0
* Keras 2.2.4
* opencv-python 3.4.2.16

## Usage

Pre-trained model is not given here. If you are going to train your own model, edit training configs in `train.py` then run this:
```shell
python train.py
```

Infer with your own model on your device:
```shell
python main.py
```

## Platform

* UGV: communication module + control module + video-capture module
* PC: receive video stream + infer + send commands

## Approaches

Originally, a *YOLOv3* model is selected as the solution on our self-made dataset, applying detection and classification simultaneously. However, we do not have enough computing resource to afford this :(

An alternative solution is to extract ROIs of traffic signs via classical algorithms, and then pass the ROIs to a simple CNN for classification.

## Codes
### Dataset Preparation
* `get_raw_images.py` for capturing images on the UGV
* `utils.py` for some tools' definitions
    * resize
    * traffic sign detection
    * dataset rename
    * dataset labeling
    * dataloader

### Model
* `model.py` defines network structure
* `train.py` is training script

### Monitor
* `main.py` defines monitor UI on PC

Currently, detection, inference and result display run in one thread, which may lead to lags in the whole process because of the great time consumption in computation. 

### Communication

`Comm` class is implemented in `utils.py`, defining process of sending commands with Socket.

### Demo

Demo for real-time inference on PC:

![s1](../samples/sample1.png)
![s2](../samples/sample2.png)
![s3](../samples/sample3.png)