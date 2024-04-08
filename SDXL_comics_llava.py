#导入的python模块
import json
import os
import time
import random

import gradio as gr
import numpy as np  #NumPy 是 Python 中用于科学计算用于数组操作的各种函数和工具集成 C/C++ 和 Fortran 代码的工具。
import requests

#导入Python中用来导入PIL库,提供图像处理，调整大小 打开 保存 旋转 合并等
from PIL import Image

#定义变量
URL = "http://127.0.0.1:8188/prompt"
INPUT_DIR = "D:\\AI\\ComfyUI_windows_portable\\ComfyUI\\input"
OUTPUT_DIR = "D:\\AI\\ComfyUI_windows_portable\\ComfyUI\\output"


#定义获取最新图像的逻辑方法，用于之后下面函数的调用
def get_latest_image(folder):
    files = os.listdir(folder)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
    latest_image = os.path.join(folder, image_files[-1]) if image_files else None
    return latest_image

#开始获取请求进行编码
def start_queue(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    requests.post(URL, data=data)

#开始生成图像，前端UI定义所需变量传递给json
def generate_image(input_image,prompt_text_positive,prompt_text_negative):
    with open("SDXL_comics_llava.json","r", encoding="utf-8") as file_json:
        prompt = json.load(file_json)


        prompt["64"]["inputs"]["seed"] = random.randint(1, 1500000000000000) #定义种子随机数1到1500000，json的参数传递给comfyUI
        prompt["74"]["inputs"]["seed"] = random.randint(1, 1500000000000000)
        prompt["76"]["inputs"]["text_positive"] = f"digital artwork of a {prompt_text_positive}"
        prompt["76"]["inputs"]["text_negative"] = f"digital artwork of a {prompt_text_negative}"


    

    image = Image.fromarray(input_image) ## 假设 input_image 是一个 NumPy 数组，表示图像的像素数据,将 NumPy 数组转换为 PIL 中的图像对象 image
    min_side = min(image.size)  #找到了图像的宽度和高度中的最小值，并将其存储在 min_side 变量中
    scale_factor = 512 / min_side #计算缩放比例，使图像最小边缩放到512像素，如果图像的最小边本身大于512，则不做任何缩放
    new_size = (round(image.size[0] * scale_factor), round(image.size[1] * scale_factor))
    resized_image = image.resize(new_size) #调整原始图像 resized_image 就是缩放后的新图像对象

    resized_image.save(os.path.join(INPUT_DIR, "test_api.jpg")) #调整图像后保存到指定的INPUT_DIR变量路径

    previous_image = get_latest_image(OUTPUT_DIR)  # 推理出的最新输出图像保存到指定的OUTPUT_DIR变量路径


    start_queue(prompt)

    #这是一个循环获取指定路径的最新图像，休眠·一秒钟后继续循环
    while True:
            latest_image = get_latest_image(OUTPUT_DIR)
            if latest_image != previous_image:
                return latest_image
            
            time.sleep(1)

demo = gr.Interface(fn=generate_image, inputs=["image","text","text"], outputs=["image"])

demo.launch(share=True)#创建URL公共链接，使用的是huggingface空间
