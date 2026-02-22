#!/usr/bin/env python3
"""
测试插件迁移后的功能完整性

验证目标：
1. 插件系统基础功能正常
2. learning_reviewer插件功能正常
3. 插件与路由集成正常
4. 数据持久化正常
5. 降级行为正常
"""

import os
import sys
import json
import tempfile
import shutil

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入插件系统
from plugin_core import call_plugin_func, set_plugin_directory, get_plugin_directory

def test_plugin_system_basics():
    """测试插件系统基础功能"""
    print("=" * 60)
    print("Testing Plugin System Basics")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # 测试1: 插件目录设置
    tests_total += 1
    try:
        original_dir = get_plugin_directory()
        print(f"1. Original plugin directory: {original_dir}")

        # 创建临时插件目录
        temp_dir = tempfile.mkdtemp()
        set_plugin_directory(temp_dir)
        new_dir = get_plugin_directory()

        if os.path.abspath(new_dir) == os.path.abspath(temp_dir):
            print("   [OK] Plugin directory set successfully")
            tests_passed += 1
        else:
            print(f"   [ERROR] Plugin directory set failed: {new_dir}")

        # 恢复原始目录
        set_plugin_directory(original_dir)
    except Exception as e:
        print(f"   [ERROR] Plugin directory test failed: {e}")

    # 测试2: 插件函数调用
    tests_total += 1
    try:
        # 使用现有的learning_reviewer插件
        result = call_plugin_func(
            "learning_reviewer",
            "update_review",
            kb_name="test_migration.json",
            card_id="test_card_migration",
            is_correct=True,
            data_dir=tempfile.gettempdir()
        )

        if result and result.get("success"):
            print(f"2. [OK] 插件函数调用成功: {result.get('card_id')}")
            tests_passed += 1
        else:
            print(f"2. [ERROR] 插件函数调用失败: {result}")
    except Exception as e:
        print(f"2. [ERROR] 插件函数调用测试失败: {e}")

    # 测试3: 降级行为
    tests_total += 1
    try:
        # 调用不存在的插件
        result = call_plugin_func(
            "non_existent_plugin",
            "non_existent_function"
        )

        if result is None:
            print("3. [OK] 降级行为正常（不存在的插件返回None）")
            tests_passed += 1
        else:
            print(f"3. [ERROR] 降级行为异常: {result}")
    except Exception as e:
        print(f"3. [ERROR] 降级行为测试失败: {e}")

    print(f"\n基础功能测试结果: {tests_passed}/{tests_total} 通过")
    return tests_passed == tests_total

