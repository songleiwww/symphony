#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘文件锁机制 v1.0
防止并发写入MEMORY.md
"""
import os
import time
import json

LOCK_FILE = "C:\\Users\\Administrator\\.openclaw\\workspace\\.memory.lock"
MAX_WAIT = 30  # 最大等待时间（秒）

def acquire_lock():
    """获取文件锁"""
    start_time = time.time()
    
    while os.path.exists(LOCK_FILE):
        # 检查锁是否过期
        try:
            with open(LOCK_FILE, 'r') as f:
                lock_data = json.load(f)
                lock_time = lock_data.get('time', 0)
                
                # 如果锁超过5分钟，认为是过期锁
                if time.time() - lock_time > 300:
                    os.remove(LOCK_FILE)
                    break
        except:
            pass
        
        if time.time() - start_time > MAX_WAIT:
            return False
        
        time.sleep(0.5)
    
    # 创建锁文件
    with open(LOCK_FILE, 'w') as f:
        json.dump({'time': time.time(), 'pid': os.getpid()}, f)
    
    return True

def release_lock():
    """释放文件锁"""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def write_memory_safe(content, file_path):
    """安全写入文件"""
    try:
        # 获取锁
        if not acquire_lock():
            print(f"无法获取锁: {file_path}")
            return False
        
        # 写入文件
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        # 释放锁
        release_lock()
        return True
    
    except Exception as e:
        print(f"写入失败: {e}")
        release_lock()
        return False

# 测试
if __name__ == '__main__':
    test_content = "\n\n--- 测试写入 ---\n"
    
    result = write_memory_safe(test_content, "C:\\Users\\Administrator\\.openclaw\\workspace\\test.txt")
    print(f"写入结果: {result}")
