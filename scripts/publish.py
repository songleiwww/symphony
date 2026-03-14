# -*- coding: utf-8 -*-
"""
序境交响 - 发布脚本 v2.0.0
"""
import os
import subprocess
import sys

# 配置
REPO_URL = "https://github.com/songleiwww/symphony.git"
VERSION = "2.0.0"

def run(cmd, shell=True):
    """执行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode

def publish_github():
    """发布到GitHub"""
    print("="*60)
    print("发布到 GitHub")
    print("="*60)
    
    # 检查Git
    if run("git --version") != 0:
        print("❌ Git未安装")
        return False
    
    # 初始化Git (如果需要)
    if not os.path.exists(".git"):
        run("git init")
        run(f"git remote add origin {REPO_URL}")
    
    # 添加文件
    print("\n添加文件...")
    run('git add .')
    
    # 提交
    print("\n提交...")
    run(f'git commit -m "Release v{VERSION}"')
    
    # 推送
    print("\n推送...")
    # 使用GH_TOKEN
    github_token = os.environ.get("GH_TOKEN", "")
    if github_token:
        # 设置remote使用token
        run(f'git remote set-url origin https://{github_token}@github.com/songleiwww/symphony.git')
    
    run("git push -u origin main")
    
    print("\n✅ GitHub发布完成!")
    return True

def publish_pypi():
    """发布到PyPI"""
    print("="*60)
    print("发布到 PyPI")
    print("="*60)
    
    # 检查pypi token
    pypi_token = os.environ.get("PYPI_TOKEN", "")
    if not pypi_token:
        print("❌ 未找到 PYPI_TOKEN 环境变量")
        print("请设置: export PYPI_TOKEN=your_token")
        return False
    
    # 构建
    print("\n构建包...")
    run("python -m build")
    
    # 发布
    print("\n发布...")
    run(f"twine upload -u __token__ -p {pypi_token} dist/*")
    
    print("\n✅ PyPI发布完成!")
    return True

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "github"
    
    if target == "github":
        publish_github()
    elif target == "pypi":
        publish_pypi()
    elif target == "all":
        publish_github()
        publish_pypi()
    else:
        print(f"未知目标: {target}")
        print("用法: python publish.py [github|pypi|all]")

if __name__ == "__main__":
    main()
