from setuptools import setup, find_packages

setup(
    name="symphony-ai",
    version="2.0.0",
    description="序境交响 - 智能多模型协作调度系统",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="序境系统",
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
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai multi-model collaboration symphony agent",
)
