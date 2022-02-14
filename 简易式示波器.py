#!/usr/bin/python3

from pyfirmata2 import Arduino
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

'''
简易式示波器.py

修改自 pyFirmata2 的示例程序 realtime_scope.py

原作者 Bernd Porr <mail@bernporr.me.uk>
修改者 Ruoheng Qu <ruoheng.qu@noldus.com>

注释翻译 + 横纵坐标轴对应现实电压及时间


图片左侧纵轴大致对应电压，下方横轴对应经过时间

默认试用A0口
注意，A0口应配有上拉或下拉电阻，以正确显示高低电平！
'''

# 原程序说明

# 默认采样率为100Hz的实时示波器，最高可至1000Hz
# 默认绘制 Analog 0 的电压
# 可以通过实例化更多的 RealtimePlotWindow 实例来绘制多个通道，并注册其他通道的 Callback。

# Copyright (c) 2018-2020, Bernd Porr <mail@berndporr.me.uk>
# see LICENSE file.

# 如此处不能正确嗅探到COM口，请反注释掉函数之后的 board = Arduino('COM5')
# 并根据IDE进行相应修改
PORT = Arduino.AUTODETECT
# Linux可在此处手动指定
# PORT = '/dev/ttyUSB0'

# 滚动显示数据
class RealtimePlotWindow:

    def __init__(self):
        # 创建图形绘制窗口
        self.fig, self.ax = plt.subplots()
        # 创建绘图区
        self.plotbuffer = np.zeros(500)
        # 创建线条
        self.line, = self.ax.plot(self.plotbuffer)
        # 坐标轴
        self.ax.set_ylim(0, 1.5)
        # Arduino 默认返回 5v 为 1，按照比例修改纵坐标轴标签
        self.ax.set_yticks([0, 0.2, 0.4, 0.6, 0.66, 0.8, 1, 1.2, 1.4])
        self.ax.set_yticklabels(['0', '1', '2', '3', '3.3', '4', '5', '6', '7'])
        self.ax.set_ylabel('Voltage (V)')
        # 调整 x 轴坐标，符合实际含义
        self.ax.set_xticks([0, 100, 200, 300, 400, 500])
        self.ax.set_xticklabels(['-5', '-4', '-3', '-2', '-1', '0'])
        self.ax.set_xlabel('Time (s)')
        # 创建环形缓冲区，用于积累样本
        # 每当下面的绘图窗口出现时，它都会被清空
        # 进行重绘时都会清空
        self.ringbuffer = []
        # 在这里添加任何初始化代码（过滤器等）
        # 开始动画
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=100)

    # 刷新图像
    def update(self, data):
        # 向绘图区添加新数据
        self.plotbuffer = np.append(self.plotbuffer, self.ringbuffer)
        # 只保留最新的500个数据，清除旧的数据
        self.plotbuffer = self.plotbuffer[-500:]
        self.ringbuffer = []
        # 设置新的500个点
        self.line.set_ydata(self.plotbuffer)
        return self.line,

    # 将数据追加到环形缓冲区
    def addData(self, v):
        self.ringbuffer.append(v)


# 创建一个动画滚动窗口的实例
# 要绘制更多的通道，只需创建更多的实例，并在下面添加回调处理程序
realtimePlotWindow = RealtimePlotWindow()

# 调节此处的数值可修改采样率
# 默认采样率: 100Hz
samplingRate = 100
# samplingRate = 1000

# 调用每一个从Arduino来的新采样数据
def callBack(data):
    # 发送采样数据到绘图窗口
    # 在这里添加任何 filter 过滤数据:
    # data = self.myfilter.dofilter(data)
    realtimePlotWindow.addData(data)

# 检测 Arduino 板
# board = Arduino(PORT)
board = Arduino('COM5')

# 设置Arduino的采样率
board.samplingOn(1000 / samplingRate)

# 注册回调，将数据添加到动画图中
board.analog[0].register_callback(callBack)

# 启用回调
board.analog[0].enable_reporting()

# 显示图像并开始播放动画
plt.show()

# 需要调用以关闭串行端口
board.exit()

print("finished")
