import os
import chardet

def fix_file_encoding(file_path):
    try:
        # 读取文件原始内容
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        # 检测编码
        detection = chardet.detect(raw_data)
        encoding = detection['encoding'] or 'gbk'
        
        # 解码内容
        try:
            content = raw_data.decode(encoding)
        except:
            # 尝试用gbk解码
            content = raw_data.decode('gbk', errors='replace')
        
        # 替换乱码字符
        content = content.replace('\ufffd', '')
        
        # 确保文件有utf-8编码声明
        if not content.startswith('# -*- coding: utf-8 -*-'):
            content = '# -*- coding: utf-8 -*-\n' + content
        
        # 保存为utf-8编码
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 修复完成: {file_path}")
        return True
    except Exception as e:
        print(f"❌ 修复失败: {file_path} - {e}")
        return False

if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 遍历所有.py文件
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py') and filename != 'fix_encoding.py':
                file_path = os.path.join(dirpath, filename)
                fix_file_encoding(file_path)
    
    print("\n========================")
    print("所有文件编码修复完成！")
    print("========================")