def test_learning_reviewer_plugin():
    """测试learning_reviewer插件功能"""
    print("\n" + "=" * 60)
    print("测试learning_reviewer插件功能")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # 创建临时数据目录
    temp_data_dir = tempfile.mkdtemp()

    try:
        # 测试1: update_review函数
        tests_total += 1
        result = call_plugin_func(
            "learning_reviewer",
            "update_review",
            kb_name="test_kb.json",
            card_id="card_001",
            is_correct=True,
            data_dir=temp_data_dir
        )

        if result and result.get("success"):
            print(f"1. [OK] update_review成功: {result}")
            tests_passed += 1
        else:
            print(f"1. [ERROR] update_review失败: {result}")

        # 测试2: handle_remember_action函数
        tests_total += 1
        result = call_plugin_func(
            "learning_reviewer",
            "handle_remember_action",
            kb_name="test_kb.json",
            card_id="card_002",
            data_dir=temp_data_dir
        )

        if result and result.get("success"):
            print(f"2. [OK] handle_remember_action成功: {result}")
            tests_passed += 1
        else:
            print(f"2. [ERROR] handle_remember_action失败: {result}")

        # 测试3: handle_forget_action函数
        tests_total += 1
        result = call_plugin_func(
            "learning_reviewer",
            "handle_forget_action",
            kb_name="test_kb.json",
            card_id="card_003",
            data_dir=temp_data_dir
        )

        if result and result.get("success"):
            print(f"3. [OK] handle_forget_action成功: {result}")
            tests_passed += 1
        else:
            print(f"3. [ERROR] handle_forget_action失败: {result}")

        # 测试4: get_statistics函数
        tests_total += 1
        result = call_plugin_func(
            "learning_reviewer",
            "get_statistics",
            kb_name="test_kb.json",
            data_dir=temp_data_dir
        )

        if result and result.get("success"):
            print(f"4. [OK] get_statistics成功: {result}")
            tests_passed += 1
        else:
            print(f"4. [ERROR] get_statistics失败: {result}")

        # 测试5: 数据持久化
        tests_total += 1
        data_file = os.path.join(temp_data_dir, "test_kb_longterm.json")
        if os.path.exists(data_file):
            print(f"5. [OK] 数据文件已创建: {data_file}")

            # 验证文件内容
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "cards" in data and len(data["cards"]) >= 3:
                print(f"   [OK] 数据文件包含 {len(data['cards'])} 张卡片")
                tests_passed += 1
            else:
                print(f"   [ERROR] 数据文件格式不正确")
        else:
            print(f"5. [ERROR] 数据文件未创建")

    except Exception as e:
        print(f"插件功能测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理临时目录
        if os.path.exists(temp_data_dir):
            shutil.rmtree(temp_data_dir)

    print(f"\n插件功能测试结果: {tests_passed}/{tests_total} 通过")
    return tests_passed == tests_total

def test_plugin_integration_with_routes():
    """测试插件与路由集成"""
    print("\n" + "=" * 60)
    print("测试插件与路由集成")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    try:
        # 导入路由模块
        from app.routes.review import PLUGIN_AVAILABLE, call_plugin_func as route_plugin_func

        # 测试1: 插件可用性检测
        tests_total += 1
        if PLUGIN_AVAILABLE:
            print("1. [OK] 路由检测到插件可用")
            tests_passed += 1
        else:
            print("1. [ERROR] 路由未检测到插件可用")

        # 测试2: 插件函数调用兼容性
        tests_total += 1
        try:
            # 模拟路由中的插件调用
            result = call_plugin_func(
                "learning_reviewer",
                "update_review",
                kb_name="integration_test.json",
                card_id="integration_card",
                is_correct=True,
                data_dir=tempfile.gettempdir()
            )

            if result:
                print("2. [OK] 路由兼容的插件调用成功")
                tests_passed += 1
            else:
                print("2. [ERROR] 路由兼容的插件调用失败")
        except Exception as e:
            print(f"2. [ERROR] 路由兼容的插件调用异常: {e}")

    except Exception as e:
        print(f"路由集成测试失败: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n路由集成测试结果: {tests_passed}/{tests_total} 通过")
    return tests_passed == tests_total

def test_cross_project_compatibility():
    """测试跨项目兼容性"""
    print("\n" + "=" * 60)
    print("测试跨项目兼容性")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # 测试核心复习流程兼容性
    test_cases = [
        {
            "name": "正确回答流程",
            "kb_name": "compat_test.json",
            "card_id": "compat_correct",
            "is_correct": True,
            "expected_fields": ["success", "card_id", "is_correct", "total_reviews", "interval", "due_date"]
        },
        {
            "name": "错误回答流程",
            "kb_name": "compat_test.json",
            "card_id": "compat_incorrect",
            "is_correct": False,
            "expected_fields": ["success", "card_id", "is_correct", "total_reviews", "interval", "due_date"]
        }
    ]

    temp_data_dir = tempfile.mkdtemp()

    try:
        for i, test_case in enumerate(test_cases, 1):
            tests_total += 1

            result = call_plugin_func(
                "learning_reviewer",
                "update_review",
                kb_name=test_case["kb_name"],
                card_id=test_case["card_id"],
                is_correct=test_case["is_correct"],
                data_dir=temp_data_dir
            )

            if result and result.get("success"):
                # 检查返回字段
                missing_fields = []
                for field in test_case["expected_fields"]:
                    if field not in result:
                        missing_fields.append(field)

                if not missing_fields:
                    print(f"{i}. [OK] {test_case['name']}: 所有必需字段存在")
                    tests_passed += 1
                else:
                    print(f"{i}. [ERROR] {test_case['name']}: 缺少字段 {missing_fields}")
            else:
                print(f"{i}. [ERROR] {test_case['name']}: 调用失败")

    except Exception as e:
        print(f"跨项目兼容性测试失败: {e}")

    finally:
        if os.path.exists(temp_data_dir):
            shutil.rmtree(temp_data_dir)

    print(f"\n跨项目兼容性测试结果: {tests_passed}/{tests_total} 通过")
    return tests_passed == tests_total

def main():
    """Main test function"""
    print("Plugin Migration Functionality Test")
    print("=" * 60)

    all_passed = True

    # Run all tests
    if not test_plugin_system_basics():
        all_passed = False

    if not test_learning_reviewer_plugin():
        all_passed = False

    if not test_plugin_integration_with_routes():
        all_passed = False

    if not test_cross_project_compatibility():
        all_passed = False

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    if all_passed:
        print("[OK] All tests passed! Plugin migration is complete.")
        return 0
    else:
        print("[ERROR] Some tests failed, need to check plugin migration.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)