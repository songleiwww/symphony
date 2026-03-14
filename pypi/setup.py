#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony 多模型协作调度系统
PyPI发布准备
"""

import os
from setuptools import setup, find_packages

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 读取 README
readme_path = os.path.join(current_dir, "README.md")
if os.path.exists(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "序境系统 - 多模型协作调度系统"

setup(
    name="symphony-ai",
    version="1.0.1",
    description="多模型协作调度系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="造梦者 & 交交",
    author_email="songlei_www@qq.com",
    url="https://github.com/songleiwww/symphony",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
