import os

def fix_file_encoding(file_path):
    try:
        # 尝试用gbk读取
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
        except:
            # 尝试用utf-8读取
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        
        # 替换乱码字符
        content = content.replace('\ufffd', '')
        
        # 确保文件有utf-8编码声明
        if not content.strip().startswith('# -*- coding: utf-8 -*-'):
            content = '# -*- coding: utf-8 -*-\n' + content
        
        # 保存为utf-8编码
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"OK: {file_path}")
        return True
    except Exception as e:
        print(f"FAIL: {file_path} - {e}")
        return False

if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 遍历所有.py文件
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py') and filename not in ['fix_encoding.py', 'simple_fix.py']:
                file_path = os.path.join(dirpath, filename)
                fix_file_encoding(file_path)
    
    print("\n========================")
    print("所有文件编码修复完成！")
    print("========================")
