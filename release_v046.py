#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v0.4.6 Release - 交响v0.4.6发布
Multi-Model Release Mode - 多模型版本发布模式
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("Symphony v0.4.6 Release - 交响v0.4.6发布")
print("Multi-Model Release Mode - 多模型版本发布模式")
print("=" * 80)

# Author info - 作者信息
AUTHOR = "步花间"
AUTHOR_EN = "Huajian Bu"
EMAIL = "songlei_www@hotmail.com"
LOCATION = "Beijing, China"
LOCATION_CN = "中国，北京"

print("\n[1] Author Info - 作者信息")
print("-" * 80)
print(f"  作者: {AUTHOR} ({AUTHOR_EN})")
print(f"  邮箱: {EMAIL}")
print(f"  地点: {LOCATION_CN} ({LOCATION})")

# GitHub Repository Info - GitHub仓库信息
REPO_OWNER = "songleiwww"
REPO_NAME = "symphony"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"

print("\n[2] GitHub Repository - GitHub仓库")
print("-" * 80)
print(f"  所有者: {REPO_OWNER}")
print(f"  仓库: {REPO_NAME}")
print(f"  地址: {REPO_URL}")

# Update README.md - 更新README.md
print("\n[3] Updating README.md - 更新README.md")
print("-" * 80)

readme_path = Path(__file__).parent / "README.md"

if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
    
    # Fix encoding issues and update metadata - 修复编码问题并更新元数据
    new_readme = readme_content
    
    # Update author/contact info - 更新作者/联系信息
    new_readme = new_readme.replace(
        "your.email@example.com",
        EMAIL
    )
    
    # Update Twitter handle - 更新Twitter
    new_readme = new_readme.replace(
        "[@yourhandle](https://twitter.com/yourhandle)",
        f"[@{REPO_OWNER}](https://github.com/{REPO_OWNER})"
    )
    
    # Write updated README - 写入更新后的README
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme)
    
    print("  ✅ README.md updated!")
else:
    print("  ⚠️  README.md not found!")

# Update setup.py if exists - 更新setup.py（如果存在）
print("\n[4] Checking setup.py - 检查setup.py")
print("-" * 80)

setup_path = Path(__file__).parent / "setup.py"

if setup_path.exists():
    with open(setup_path, "r", encoding="utf-8") as f:
        setup_content = f.read()
    
    new_setup = setup_content
    
    # Update author info - 更新作者信息
    new_setup = new_setup.replace(
        'author="Your Name"',
        f'author="{AUTHOR}"'
    )
    new_setup = new_setup.replace(
        'author_email="your.email@example.com"',
        f'author_email="{EMAIL}"'
    )
    
    with open(setup_path, "w", encoding="utf-8") as f:
        f.write(new_setup)
    
    print("  ✅ setup.py updated!")
else:
    print("  ⚠️  setup.py not found, skipping...")

# Create or update package.json for npm-style metadata - 创建或更新package.json（npm风格元数据）
print("\n[5] Creating package.json (metadata) - 创建package.json（元数据）")
print("-" * 80)

package_json = {
    "name": "symphony",
    "version": "0.4.6",
    "description": "Symphony - A complete multi-model collaboration platform",
    "description_cn": "交响 - 一个完整的多模型协作平台",
    "author": {
        "name": AUTHOR,
        "name_en": AUTHOR_EN,
        "email": EMAIL,
        "location": LOCATION,
        "location_cn": LOCATION_CN
    },
    "repository": {
        "type": "git",
        "url": f"{REPO_URL}.git"
    },
    "homepage": REPO_URL,
    "bugs": {
        "url": f"{REPO_URL}/issues"
    },
    "license": "MIT",
    "keywords": [
        "multi-agent",
        "collaboration",
        "ai",
        "llm",
        "symphony",
        "多模型",
        "协作"
    ],
    "brand": {
        "slogan": "智韵交响，共创华章",
        "slogan_en": "Harmony of Minds, Creation of Excellence"
    }
}

import json
package_path = Path(__file__).parent / "package.json"
with open(package_path, "w", encoding="utf-8") as f:
    json.dump(package_json, f, ensure_ascii=False, indent=2)

print(f"  ✅ package.json created at: {package_path}")

# Create CITATION.cff - 创建CITATION.cff
print("\n[6] Creating CITATION.cff - 创建CITATION.cff")
print("-" * 80)

citation_content = f"""cff-version: 1.2.0
message: If you use this software, please cite it as below.
type: software
title: Symphony
title-translation:
  zh: 交响
abstract: A complete multi-model collaboration platform
abstract-translation:
  zh: 一个完整的多模型协作平台
authors:
  - family-names: Bu
    given-names: Huajian
    name-translation:
      zh: 步花间
    email: {EMAIL}
    affiliation: Independent Researcher
    location: {LOCATION}
repository-code: {REPO_URL}
url: {REPO_URL}
license: MIT
version: 0.4.6
date-released: 2026-03-05
keywords:
  - multi-agent
  - collaboration
  - ai
  - llm
  - 多模型
  - 协作
"""

