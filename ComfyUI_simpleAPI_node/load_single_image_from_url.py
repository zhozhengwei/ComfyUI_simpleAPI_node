# comfyui_custom_nodes/load_single_image_from_url.py
import torch
import numpy as np
import requests
from PIL import Image, ImageOps, ImageSequence
from io import BytesIO

class LoadSingleImageFromURL:
    """
    从远程 URL 加载单张图片并嵌入到工作流中
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "", "multiline": False}),  # 图片的 URL
                "timeout": ("INT", {"default": 30, "min": 1, "max": 120}),  # 请求超时时间
            },
            "optional": {
                "proxy": ("STRING", {"default": None}),  # 代理设置
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_image"
    CATEGORY = "Custom Nodes"

    def load_image(self, url, timeout=30, proxy=None):
        """
        从 URL 加载图片并返回图像和掩码
        """
        # 设置代理
        proxies = None
        if proxy:
            proxies = {
                "http": proxy,
                "https": proxy,
            }

        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            # 发送请求
            print(f"正在从 URL 加载图片: {url}")
            response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            response.raise_for_status()  # 检查请求是否成功
            print("图片加载成功！")

            # 打开图片
            img = Image.open(BytesIO(response.content))
            img = ImageOps.exif_transpose(img)  # 处理 EXIF 方向信息
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            raise ValueError(f"无法从 URL 加载图片: {e}")
        except Exception as e:
            print(f"处理图片时发生错误: {e}")
            raise ValueError(f"处理图片时发生错误: {e}")

        # 初始化输出列表
        output_images = []
        output_masks = []
        w, h = None, None

        # 排除不支持的多帧格式
        excluded_formats = ['MPO']

        # 遍历图片的每一帧（如果是多帧图片）
        for i in ImageSequence.Iterator(img):
            i = ImageOps.exif_transpose(i)  # 处理 EXIF 方向信息

            # 处理灰度图像
            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))

            # 将图片转换为 RGB 模式
            image = i.convert("RGB")

            # 如果是第一帧，记录图片的尺寸
            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]

            # 如果图片尺寸与第一帧不一致，跳过该帧
            if image.size[0] != w or image.size[1] != h:
                continue

            # 将图片转换为 NumPy 数组并归一化
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]  # 添加批次维度

            # 生成掩码
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

            # 将图片和掩码添加到输出列表
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        # 如果是多帧图片且格式不在排除列表中，将所有帧拼接成一个张量
        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, output_mask)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "LoadSingleImageFromURL": LoadSingleImageFromURL,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadSingleImageFromURL": "Load Single Image From URL",
}