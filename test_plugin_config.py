#!/usr/bin/env python3
"""
测试 learning_reviewer 插件配置
验证插件能正确加载和存储长期记忆数据
"""

import os
import sys
import json

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入插件核心函数
try:
    from plugin_core import call_plugin_func, set_plugin_directory
    print("[OK] Plugin core imported successfully")

    # 设置插件目录
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
    set_plugin_directory(plugin_dir)
    print(f"[OK] Plugin directory set to: {plugin_dir}")

    # 测试插件加载
    print("\n测试插件加载...")

    # 测试 1: 检查插件模块是否存在
    result = call_plugin_func("learning_reviewer", "get_card_stats", card_id="test123", detailed=True)
    if result is None:
        print("[OK] Plugin module loaded (返回 None 表示卡片不存在，这是正常的)")
    else:
        print(f"[OK] Plugin module loaded with result: {result}")

    # 测试 2: 测试插件函数
    print("\n测试插件函数...")

    # 配置数据目录
    knowledge_dir = "D:\\knowledge_bases"
    plugin_data_dir = os.path.join(knowledge_dir, ".data")
    os.makedirs(plugin_data_dir, exist_ok=True)
    print(f"[OK] Plugin data directory: {plugin_data_dir}")

    # 测试初始化卡片
    test_result = call_plugin_func(
        "learning_reviewer",
        "initialize_card",
        question="测试问题",
        answer="测试答案",
        data_dir=plugin_data_dir,
        detailed=True
    )

    if test_result and "card_id" in test_result:
        print(f"[OK] Card initialized successfully: {test_result['card_id']}")

        # 测试更新复习
        update_result = call_plugin_func(
            "learning_reviewer",
            "update_card_review",
            card_id=test_result["card_id"],
            success=True,
            data_dir=plugin_data_dir,
            detailed=True
        )

        if update_result and "success" in update_result:
            print(f"[OK] Card review updated: {update_result}")
        else:
            print("[ERROR] Failed to update card review")
    else:
        print("[ERROR] Failed to initialize card")

except ImportError as e:
    print(f"[ERROR] Failed to import plugin core: {e}")
except Exception as e:
    print(f"[ERROR] Error during plugin test: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成！")