# 交响主大脑配置
BRAIN_CONFIG = {
    " name\: \豆包主大脑\,
 \api_url\: \https://ark.cn-beijing.volces.com/api/coding/v3\,
 \api_key\: \3b922877-3fbe-45d1-a298-53f2231c5224\,
 \primary_model\: \ark-code-latest\,
 \backup_brains\: [
 {\model\: \doubao-seed-code\, \name\: \豆包代码模型\},
 {\model\: \glm-4.7\, \name\: \智谱模型\},
 {\model\: \deepseek-v3.2\, \name\: \DeepSeek模型\},
 ]
}

def get_brain_info():
 return BRAIN_CONFIG
