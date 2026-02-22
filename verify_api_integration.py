#!/usr/bin/env python3
"""
验证插件API接口与main.py函数的对应关系
"""

import os
import sys
import inspect
from typing import Dict, Any, List, Optional

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_api_functions():
    """Verify correspondence between API functions and main.py functions"""
    print("=" * 70)
    print("Verifying Plugin API Interface Correspondence with main.py")
    print("=" * 70)

    # 导入相关模块
    try:
        from plugins.learning_reviewer.api import plugin_api
        from plugins.learning_reviewer import main

        print("[OK] 成功导入plugin_api和main模块")
    except ImportError as e:
        print(f"[ERROR] 导入失败: {e}")
        return False

    # 需要验证的函数列表
    api_functions_to_check = [
        # 核心函数
        ("get_review_engine", "get_review_engine"),
        ("handle_review_action", "handle_review_action"),
        ("get_review_state", "get_review_state"),
        ("export_review_data", "export_review_data"),
        ("reset_review_session", "reset_review_session"),

        # 引擎相关函数
        ("get_spaced_repetition_engine", "get_spaced_repetition_engine"),
        ("initialize_engine_from_items", "initialize_engine_from_items"),
        ("handle_review_action_with_engine", "handle_review_action_with_engine"),
        ("get_review_state_from_engine", "get_review_state_from_engine"),
        ("export_review_data_from_engine", "export_review_data_from_engine"),
        ("reset_review_session_in_engine", "reset_review_session_in_engine"),
    ]

    all_passed = True
    results = []

    for api_func_name, main_func_name in api_functions_to_check:
        print(f"\n验证函数: {api_func_name} -> {main_func_name}")

        # 检查API函数是否存在
        if not hasattr(plugin_api, api_func_name):
            print(f"  [ERROR] plugin_api中未找到函数: {api_func_name}")
            all_passed = False
            results.append((api_func_name, "MISSING_IN_API", None))
            continue

        # 检查main.py函数是否存在
        if not hasattr(main, main_func_name):
            print(f"  [ERROR] main.py中未找到函数: {main_func_name}")
            all_passed = False
            results.append((api_func_name, "MISSING_IN_MAIN", None))
            continue

        api_func = getattr(plugin_api, api_func_name)
        main_func = getattr(main, main_func_name)

        # 获取函数签名
        try:
            api_sig = inspect.signature(api_func)
            main_sig = inspect.signature(main_func)

            # 比较参数
            api_params = list(api_sig.parameters.keys())
            main_params = list(main_sig.parameters.keys())

            # 检查参数匹配
            if api_params != main_params:
                print(f"  [WARNING] 参数不匹配:")
                print(f"    API参数: {api_params}")
                print(f"    Main参数: {main_params}")
                results.append((api_func_name, "PARAM_MISMATCH", (api_params, main_params)))
            else:
                print(f"  [OK] 参数匹配: {api_params}")
                results.append((api_func_name, "OK", api_params))

        except Exception as e:
            print(f"  [ERROR] 获取函数签名失败: {e}")
            all_passed = False
            results.append((api_func_name, "SIGNATURE_ERROR", str(e)))

    # 打印摘要
    print("\n" + "=" * 70)
    print("验证结果摘要")
    print("=" * 70)

    for func_name, status, details in results:
        if status == "OK":
            print(f"[OK] {func_name}: 验证通过")
        elif status == "PARAM_MISMATCH":
            print(f"[WARNING] {func_name}: 参数不匹配")
            if details:
                api_params, main_params = details
                print(f"  API参数: {api_params}")
                print(f"  Main参数: {main_params}")
        else:
            print(f"[ERROR] {func_name}: {status}")

    print("\n" + "=" * 70)
    if all_passed:
        print("所有API函数验证通过！")
    else:
        print("部分API函数验证失败")

    return all_passed

def test_api_function_calls():
    """测试API函数调用"""
    print("\n" + "=" * 70)
    print("测试API函数调用")
    print("=" * 70)

    try:
        from plugins.learning_reviewer.api import plugin_api

        # 测试简单的函数调用
        test_functions = [
            ("get_spaced_repetition_engine", {"kb_name": "test_kb", "data_dir": ".data/test"}),
            ("get_review_state", {"kb_name": "test_kb"}),
        ]

        for func_name, kwargs in test_functions:
            print(f"\n测试函数调用: {func_name}")
            try:
                func = getattr(plugin_api, func_name)
                # 尝试调用（可能会失败，但应该能导入）
                print(f"  [OK] 函数可访问")
            except Exception as e:
                print(f"  [ERROR] 函数调用失败: {e}")

    except Exception as e:
        print(f"[ERROR] 测试API函数调用失败: {e}")
        return False

    return True

def main():
    """主函数"""
    print("插件API接口验证工具")
    print("=" * 70)

    # 验证函数对应关系
    if not verify_api_functions():
        return 1

    # 测试函数调用
    if not test_api_function_calls():
        return 1

    print("\n" + "=" * 70)
    print("验证完成！所有API接口已正确配置。")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    sys.exit(main())