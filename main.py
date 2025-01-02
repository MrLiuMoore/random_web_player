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
    """获取视频对应的图片URL"""
    try:
        # 构建图片目录URL
        image_dir_url = video_url.replace('index.m3u8', 'image/')
        
        # 发送请求获取目录内容
        response = requests.get(image_dir_url)
        response.raise_for_status()
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有链接
        links = soup.find_all('a')
        
        # 查找.webp后缀的文件
        webp_files = [link.get('href') for link in links if link.get('href', '').endswith('.webp')]
        
        if webp_files:
            # 返回完整的图片URL
            return f"{image_dir_url}{webp_files[0]}"
            
        return None
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

@app.get("/")
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