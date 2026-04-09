# -*- coding: utf-8 -*-
"""
Symphony Skills 整体测试脚本
用于验证 skills/symphony 目录的完整性和功能
"""

import sys
import os
import time
from pathlib import Path

# 添加 symphony 到路径
SYMPHONY_PATH = Path(__file__).parent
sys.path.insert(0, str(SYMPHONY_PATH))

class TestColors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{TestColors.BOLD}{TestColors.BLUE}{'='*60}{TestColors.END}")
    print(f"{TestColors.BOLD}{TestColors.BLUE}{text:^60}{TestColors.END}")
    print(f"{TestColors.BOLD}{TestColors.BLUE}{'='*60}{TestColors.END}\n")

def print_success(text):
    print(f"{TestColors.GREEN}[PASS] {text}{TestColors.END}")

def print_error(text):
    print(f"{TestColors.RED}[FAIL] {text}{TestColors.END}")

def print_info(text):
    print(f"{TestColors.YELLOW}[INFO] {text}{TestColors.END}")

def test_directory_structure():
    """测试目录结构"""
    print_header("测试 1: 目录结构验证")
    
    required_dirs = [
        "Kernel",
        "Kernel/evolution",
        "Kernel/multi_agent",
        "algorithms",
        "strategy",
        "providers",
        "config",
        "data",
        "docs"
    ]
    
    all_passed = True
    for dir_path in required_dirs:
        full_path = SYMPHONY_PATH / dir_path
        if full_path.exists() and full_path.is_dir():
            print_success(f"目录存在：{dir_path}")
        else:
            print_error(f"目录缺失：{dir_path}")
            all_passed = False
    
    return all_passed

def test_core_files():
    """测试核心文件"""
    print_header("测试 2: 核心文件验证")
    
    required_files = [
        "Kernel/__init__.py",
        "Kernel/evolution_kernel.py",
        "Kernel/wisdom_engine.py",
        "Kernel/model_federation.py",
        "Kernel/intelligent_strategy_scheduler.py",
        "algorithms/__init__.py",
        "algorithms/ant_colony.py",
        "algorithms/bee_colony.py",
        "strategy/__init__.py",
        "strategy/dual_engine_scheduler.py",
        "providers/__init__.py",
        "providers/pool.py",
        "config/__init__.py",
        "config/provider_mapping.py",
        "README.md"
    ]
    
    all_passed = True
    for file_path in required_files:
        full_path = SYMPHONY_PATH / file_path
        if full_path.exists():
            print_success(f"文件存在：{file_path}")
        else:
            print_error(f"文件缺失：{file_path}")
            all_passed = False
    
    return all_passed

def test_imports():
    """测试模块导入"""
    print_header("测试 3: 模块导入验证")
    
    test_imports = [
        ("Kernel", "Kernel"),
        ("Kernel.evolution_kernel", "EvolutionKernel"),
        ("Kernel.wisdom_engine", "WisdomEngine"),
        ("Kernel.wisdom_engine", "WisdomEmergenceEngine"),
        ("Kernel.wisdom_engine", "BrainClusterManager"),
        ("Kernel.model_federation", "ModelFederation"),
        ("algorithms.ant_colony", "ACO"),
        ("algorithms.bee_colony", "BeeColonyOptimizer"),
        ("strategy.dual_engine_scheduler", "DualEngineScheduler"),
        ("providers.pool", "ProviderPool"),
    ]
    
    all_passed = True
    for module_name, class_name in test_imports:
        try:
            module = __import__(module_name, fromlist=[class_name])
            if hasattr(module, class_name):
                print_success(f"成功导入：{module_name}.{class_name}")
            else:
                print_info(f"模块存在但类缺失：{module_name}.{class_name}")
        except Exception as e:
            print_error(f"导入失败：{module_name} - {str(e)}")
            all_passed = False
    
    return all_passed

