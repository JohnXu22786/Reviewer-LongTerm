#!/usr/bin/env python3
"""
测试插件系统集成
"""

import os
import sys
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_plugin_import():
    """Test plugin import"""
    print("=== Testing Plugin System Import ===")

    try:
        from plugin_core import call_plugin_func
        print("✓ call_plugin_func 导入成功")

        # 测试调用一个不存在的插件
        result = call_plugin_func("test_module", "test_function")
        print(f"测试调用结果: {result}")

        return True
    except ImportError as e:
        print(f"✗ 插件导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 其他错误: {e}")
        return False

def test_review_logic():
    """测试复习逻辑"""
    print("\n=== 测试复习逻辑 ===")

    try:
        from app.algorithms.spaced_repetition import SpacedRepetitionEngine, ItemState

        # 创建测试项目
        items = [
            {"id": "test1", "question": "测试问题1", "answer": "测试答案1"},
            {"id": "test2", "question": "测试问题2", "answer": "测试答案2"},
            {"id": "test3", "question": "测试问题3", "answer": "测试答案3"}
        ]

        # 初始化引擎
        engine = SpacedRepetitionEngine()
        engine.initialize_from_items(items)

        print(f"✓ 引擎初始化成功")
        print(f"  总项目数: {engine.total_items_count}")
        print(f"  动态序列长度: {len(engine.dynamic_sequence)}")

        # 测试复习动作
        if engine.dynamic_sequence:
            first_item = engine.dynamic_sequence[0]
            result = engine.handle_review_action(first_item, "recognized")
            print(f"✓ 复习动作处理成功")
            print(f"  动作: {result['action_processed']}")
            print(f"  掌握项目数: {engine.mastered_items_count}")

        return True
    except Exception as e:
        print(f"✗ 复习逻辑测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")

    try:
        # 创建测试应用
        from app import create_app
        app = create_app()

        print("✓ Flask应用创建成功")

        # 测试应用配置
        with app.app_context():
            knowledge_dir = app.config.get('KNOWLEDGE_DIR')
            print(f"  知识库目录: {knowledge_dir}")

            # 检查测试知识库文件
            test_file = os.path.join(knowledge_dir, "test_knowledge.json")
            if os.path.exists(test_file):
                print(f"✓ 测试知识库文件存在: {test_file}")

                # 读取文件内容
                with open(test_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"  文件包含 {len(data)} 个项目")
            else:
                print(f"✗ 测试知识库文件不存在: {test_file}")

        return True
    except Exception as e:
        print(f"✗ API端点测试失败: {e}")
        return False

def test_plugin_integration():
    """测试插件集成"""
    print("\n=== 测试插件集成 ===")

    try:
        # 导入 review.py 中的函数
        from app.routes.review import get_review_engine

        print("✓ review模块导入成功")

        # 测试插件可用性检查
        from app.routes.review import PLUGIN_AVAILABLE
        print(f"  插件可用性: {PLUGIN_AVAILABLE}")

        if PLUGIN_AVAILABLE:
            print("✓ 插件系统可用")

            # 测试插件目录配置
            from plugin_core import get_plugin_directory
            plugin_dir = get_plugin_directory()
            print(f"  插件目录: {plugin_dir}")

            if os.path.exists(plugin_dir):
                print(f"✓ 插件目录存在")

                # 列出插件目录内容
                plugins = [f for f in os.listdir(plugin_dir) if f.endswith('.py') and f != '__init__.py']
                print(f"  找到 {len(plugins)} 个插件文件")
                for plugin in plugins:
                    print(f"    - {plugin}")
            else:
                print(f"✗ 插件目录不存在: {plugin_dir}")
        else:
            print("⚠ 插件系统不可用")

        return True
    except Exception as e:
        print(f"✗ 插件集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("Testing Reviewer-LongTerm Plugin Integration")
    print("=" * 50)

    tests = [
        ("插件导入", test_plugin_import),
        ("复习逻辑", test_review_logic),
        ("API端点", test_api_endpoints),
        ("插件集成", test_plugin_integration)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("-" * 30)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1

    print("-" * 30)
    print(f"总计: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过!")
        return 0
    else:
        print("⚠ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())