# setup.py
from setuptools import setup, find_packages

setup(
    name="comfyui_custom_nodes",
    version="0.1.0",
    author="Your Name",
    author_email="zzw17370709160@163.com",
    description="A collection of custom nodes for ComfyUI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zhozhengwei/ComfyUI_simpleAPI_node",
    packages=find_packages(),
    install_requires=[
        "torch",
        "numpy",
        "requests",
        "Pillow",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)