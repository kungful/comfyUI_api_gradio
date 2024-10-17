import json
import os
import time
import random
import requests
import gradio as gr
import shutil

# 定义变量
URL = "http://127.0.0.1:8188/prompt"
OUTPUT_DIR = "C:\\Users\\h\\Desktop\\ComfyUI_windows_portable\\ComfyUI\\output"

# 定义获取最新图像的逻辑方法，用于之后下面函数的调用
def get_latest_image(folder):
    files = os.listdir(folder)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
    latest_image = os.path.join(folder, image_files[-1]) if image_files else None
    return latest_image

# 开始获取请求进行编码
def start_queue(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    requests.post(URL, data=data)

# 开始生成图像，前端UI定义所需变量传递给json
def generate_image(prompt_text_positive, prompt_text_negative):
    with open("run1.json", "r", encoding="utf-8") as file_json:
        prompt = json.load(file_json)

    prompt["3"]["inputs"]["seed"] = random.randint(1, 1500000000000000)  # 定义种子随机数1到1500000，json的参数传递给comfyUI
    prompt["6"]["inputs"]["text"] = f"digital artwork of a {prompt_text_positive}"
    prompt["7"]["inputs"]["text"] = f"digital artwork of a {prompt_text_negative}"

    previous_image = get_latest_image(OUTPUT_DIR)  # 推理出的最新输出图像保存到指定的OUTPUT_DIR变量路径

    start_queue(prompt)

    # 这是一个循环获取指定路径的最新图像，休眠一秒钟后继续循环
    while True:
        latest_image = get_latest_image(OUTPUT_DIR)
        if latest_image != previous_image:
            # 将最新的图像复制到当前工作目录
            new_image_path = os.path.join(os.getcwd(), os.path.basename(latest_image))
            shutil.copy(latest_image, new_image_path)
            return new_image_path  # 返回最新的图像路径

        time.sleep(1)

# 创建 Gradio 界面，定义输入和输出
demo = gr.Interface(
    fn=generate_image,
    inputs=[gr.Textbox(label="正向提示文本"), gr.Textbox(label="负向提示文本")],
    outputs=gr.Image(type="filepath", label="生成的图像")
)

# 启动 Gradio 界面，并创建一个公共链接
demo.launch(share=True, allowed_paths=[OUTPUT_DIR])
