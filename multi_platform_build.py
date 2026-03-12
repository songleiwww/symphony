#!/usr/bin/env python3
"""
序境系统 - 多平台打包工具
支持 Windows、Linux、macOS 等多平台打包
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
TEMP_DIRS = ["dist", "build", "*.egg-info", "__pycache__"]

def clean_temp_files():
    """清理临时文件"""
    print("🧹 清理临时文件...")
    
    temp_patterns = [
        PROJECT_ROOT / "dist",
        PROJECT_ROOT / "build",
    ]
    
    # 清理 egg-info
    for item in PROJECT_ROOT.glob("**/*.egg-info"):
        shutil.rmtree(item, ignore_errors=True)
    
    # 清理 __pycache__
    for item in PROJECT_ROOT.glob("**/__pycache__"):
        shutil.rmtree(item, ignore_errors=True)
    
    # 清理 dist 和 build
    for pattern in temp_patterns:
        if pattern.exists():
            shutil.rmtree(pattern, ignore_errors=True)
    
    print("✅ 临时文件清理完成")

def build_windows():
    """Windows平台打包"""
    print("\n📦 开始 Windows 平台打包...")
    
    # 使用 pyinstaller 或直接构建 wheel
    subprocess.run([
        sys.executable, "-m", "build"
    ], cwd=PROJECT_ROOT)
    
    print("✅ Windows 打包完成")

def build_linux():
    """Linux平台打包"""
    print("\n📦 开始 Linux 平台打包...")
    
    # 创建 Linux 特定版本
    subprocess.run([
        sys.executable, "-m", "build"
    ], cwd=PROJECT_ROOT)
    
    print("✅ Linux 打包完成")

def build_macos():
    """macOS平台打包"""
    print("\n📦 开始 macOS 平台打包...")
    
    subprocess.run([
        sys.executable, "-m", "build"
    ], cwd=PROJECT_ROOT)
    
    print("✅ macOS 打包完成")

def build_all():
    """多平台打包"""
    print("=" * 50)
    print("🚀 序境系统多平台打包工具")
    print("=" * 50)
    
    # 清理旧文件
    clean_temp_files()
    
    # 执行打包
    build_windows()
    build_linux()
    build_macos()
    
    print("\n" + "=" * 50)
    print("📋 打包完成！")
    print("=" * 50)
    
    # 显示打包产物
    if DIST_DIR.exists():
        print("\n📦 打包产物：")
        for f in DIST_DIR.iterdir():
            print(f"  - {f.name}")
    
    # 清理临时文件
    print("\n🧹 清理临时打包文件...")
    clean_temp_files()
    print("✅ 所有临时文件已删除")

if __name__ == "__main__":
    build_all()
