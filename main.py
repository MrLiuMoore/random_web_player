import os
from typing import Union
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
import random
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# 跨域处理
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

def get_image_url(video_url: str) -> str:
    try:
        # 构建图片目录URL
        image_dir_url = video_url.replace('index.m3u8', 'image/')

        # 发送请求获取目录内容
        response = requests.get(image_dir_url, timeout=10)  # 设置超时时间防止长时间等待
        response.raise_for_status()  # 如果响应状态码不是200，抛出HTTPError

        # 解析HTML并提取链接
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.find_all('a', href=True)  # 只查找有href属性的<a>标签

        # 分离出.webp和其他格式链接，并排除上级目录链接
        links = [image_dir_url + tag['href'] for tag in a_tags if tag['href'] != '../']
        webp_links = [link for link in links if link.endswith('.webp')]

        # 优先返回.webp链接，如果没有则从其他链接中随机返回
        if not links:
            return "No image links found."
        return random.choice(webp_links or links)
    except Exception as e:
        print(f"获取图片URL失败: {str(e)}")
        return None

def read_random_line(file_path: str) -> tuple[str, str]:
    """Reads a random line from a given file and returns video URL and image URL."""
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    with open(file_path, 'r') as file:
        lines = file.readlines()

    if not lines:
        raise HTTPException(status_code=400, detail="File is empty")

    random_line = random.choice(lines).strip()
    img_url = get_image_url(random_line)
    
    return random_line, img_url

@app.get("/v1/get_video")
async def get_random_video_url():
    """Returns a random video URL and its corresponding image URL."""
    try:
        file_path = "./file/video_urls.txt"
        video_url, img_url = read_random_line(file_path)
        return {
            "url": video_url,
            "img_url": img_url or ""  # 如果没有找到图片，使用默认图片
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))