def test_evolution_module():
    """测试进化模块"""
    print_header("测试 4: 进化模块验证")
    
    evolution_files = [
        "Kernel/evolution/__init__.py",
        "Kernel/evolution/self_evolver.py",
        "Kernel/evolution/self_evolution_v2.py",
        "Kernel/evolution/agent_memory_layer.py",
        "Kernel/evolution/lifecycle_manager.py",
        "Kernel/evolution/unit_registry.py"
    ]
    
    all_passed = True
    for file_path in evolution_files:
        full_path = SYMPHONY_PATH / file_path
        if full_path.exists():
            print_success(f"进化模块文件存在：{file_path}")
        else:
            print_error(f"进化模块文件缺失：{file_path}")
            all_passed = False
    
    return all_passed

def test_multi_agent_module():
    """测试多Agent模块"""
    print_header("测试 5: 多Agent模块验证")
    
    multi_agent_files = [
        "Kernel/multi_agent/__init__.py",
        "Kernel/multi_agent/multi_agent_orchestrator.py",
        "Kernel/multi_agent/detect_then_team.py"
    ]
    
    all_passed = True
    for file_path in multi_agent_files:
        full_path = SYMPHONY_PATH / file_path
        if full_path.exists():
            print_success(f"多Agent文件存在：{file_path}")
        else:
            print_error(f"多Agent文件缺失：{file_path}")
            all_passed = False
    
    return all_passed

def test_config_files():
    """测试配置文件"""
    print_header("测试 6: 配置文件验证")
    
    config_files = [
        "config/provider_mapping.py",
        "config/scheduling_strategy.py",
        "config/task_complexity.py",
        "config/tokens_config.py",
        "config/compliance_engine.py"
    ]
    
    all_passed = True
    for file_path in config_files:
        full_path = SYMPHONY_PATH / file_path
        if full_path.exists():
            print_success(f"配置文件存在：{file_path}")
        else:
            print_error(f"配置文件缺失：{file_path}")
            all_passed = False
    
    return all_passed

def test_documentation():
    """测试文档"""
    print_header("测试 7: 文档验证")
    
    doc_files = [
        "README.md",
        "QUICKSTART.md"
    ]
    
    all_passed = True
    for file_path in doc_files:
        full_path = SYMPHONY_PATH / file_path
        if full_path.exists():
            print_success(f"文档存在：{file_path}")
        else:
            print_error(f"文档缺失：{file_path}")
            all_passed = False
    
    return all_passed

def test_no_sensitive_data():
    """测试是否包含敏感数据"""
    print_header("测试 8: 敏感数据检?)
    
    sensitive_patterns = [
        "cherry",
        "tvly-dev-",
        "nvapi-",
        "7165f8ffad664d06bacf9be04b48e26",
        "sk-",
        "api_key",
        "secret"
    ]
    
    all_passed = True
    checked_files = 0
    
    for root, dirs, files in os.walk(SYMPHONY_PATH):
        # 跳过 __pycache__、backup 目录和测试文件本?        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'backup', '.git']]
        
        for file in files:
            # 跳过测试文件本身
            if file == 'test_all.py':
                continue
                
            if file.endswith(('.py', '.md', '.json', '.txt', '.yml', '.yaml')):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in sensitive_patterns:
                            if pattern.lower() in content.lower():
                                print_error(f"发现敏感数据 '{pattern}' 在：{file_path}")
                                all_passed = False
                    checked_files += 1
                except:
                    pass
    
    if all_passed:
        print_success(f"已检?{checked_files} 个文件，未发现敏感数?)
    
    return all_passed

def test_encoding():
    """测试所有Python文件编码是否为UTF-8无BOM"""
    print_header("测试 9: 文件编码验证")
    
    all_passed = True
    checked_files = 0
    
    for root, dirs, files in os.walk(SYMPHONY_PATH):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'backup', '.git']]
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                try:
                    # 检查BOM
                    with open(file_path, 'rb') as f:
                        first_bytes = f.read(3)
                        if first_bytes == b'\xef\xbb\xbf':
                            print_error(f"文件包含UTF-8 BOM：{file_path}")
                            all_passed = False
                            continue
                    
                    # 尝试用UTF-8读取
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read()
                    checked_files += 1
                except UnicodeDecodeError:
                    print_error(f"文件编码不是UTF-8：{file_path}")
                    all_passed = False
                except Exception as e:
                    print_error(f"无法读取文件 {file_path}：{str(e)}")
                    all_passed = False
    
    if all_passed:
        print_success(f"已检?{checked_files} 个Python文件，全部为UTF-8无BOM编码")
    
    return all_passed

