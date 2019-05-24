# 光电实验大作业
2018-2019学年，ISEE光电信息综合实验期末大作业。

## 内容
基于路标识别的无人车自动驾驶。

## 平台
* 无人车（带有摄像头、无线通信模块）
* PC（用于图像实时处理）


## 实现
* Socket+OpenCV实时传输、显示视频流
* YOLOv3实现目标检测，参考[keras-yolov3](https://github.com/qqwweee/keras-yolo3)
* 目标检测、分类结果确定驾驶指令，Socket发送

## 文件说明
### 数据集制作
* get_raw_images.py 自动采集车载摄像头图像
* utils.py 一些小工具
* tracker.py 训练集ROI标注工具