citation_path = Path(__file__).parent / "CITATION.cff"
with open(citation_path, "w", encoding="utf-8") as f:
    f.write(citation_content)

print(f"  ✅ CITATION.cff created at: {citation_path}")

# Update VERSION.md - 更新VERSION.md
print("\n[7] Updating VERSION.md - 更新VERSION.md")
print("-" * 80)

version_path = Path(__file__).parent / "VERSION.md"

if version_path.exists():
    with open(version_path, "r", encoding="utf-8") as f:
        version_content = f.read()
    
    v046_entry = f"""
## v0.4.6 - Author Metadata & GitHub Repository Setup (2026-03-05)
### New Features
- 📝 **Complete Author Metadata**
  - Author: {AUTHOR} ({AUTHOR_EN})
  - Email: {EMAIL}
  - Location: {LOCATION_CN} ({LOCATION})

- 🏷️ **GitHub Repository Setup**
  - Repository: {REPO_URL}
  - package.json created for metadata
  - CITATION.cff created for academic citation
  - README.md updated with contact info

### Files Added
- `package.json` - Project metadata (npm-style)
- `CITATION.cff` - Academic citation file

### Files Updated
- `README.md` - Updated contact information
- `setup.py` - Updated author information (if exists)
"""
    
    # Insert at the beginning - 在开头插入
    new_version = v046_entry + "\n" + version_content
    
    with open(version_path, "w", encoding="utf-8") as f:
        f.write(new_version)
    
    print("  ✅ VERSION.md updated!")
else:
    print("  ⚠️  VERSION.md not found!")

# Create release report - 创建发布报告
print("\n[8] Creating release report - 创建发布报告")
print("-" * 80)

report_content = f"""# Symphony v0.4.6 Release Report - 交响v0.4.6发布报告

**发布时间**: 2026-03-05  
**版本**: v0.4.6  
**模式**: 多模型版本发布模式

---

## 作者信息 - Author Information

| 字段 | 值 |
|------|-----|
| 作者 | {AUTHOR} |
| 作者（英文）| {AUTHOR_EN} |
| 邮箱 | {EMAIL} |
| 地点 | {LOCATION_CN} |
| 地点（英文）| {LOCATION} |

---

## GitHub仓库信息 - GitHub Repository Info

| 字段 | 值 |
|------|-----|
| 所有者 | {REPO_OWNER} |
| 仓库名 | {REPO_NAME} |
| 仓库地址 | {REPO_URL} |
| 问题追踪 | {REPO_URL}/issues |
| 讨论区 | {REPO_URL}/discussions |

---

## 更新内容 - What's Updated

### 新增文件 - Files Added
1. `package.json` - 项目元数据（npm风格）
2. `CITATION.cff` - 学术引用文件

### 更新文件 - Files Updated
1. `README.md` - 更新联系信息
2. `VERSION.md` - 添加v0.4.6发布记录
3. `setup.py` - 更新作者信息（如果存在）

---

## package.json元数据 - package.json Metadata

```json
{json.dumps(package_json, ensure_ascii=False, indent=2)}
```

---

## CITATION.cff - 学术引用

```
{citation_content.strip()}
```

---

## 品牌信息 - Brand Info

| 项目 | 值 |
|------|-----|
| 项目名（中文）| 交响 |
| 项目名（英文）| Symphony |
| 品牌标语（中文）| 智韵交响，共创华章 |
| 品牌标语（英文）| Harmony of Minds, Creation of Excellence |

---

## 总结 - Summary

v0.4.6完成了：
- ✅ 完整作者元数据（中英文）
- ✅ GitHub仓库正规化配置
- ✅ package.json元数据文件
- ✅ CITATION.cff学术引用文件
- ✅ README.md联系信息更新
- ✅ VERSION.md版本记录更新

---

智韵交响，共创华章
"""

report_path = Path(__file__).parent / "RELEASE_v046_REPORT.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"  ✅ Release report created at: {report_path}")

# Summary - 总结
print("\n" + "=" * 80)
print("SUMMARY - 总结")
print("=" * 80)

print("\n✅ v0.4.6 Release Complete!")
print("✅ v0.4.6发布完成！")
print("\nFiles:")
print(f"  - package.json (created)")
print(f"  - CITATION.cff (created)")
print(f"  - README.md (updated)")
print(f"  - VERSION.md (updated)")
print(f"  - RELEASE_v046_REPORT.md (created)")
print(f"  - release_v046.py (this script)")

print("\nAuthor Info:")
print(f"  - {AUTHOR} ({AUTHOR_EN})")
print(f"  - {EMAIL}")
print(f"  - {LOCATION_CN}")

print("\nRepository:")
print(f"  - {REPO_URL}")

print("\n" + "=" * 80)
print("智韵交响，共创华章")
print("=" * 80)