def test_wisdom_engine_initialization():
    """测试智慧引擎初始化和动态脑群功?""
    print_header("测试 10: 智慧引擎与动态脑群验?)
    
    all_passed = True
    try:
        from Kernel.wisdom_engine import WisdomEngine, WisdomEmergenceEngine, BrainClusterManager, EmergenceConfig
        
        # 测试配置
        config = EmergenceConfig(
            min_brain_count=3,
            max_brain_count=10,
            auto_scale_threshold=0.6
        )
        
        # 测试集群管理?        cluster = BrainClusterManager(config)
        stats = cluster.get_cluster_stats()
        assert stats["total_brains"] == 3, f"初始脑数量应该为3，实际为{stats['total_brains']}"
        assert stats["min_brains"] == 3
        assert stats["max_brains"] == 10
        print_success("动态脑群管理器初始化成?)
        
        # 测试自动扩容
        # 模拟高负?        for _ in range(10):
            cluster.auto_scale()
        stats_after_scale = cluster.get_cluster_stats()
        print_info(f"扩容后脑数量：{stats_after_scale['total_brains']}")
        assert stats_after_scale["total_brains"] >= 3
        assert stats_after_scale["total_brains"] <= 10
        print_success("动态脑群自动扩缩容功能正常")
        
        # 测试智慧引擎初始?        engine = WisdomEngine()
        assert engine is not None
        assert hasattr(engine, "cluster_manager")
        assert hasattr(engine, "memory_brain")
        assert hasattr(engine, "military_advisor")
        print_success("智慧引擎初始化成?)
        
        # 测试任务处理
        result = engine.process_task("测试任务：优化系统响应速度")
        assert result["status"] == "dispatched"
        assert "task_id" in result
        assert "complexity" in result
        assert "strategy" in result
        assert "cluster_status" in result
        print_success("智慧引擎任务处理功能正常")
        
        # 测试军事战略顾问
        advice = engine.military_advisor.advise(
            scenario="我方兵力仅为对手三分之一，防守有利地?,
            goal="最小代价退?
        )
        assert advice is not None
        print_success("军事战略顾问模块加载正常")
        
        engine.shutdown()
        print_success("智慧引擎关闭正常")
        
    except Exception as e:
        print_error(f"智慧引擎测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    return all_passed

def test_swarm_algorithms():
    """测试群智能算?""
    print_header("测试 11: 群智能算法验?)
    
    all_passed = True
    try:
        from algorithms.ant_colony import ACO
        from algorithms.bee_colony import BeeColonyOptimizer
        
        # 测试蚁群算法
        aco = ACO(num_ants=10, num_iterations=5)
        assert aco is not None
        print_success("蚁群算法加载成功")
        
        # 测试蜂群算法
        bco = BeeColonyOptimizer(num_bees=10, num_iterations=5)
        assert bco is not None
        print_success("蜂群算法加载成功")
        
    except Exception as e:
        print_error(f"群智能算法测试失败：{str(e)}")
        all_passed = False
    
    return all_passed

def run_all_tests():
    """运行所有测?""
    print_header("Symphony Skills 整体测试套件")
    print_info(f"测试路径：{SYMPHONY_PATH}")
    
    tests = [
        ("目录结构", test_directory_structure),
        ("核心文件", test_core_files),
        ("模块导入", test_imports),
        ("进化模块", test_evolution_module),
        ("多Agent模块", test_multi_agent_module),
        ("配置文件", test_config_files),
        ("文档", test_documentation),
        ("敏感数据", test_no_sensitive_data),
        ("文件编码", test_encoding),
        ("智慧引擎与动态脑?, test_wisdom_engine_initialization),
        ("群智能算?, test_swarm_algorithms),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"测试 '{test_name}' 发生异常：{str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 打印总结
    print_header("测试总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: 通过")
        else:
            print_error(f"{test_name}: 失败")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print_success("SUCCESS: All tests passed! Symphony Skills is ready.")
        return True
    else:
        print_error(f"WARNING: {total - passed} tests failed. Please check.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

