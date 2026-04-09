import subprocess
import json

# Use curl via subprocess
cmd = [
    'curl', '-X', 'POST',
    'https://dashscope.aliyuncs.com/api/v1/services/audio/tts',
    '-H', 'Authorization: Bearer sk-fee678dbf4d84f9a910356821c95c0d5',
    '-H', 'Content-Type: application/json',
    '-d', '{"model":"cosyvoice-v2","input":{"text":"hello"},"parameters":{"voice":"longxiaochun"}}',
    '--max-time', '10',
    '-v'
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
print('STDOUT:', result.stdout[:500])
print('STDERR:', result.stderr[:500])
