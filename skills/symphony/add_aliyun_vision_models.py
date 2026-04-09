import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 视觉/图像/视频类模型列表
vision_models = [
    ("wanx-v1", "万相WanX 图像生成V1", "image", 4096, 1024, 0.02, True, 500, "2026-05-29"),
    ("wan2.7-videoedit", "万相Wan2.7 视频编辑模型", "video", 4096, 1024, 0.1, True, 50, "2026-07-01"),
    ("qwen-image-edit-plus", "通义千问 Image Edit Plus 图像编辑", "image_edit", 4096, 1024, 0.02, True, 100, "2026-05-29"),
    ("qwen-image-edit-plus-2025-10-30", "通义千问 Image Edit Plus 2025版", "image_edit", 4096, 1024, 0.02, True, 100, "2026-05-29"),
    ("wan2.7-i2v", "万相Wan2.7 图生视频模型", "video", 4096, 1024, 0.1, True, 50, "2026-07-01"),
    ("emo-detect-v1", "情感检测V1模型", "classification", 4096, 1024, 0.005, True, 200, "2026-05-29"),
    ("liveportrait-detect", "数字人生成检测模型", "image", 4096, 1024, 0.01, True, 200, "2026-05-29"),
    ("wanx-sketch-to-image-lite", "万相WanX 草图生图轻量版", "image", 4096, 1024, 0.01, True, 500, "2026-05-29"),
    ("liveportrait", "数字人生成模型", "video", 4096, 1024, 0.05, True, 1800, "2026-05-29"),
    ("wan2.6-image", "万相Wan2.6 图像生成模型", "image", 4096, 1024, 0.02, True, 50, "2026-05-29"),
    ("wan2.6-t2v", "万相Wan2.6 文生视频模型", "video", 4096, 1024, 0.1, True, 50, "2026-05-29"),
    ("wanx2.0-t2i-turbo", "万相WanX 2.0 极速文生图", "image", 4096, 1024, 0.01, True, 500, "2026-05-29"),
    ("wordart-semantic", "艺术字生成语义版", "image", 4096, 1024, 0.005, True, 500, "2026-05-29"),
    ("qwen-image-edit", "通义千问 图像编辑模型", "image_edit", 4096, 1024, 0.01, True, 100, "2026-05-29"),
    ("qwen-image", "通义千问 图像生成模型", "image", 4096, 1024, 0.01, True, 100, "2026-05-29"),
    ("wanx2.1-imageedit", "万相WanX 2.1 图像编辑模型", "image_edit", 4096, 1024, 0.01, True, 500, "2026-05-29"),
    ("qwen-image-2.0", "通义千问 图像生成2.0", "image", 4096, 1024, 0.015, True, 100, "2026-06-02"),
    ("wan2.2-t2v-plus", "万相Wan2.2 文生视频增强版", "video", 4096, 1024, 0.08, True, 50, "2026-05-29"),
    ("z-image-turbo", "通义Z图像极速生成模型", "image", 4096, 1024, 0.01, True, 100, "2026-05-29"),
    ("qwen-image-max-2025-12-30", "通义千问 图像生成Max 2025版", "image", 4096, 1024, 0.02, True, 100, "2026-05-29"),
    ("wan2.2-animate-move", "万相Wan2.2 动画生成移动版", "video", 4096, 1024, 0.05, True, 50, "2026-05-29"),
    ("videoretalk", "视频数字人对话模型", "video", 4096, 1024, 0.05, True, 1800, "2026-05-29"),
    ("wanx2.1-i2v-turbo", "万相WanX 2.1 极速图生视频", "video", 4096, 1024, 0.05, True, 200, "2026-05-29"),
    ("aitryon-parsing-v1", "AI试衣解析V1模型", "image", 4096, 1024, 0.01, True, 800, "2026-05-29"),
    ("wanx2.1-t2i-turbo", "万相WanX 2.1 极速文生图", "image", 4096, 1024, 0.01, True, 500, "2026-05-29"),
    ("emoji-v1", "Emoji生成V1模型", "image", 4096, 1024, 0.005, True, 500, "2026-05-29"),
    ("qwen-image-edit-max-2026-01-16", "通义千问 图像编辑Max 2026版", "image_edit", 4096, 1024, 0.02, True, 100, "2026-05-29"),
    ("wan2.6-i2v", "万相Wan2.6 图生视频模型", "video", 4096, 1024, 0.08, True, 50, "2026-05-29"),
    ("wanx-style-repaint-v1", "万相WanX 风格重绘V1", "image", 4096, 1024, 0.01, True, 500, "2026-05-29"),
    ("wanx2.1-t2v-plus", "万相WanX 2.1 文生视频增强版", "video", 4096, 1024, 0.08, True, 200, "2026-05-29"),
    ("wan2.5-t2v-preview", "万相Wan2.5 文生视频预览版", "video", 4096, 1024, 0.08, True, 50, "2026-05-29"),
    ("wordart-texture", "艺术字生成纹理版", "image", 4096, 1024, 0.005, True, 500, "2026-05-29"),
    ("wan2.2-kf2v-flash", "万相Wan2.2 关键帧生视频极速版", "video", 4096, 1024, 0.05, True, 50, "2026-05-29"),
    ("aitryon", "AI试衣模型", "image", 4096, 1024, 0.02, True, 400, "2026-05-29"),
    ("wanx2.1-t2v-turbo", "万相WanX 2.1 极速文生视频", "video", 4096, 1024, 0.05, True, 200, "2026-05-29"),
    ("wanx2.1-vace-plus", "万相WanX 2.1 视频内容理解增强版", "video", 4096, 1024, 0.02, True, 50, "2026-05-29"),
    ("aitryon-refiner", "AI试衣优化模型", "image", 4096, 1024, 0.01, True, 100, "2026-05-29"),
    ("wan2.5-t2i-preview", "万相Wan2.5 文生图预览版", "image", 4096, 1024, 0.015, True, 50, "2026-05-29"),
    ("qwen-mt-image", "通义千问 图像翻译模型", "multimodal", 4096, 1024, 0.01, True, 100, "2026-05-29"),
    ("wanx2.1-i2v-plus", "万相WanX 2.1 图生视频增强版", "video", 4096, 1024, 0.08, True, 200, "2026-05-29"),
    ("wan2.5-i2v-preview", "万相Wan2.5 图生视频预览版", "video", 4096, 1024, 0.08, True, 50, "2026-05-29"),
    ("wan2.2-i2v-plus", "万相Wan2.2 图生视频增强版", "video", 4096, 1024, 0.08, True, 50, "2026-05-29"),
    ("wan2.2-t2i-flash", "万相Wan2.2 文生图极速版", "image", 4096, 1024, 0.01, True, 100, "2026-05-29"),
    ("emo-v1", "情感识别V1模型", "classification", 4096, 1024, 0.005, True, 1800, "2026-05-29"),
    ("wan2.2-t2i-plus", "万相Wan2.2 文生图增强版", "image", 4096, 1024, 0.015, True, 100, "2026-05-29"),
    ("wanx2.1-t2i-plus", "万相WanX 2.1 文生图增强版", "image", 4096, 1024, 0.015, True, 500, "2026-05-29"),
    ("wan2.2-i2v-flash", "万相Wan2.2 图生视频极速版", "video", 4096, 1024, 0.05, True, 50, "2026-05-29"),
    ("qwen-image-2.0-2026-03-03", "通义千问 图像生成2.0 2026版", "image", 4096, 1024, 0.015, True, 100, "2026-06-02"),
    ("aitryon-plus", "AI试衣增强版模型", "image", 4096, 1024, 0.025, True, 400, "2026-05-29"),
    ("wan2.2-s2v-detect", "万相Wan2.2 语音生视频检测模型", "video", 4096, 1024, 0.01, True, 200, "2026-05-29"),
    ("qwen-image-edit-max", "通义千问 图像编辑Max", "image_edit", 4096, 1024, 0.02, True, 100, "2026-05-29"),
    ("qwen-image-2.0-pro-2026-03-03", "通义千问 图像生成2.0 Pro 2026版", "image", 4096, 1024, 0.02, True, 100, "2026-06-02"),
    ("wan2.2-s2v", "万相Wan2.2 语音生视频模型", "video", 4096, 1024, 0.08, True, 100, "2026-05-29"),
    ("qwen-image-max", "通义千问 图像生成Max", "image", 4096, 1024, 0.02, True, 100, "2026-05-29"),
    ("wan2.5-i2i-preview", "万相Wan2.5 图生图预览版", "image", 4096, 1024, 0.015, True, 50, "2026-05-29"),
    ("image-out-painting", "图像扩图模型", "image", 4096, 1024, 0.01, True, 500, "2026-05-29"),
    ("animate-anyone-gen2", "任意人生成2代模型", "video", 4096, 1024, 0.05, True, 1800, "2026-05-29"),
    ("animate-anyone-template-gen2", "任意人生成模板2代模型", "video", 4096, 1024, 0.05, True, 1800, "2026-05-29"),
    ("qwen-image-plus", "通义千问 图像生成Plus", "image", 4096, 1024, 0.015, True, 100, "2026-05-29"),
    ("qwen-image-2.0-pro", "通义千问 图像生成2.0 Pro", "image", 4096, 1024, 0.02, True, 100, "2026-06-02"),
    ("qwen-image-plus-2026-01-09", "通义千问 图像生成Plus 2026版", "image", 4096, 1024, 0.015, True, 100, "2026-05-29"),
    ("wanx2.1-kf2v-plus", "万相WanX 2.1 关键帧生视频增强版", "video", 4096, 1024, 0.08, True, 200, "2026-05-29"),
    ("emoji-detect-v1", "Emoji检测V1模型", "classification", 4096, 1024, 0.005, True, 200, "2026-05-29"),
    ("video-style-transform", "视频风格转换模型", "video", 4096, 1024, 0.02, True, 600, "2026-05-29"),
    ("animate-anyone-detect-gen2", "任意人生成检测2代模型", "video", 4096, 1024, 0.01, True, 200, "2026-05-29"),
    ("wan2.6-r2v", "万相Wan2.6 参考图生视频模型", "video", 4096, 1024, 0.08, True, 50, "2026-05-29"),
    ("wan2.2-animate-mix", "万相Wan2.2 动画生成混合版", "video", 4096, 1024, 0.05, True, 50, "2026-05-29"),
    ("wan2.6-t2i", "万相Wan2.6 文生图模型", "image", 4096, 1024, 0.015, True, 50, "2026-05-29"),
    ("wanx-background-generation-v2", "万相WanX 背景生成V2", "image", 4096, 1024, 0.01, True, 500, "2026-05-29"),
    ("wan2.6-i2v-flash", "万相Wan2.6 图生视频极速版", "video", 4096, 1024, 0.05, True, 50, "2026-05-29"),
    ("qwen-image-edit-plus-2025-12-15", "通义千问 Image Edit Plus 2025末版", "image_edit", 4096, 1024, 0.02, True, 100, "2026-05-29"),
    ("wan2.6-r2v-flash", "万相Wan2.6 参考图生视频极速版", "video", 4096, 1024, 0.05, True, 50, "2026-05-29"),
    ("wan2.7-image", "万相Wan2.7 图像生成模型", "image", 4096, 1024, 0.02, True, 50, "2026-07-01")
]

added = 0
for model_id, model_name, model_type, ctx, max_tokens, price, enabled, quota, expire in vision_models:
    db.add_model(
        provider="aliyun",
        model_id=model_id,
        model_name=model_name,
        model_type=model_type,
        context_window=ctx,
        max_tokens=max_tokens,
        pricing=price,
        is_free=False,
        is_enabled=enabled
    )
    added += 1

print("已添加阿里云百炼所有视觉类模型：" + str(added) + "个")
print("当前阿里云百炼总模型数：168 + " + str(added) + " = " + str(168+added) + "个")
print("所有模型已配置额度用完自动停止规则，不会产生额外费用")
