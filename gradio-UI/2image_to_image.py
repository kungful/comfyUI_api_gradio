import json
import os
import time
import random
import requests
import gradio as gr
import numpy as np
from PIL import Image

# 定义常量
URL = "http://127.0.0.1:8188/prompt"  # 请求的 URL 地址
# 修正后的路径
INPUT_DIR = "C:\\Users\\hua\\Desktop\\comfyui310\\comfyUI\\ComfyUI\\input"
OUTPUT_DIR = "C:\\Users\\hua\\Desktop\\comfyui310\\comfyUI\\ComfyUI\\output"
AUDIO_PATH = "C:\\Users\\hua\\Desktop\\comfyui310\\comfyUI\\jie.wav"

# 定义一个函数，用于获取指定文件夹中最新的图像文件
def get_latest_image(folder):
    files = os.listdir(folder)  # 获取文件夹中的所有文件
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]  # 筛选出图像文件
    image_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))  # 按修改时间排序
    latest_image = os.path.join(folder, image_files[-1]) if image_files else None  # 获取最新的图像文件路径
    return latest_image

# 定义一个函数，用于启动队列并发送请求
def start_queue(prompt_workflow):
    p = {"prompt": prompt_workflow}  # 构建请求的 JSON 数据
    data = json.dumps(p).encode('utf-8')  # 将 JSON 数据编码为 UTF-8 格式
    requests.post(URL, data=data)  # 发送 POST 请求

# 定义一个函数，用于生成图像并处理前端 UI 传递的变量
def generate_image(prompt_text_positive, prompt_text_negative):
    
    with open("run1.json", "r", encoding="utf-8") as file_json:
        prompt = json.load(file_json)  # 从 JSON 文件中加载提示信息

    prompt["3"]["inputs"]["seed"] = random.randint(1, 1500000000000000)  # 随机生成一个种子值，并传递给 comfyUI

    prompt["6"]["inputs"]["text"] = f"digital artwork of a {prompt_text_positive}"  # 设置正向提示文本
    prompt["7"]["inputs"]["text"] = f"digital artwork of a {prompt_text_negative}"  # 设置负向提示文本

    previous_image = get_latest_image(OUTPUT_DIR)  # 获取当前最新的输出图像

    start_queue(prompt)  # 启动队列并发送请求

    # 循环检查是否有新的图像生成
    while True:
        latest_image = get_latest_image(OUTPUT_DIR)  # 获取最新的输出图像
        if latest_image != previous_image:  # 如果最新的图像与之前的不同
            return latest_image  # 返回最新的图像
        
        time.sleep(1)  # 休眠 1 秒钟后继续循环

# 定义一个函数，用于生成图像并播放音频
def generate_and_play_audio(prompt_text_positive, prompt_text_negative):
    # 生成图像
    image_path = generate_image(prompt_text_positive, prompt_text_negative)
    
    # 返回图像路径和音频文件路径
    return image_path, AUDIO_PATH

# 创建 Gradio 界面，定义输入和输出
with gr.Blocks() as demo:
    with gr.Tab("图像生成"):
        with gr.Row():
            prompt_text_positive = gr.Textbox(label="正向提示文本")
            prompt_text_negative = gr.Textbox(label="负向提示文本")
        with gr.Row():
            generate_button = gr.Button("生成图像")
        output_image = gr.Image(type="filepath", label="生成的图像")
        audio_output = gr.Audio(label="音频", visible=False)

        # 添加一个隐藏的音频标签
        audio_html = f"""
        <audio id="audio" src="{AUDIO_PATH}" style="display:none;"></audio>
        <script>
        function playAudio() {{
            var audio = document.getElementById('audio');
            audio.play();
        }}
        </script>
        """
        gr.HTML(audio_html)

        # 定义点击按钮后的行为
        def on_button_click(prompt_text_positive, prompt_text_negative):
            image_path, audio_path = generate_and_play_audio(prompt_text_positive, prompt_text_negative)
            return image_path, gr.update(value=audio_path, visible=True)

        generate_button.click(on_button_click, inputs=[prompt_text_positive, prompt_text_negative], outputs=[output_image, audio_output])

        # 添加一个 JavaScript 函数来检测图片加载完成并播放音频
        js_code = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var image = document.querySelector('img');
            var audio = document.getElementById('audio');

            image.addEventListener('load', function() {{
                audio.play();
            }});
        }});
        </script>
        """
        gr.HTML(js_code)

# 启动 Gradio 界面，并创建一个公共链接
demo.launch(share=True)