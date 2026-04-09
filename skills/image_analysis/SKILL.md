# Image Analysis Skill
多模态图像分析技能，基于免费多模态模型实现图像内容识别、OCR、视觉问答等功能

## 功能
- 图像内容描述
- 文字识别（OCR）
- 视觉问答（VQA）
- 图像分类
- 二维码/条形码识别
- 表格识别

## 配置
无需额外API Key，使用智谱AI免费glm-4v-flash模型，优先级最高

## 用法
```bash
# 图像描述
python symphony_adapter.py '{"image_path": "test.jpg", "action": "describe"}'

# OCR识别
python symphony_adapter.py '{"image_path": "test.png", "action": "ocr"}'

# 视觉问答
python symphony_adapter.py '{"image_path": "test.jpg", "action": "qa", "question": "图中有几个人？"}'
```

## 输出格式
```json
{
  "success": true,
  "data": "图像描述内容/OCR结果/问答答案",
  "message": "执行成功",
  "model_used": "glm-4v-flash",
  "cost": 0
}
```
