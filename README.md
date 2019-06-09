# 光电实验大作业
2018-2019学年，ISEE光电信息综合实验期末大作业。

## 内容
基于路标识别的无人车自动驾驶。

## 平台
* 无人车（带有摄像头、无线通信模块）
* PC（用于图像实时处理）


## 实现
计划Solution：
* Socket+OpenCV实时传输、显示视频流
* YOLOv3实现目标检测，参考[keras-yolov3](https://github.com/qqwweee/keras-yolo3)
* 目标检测、分类结果确定驾驶指令，Socket发送

备用Solution：
* ROI提取
* VGG风格的网络训练多分类器
* Socket发送指令

## 文件说明
### 数据集制作
* get_raw_images.py 自动/手动采集车载摄像头图像
* utils.py 一些小工具
    * 图片尺寸调整
    * 圆形目标检测
    * 数据集重命名
    * 数据集自动/手动标注
    * DataLoader数据读入工具
* model.py 定义了网络结构
* train.py 定义了训练脚本
* main.py 定义了PC端视频流监视界面
