# -*- coding: utf-8 -*-
"""
algorithm_sync.py - 优秀算法定期同步机制
支持后续新算法的快速集成、版本管理、自动更??"""
import os
import sys
import json
import importlib
import requests
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

class AlgorithmSyncManager:
    """算法同步管理??"""
    
    def __init__(self, kernel_path: str = None):
        self.kernel_path = kernel_path or os.path.dirname(os.path.abspath(__file__))
        self.algorithm_dir = self.kernel_path
        self.sync_config_path = os.path.join(self.kernel_path, "sync_config.json")
        self.registry_path = os.path.join(self.kernel_path, "algorithm_registry.json")
        
        # 加载配置
        self.config = self._load_config()
        self.registry = self._load_registry()
    
    def _load_config(self) -> Dict:
        """加载同步配置"""
        default_config = {
            "sync_enabled": True,
            "sync_interval_hours": 24 * 7,  # 每周同步一??            "last_sync_time": None,
            "sync_sources": [
                "https://api.clawhub.com/skills/symphony/algorithms",
                "https://gitee.com/openclaw/symphony-algorithms/raw/main/registry.json"
            ],
            "auto_update": True,
            "auto_register": True,
            "backup_before_update": True,
        }
        
        if os.path.exists(self.sync_config_path):
            try:
                with open(self.sync_config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
            except:
                pass
        
        return default_config
    
    def _save_config(self):
        """保存配置"""
        with open(self.sync_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _load_registry(self) -> Dict:
        """加载本地算法注册??"""
        default_registry = {
            "version": "1.0.0",
            "algorithms": {},
        }
        
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    saved_registry = json.load(f)
                    default_registry.update(saved_registry)
            except:
                pass
        
        return default_registry
    
    def _save_registry(self):
        """保存算法注册??"""
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
    
    def _backup_algorithm(self, algo_name: str) -> bool:
        """备份算法文件"""
        if not self.config.get('backup_before_update', True):
            return True
        
        backup_dir = os.path.join(self.kernel_path, "backups", "algorithms")
        os.makedirs(backup_dir, exist_ok=True)
        
        try:
            algo_file = os.path.join(self.algorithm_dir, f"{algo_name.lower()}.py")
            if os.path.exists(algo_file):
                backup_file = os.path.join(backup_dir, f"{algo_name.lower()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.py")
                with open(algo_file, 'r', encoding='utf-8') as src, open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                return True
        except Exception as e:
            print(f"备份算法 {algo_name} 失败: {e}")
            return False
    
    def check_sync_needed(self) -> bool:
        """检查是否需要同??"""
        if not self.config.get('sync_enabled', True):
            return False
        
        last_sync = self.config.get('last_sync_time')
        if not last_sync:
            return True
        
        last_sync_time = datetime.fromisoformat(last_sync)
        interval = timedelta(hours=self.config.get('sync_interval_hours', 24*7))
        return datetime.now() - last_sync_time > interval
    
    def fetch_remote_registry(self) -> Dict:
        """从远程源获取最新算法注册表"""
        for source in self.config.get('sync_sources', []):
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"??{source} 获取注册表失?? {e}")
                continue
        
        return {}
    
    def sync_algorithms(self, force: bool = False) -> Tuple[int, int, int]:
        """
        同步算法
        返回: (新增算法?? 更新算法?? 失败??
        """
        if not force and not self.check_sync_needed():
            return (0, 0, 0)
        
        print("开始同步最新算??..")
        
        remote_registry = self.fetch_remote_registry()
        if not remote_registry or 'algorithms' not in remote_registry:
            print("无法获取远程算法注册表，同步终止")
            return (0, 0, 0)
        
        remote_algos = remote_registry['algorithms']
        local_algos = self.registry.get('algorithms', {})
        
        added = 0
        updated = 0
        failed = 0
        
        for algo_name, remote_info in remote_algos.items():
            remote_version = remote_info.get('version', '0.0.0')
            local_version = local_algos.get(algo_name, {}).get('version', '0.0.0')
            
            # 比较版本
            if remote_version > local_version:
                if algo_name in local_algos:
                    # 更新现有算法
                    print(f"更新算法 {algo_name}: {local_version} ??{remote_version}")
                    if not self._backup_algorithm(algo_name):
                        failed += 1
                        continue
                    
                    if self._download_algorithm(algo_name, remote_info):
                        updated += 1
                        local_algos[algo_name] = remote_info
                    else:
                        failed += 1
                else:
                    # 新增算法
                    print(f"新增算法 {algo_name}: {remote_version}")
                    if self._download_algorithm(algo_name, remote_info):
                        added += 1
                        local_algos[algo_name] = remote_info
                    else:
                        failed += 1
        
        # 更新注册表和配置
        self.registry['algorithms'] = local_algos
        self.registry['version'] = remote_registry.get('version', self.registry['version'])
        self.config['last_sync_time'] = datetime.now().isoformat()
        
        self._save_registry()
        self._save_config()
        
        print(f"同步完成: 新增{added}?? 更新{updated}?? 失败{failed}??)
        return (added, updated, failed)
    
    def _download_algorithm(self, algo_name: str, remote_info: Dict) -> bool:
        """下载算法文件"""
        try:
            download_url = remote_info.get('download_url')
            if not download_url:
                print(f"算法 {algo_name} 没有提供下载地址")
                return False
            
            response = requests.get(download_url, timeout=30)
            if response.status_code != 200:
                print(f"下载 {algo_name} 失败，状态码: {response.status_code}")
                return False
            
            # 保存算法文件
            algo_file = os.path.join(self.algorithm_dir, f"{algo_name.lower()}.py")
            with open(algo_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # 自动注册到协调器
            if self.config.get('auto_register', True):
                self._register_algorithm(algo_name, remote_info)
            
            return True
        except Exception as e:
            print(f"下载算法 {algo_name} 失败: {e}")
            return False
    
    def _register_algorithm(self, algo_name: str, info: Dict):
        """自动注册算法到协调器"""
        try:
            # 修改adaptive_algorithm_coordinator.py，添加注册代??            coordinator_file = os.path.join(self.algorithm_dir, "adaptive_algorithm_coordinator.py")
            with open(coordinator_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已经注??            if f'name="{algo_name}"' in content:
                return
            
            # 添加导入
            import_line = f"from .{algo_name.lower()} import {algo_name}\n"
            import_section_end = content.find("# 初始化主动适应引擎")
            if import_section_end != -1:
                content = content[:import_section_end] + import_line + content[import_section_end:]
            
            # 添加注册代码
            register_code = f"""
        # {info.get('description', '新增算法')}
        self.register(
            name="{algo_name}",
            category=AlgorithmCategory.SWARM,
            instance={algo_name}(**{json.dumps(info.get('default_parameters', {}))}),
            metadata={json.dumps(info.get('metadata', {}), ensure_ascii=False)},
        )
"""
            register_section_end = content.find("# 初始化主动适应引擎")
            if register_section_end != -1:
                content = content[:register_section_end] + register_code + content[register_section_end:]
            
            with open(coordinator_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"算法 {algo_name} 已自动注册到协调??)
        
        except Exception as e:
            print(f"自动注册算法 {algo_name} 失败: {e}")
    
    def get_installed_algorithms(self) -> List[Dict]:
        """获取已安装的算法列表"""
        return list(self.registry.get('algorithms', {}).values())
    
    def add_local_algorithm(self, algo_name: str, info: Dict, code: str) -> bool:
        """手动添加本地算法"""
        try:
            # 保存算法文件
            algo_file = os.path.join(self.algorithm_dir, f"{algo_name.lower()}.py")
            with open(algo_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # 更新注册??            self.registry['algorithms'][algo_name] = info
            self._save_registry()
            
            # 自动注册
            if self.config.get('auto_register', True):
                self._register_algorithm(algo_name, info)
            
            print(f"本地算法 {algo_name} 添加成功")
            return True
        except Exception as e:
            print(f"添加本地算法 {algo_name} 失败: {e}")
            return False

# 全局同步管理器实??sync_manager = AlgorithmSyncManager()

# 内核启动时自动检查同??def auto_sync_on_startup():
    if sync_manager.config.get('auto_update', False):
        sync_manager.sync_algorithms()

__all__ = ['AlgorithmSyncManager', 'sync_manager', 'auto_sync_on_startup']

