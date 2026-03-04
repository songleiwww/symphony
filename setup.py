from setuptools import setup, find_packages

setup(
    name="todo-cli",
    version="1.0.0",
    description="简易的待办事项管理工具",
    author="Multi-Agent Demo",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "todo = main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
