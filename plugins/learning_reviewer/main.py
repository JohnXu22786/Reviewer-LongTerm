"""
learning_reviewer_api 插件主模块
基于间隔重复算法（SM-2变体）的学习复习插件
"""

import os
import json
import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from pathlib import Path
import hashlib


@dataclass
class CardData:
    """卡片数据（长期记忆存储）"""
    card_id: str
    question: str
    answer: str
    interval: int = 1  # 下次复习间隔（天）
    e_factor: float = 2.5  # 简易度因子，初始值2.5
    consecutive_correct: int = 0  # 连续正确次数
    due_date: str = ""  # 下次复习日期（YYYY-MM-DD）
    mastered: bool = False  # 是否已掌握
    last_reviewed: str = ""  # 最后复习日期
    total_reviews: int = 0  # 总复习次数
    correct_reviews: int = 0  # 正确复习次数
    created_date: str = ""  # 创建日期


@dataclass
class ReviewResult:
    """复习结果"""
    card_id: str
    success: bool
    new_interval: int
    new_e_factor: float
    new_due_date: str
    mastered: bool
    message: str


class LearningReviewer:
    """学习复习器"""

    def __init__(self, data_dir: str = ".data"):
        """
        初始化学习复习器

        Args:
            data_dir: 数据目录路径
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 默认配置
        self.default_e_factor = 2.5
        self.min_e_factor = 1.3
        self.max_interval = 365
        self.auto_master_threshold = 3.0
        self.auto_master_consecutive = 7

        # 加载配置
        self._load_config()

    def _load_config(self):
        """加载配置"""
        config_file = self.data_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.default_e_factor = config.get("default_e_factor", 2.5)
                    self.min_e_factor = config.get("min_e_factor", 1.3)
                    self.max_interval = config.get("max_interval", 365)
                    self.auto_master_threshold = config.get("auto_master_threshold", 3.0)
                    self.auto_master_consecutive = config.get("auto_master_consecutive", 7)
            except Exception as e:
                print(f"加载配置失败: {e}")

    def _save_config(self):
        """保存配置"""
        config_file = self.data_dir / "config.json"
        config = {
            "default_e_factor": self.default_e_factor,
            "min_e_factor": self.min_e_factor,
            "max_interval": self.max_interval,
            "auto_master_threshold": self.auto_master_threshold,
            "auto_master_consecutive": self.auto_master_consecutive
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _get_card_file_path(self, card_id: str) -> Path:
        """
        获取卡片数据文件路径

        Args:
            card_id: 卡片ID

        Returns:
            Path: 文件路径
        """
        # 使用卡片ID的前2个字符作为子目录
        subdir = card_id[:2] if len(card_id) >= 2 else "00"
        card_dir = self.data_dir / "cards" / subdir
        card_dir.mkdir(parents=True, exist_ok=True)
        return card_dir / f"{card_id}.json"

    def _generate_card_id(self, question: str, answer: str) -> str:
        """
        生成卡片ID

        Args:
            question: 问题
            answer: 答案

        Returns:
            str: 卡片ID
        """
        content = f"{question}|{answer}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _get_today_str(self) -> str:
        """
        获取今天日期字符串

        Returns:
            str: 日期字符串（YYYY-MM-DD）
        """
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def _add_days(self, date_str: str, days: int) -> str:
        """
        日期加天数

        Args:
            date_str: 日期字符串（YYYY-MM-DD）
            days: 天数

        Returns:
            str: 新的日期字符串
        """
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            new_date = date + datetime.timedelta(days=days)
            return new_date.strftime("%Y-%m-%d")
        except ValueError:
            # 如果日期格式错误，从今天开始计算
            today = datetime.datetime.now()
            new_date = today + datetime.timedelta(days=days)
            return new_date.strftime("%Y-%m-%d")

    def initialize_card(self, question: str, answer: str, **kwargs) -> Dict[str, Any]:
        """
        初始化新卡片

        Args:
            question: 问题内容
            answer: 答案内容
            **kwargs: 其他参数
                - card_id: 自定义卡片ID（可选）
                - interval: 初始间隔（默认1）
                - e_factor: 初始简易度因子（默认2.5）

        Returns:
            Dict[str, Any]: 卡片数据
        """
        # 生成或使用提供的卡片ID
        card_id = kwargs.get("card_id") or self._generate_card_id(question, answer)

        # 创建卡片数据
        today = self._get_today_str()
        card_data = CardData(
            card_id=card_id,
            question=question,
            answer=answer,
            interval=kwargs.get("interval", 1),
            e_factor=kwargs.get("e_factor", self.default_e_factor),
            consecutive_correct=0,
            due_date=today,  # 新卡片立即需要复习
            mastered=False,
            last_reviewed="",
            total_reviews=0,
            correct_reviews=0,
            created_date=today
        )

        # 保存卡片数据
        self._save_card_data(card_data)

        return asdict(card_data)

    def _save_card_data(self, card_data: CardData):
        """
        保存卡片数据

        Args:
            card_data: 卡片数据
        """
        card_file = self._get_card_file_path(card_data.card_id)
        with open(card_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(card_data), f, indent=2, ensure_ascii=False)

    def _load_card_data(self, card_id: str) -> Optional[CardData]:
        """
        加载卡片数据

        Args:
            card_id: 卡片ID

        Returns:
            Optional[CardData]: 卡片数据，如果不存在则返回None
        """
        card_file = self._get_card_file_path(card_id)
        if not card_file.exists():
            return None

        try:
            with open(card_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return CardData(**data)
        except Exception as e:
            print(f"加载卡片数据失败 {card_id}: {e}")
            return None

    def update_card_review(self, card_id: str, success: bool, review_date: str = None) -> Dict[str, Any]:
        """
        更新卡片复习结果

        Args:
            card_id: 卡片ID
            success: 是否回答正确
            review_date: 复习日期（默认今天）

        Returns:
            Dict[str, Any]: 复习结果
        """
        # 加载卡片数据
        card_data = self._load_card_data(card_id)
        if not card_data:
            return {
                "error": f"卡片不存在: {card_id}",
                "success": False
            }

        # 设置复习日期
        today = review_date or self._get_today_str()

        # 更新复习统计
        card_data.total_reviews += 1
        if success:
            card_data.correct_reviews += 1
            card_data.consecutive_correct += 1
        else:
            card_data.consecutive_correct = 0

        # 更新间隔和简易度因子
        if success:
            # 处理"记得"的情况
            if card_data.consecutive_correct == 1:
                # 第一次正确：1天后复习
                card_data.interval = 1
            elif card_data.consecutive_correct == 2:
                # 第二次正确：3天后复习
                card_data.interval = 3
            else:
                # 第三次及以后：按eFactor倍数增长
                card_data.interval = min(
                    int(card_data.interval * card_data.e_factor),
                    self.max_interval
                )

            # eFactor保持不变（简化公式）
            # card_data.e_factor 保持不变
        else:
            # 处理"不记得"的情况
            card_data.interval = 1

            # 平滑更新eFactor
            raw_decrease = 0.54
            new_ef_raw = card_data.e_factor - raw_decrease
            new_ef_clamped = max(new_ef_raw, self.min_e_factor)

            # 应用平滑更新：80%保持原值 + 20%应用下降
            card_data.e_factor = 0.8 * card_data.e_factor + 0.2 * new_ef_clamped

        # 检查是否自动标记为已掌握
        if (card_data.e_factor > self.auto_master_threshold and
            card_data.consecutive_correct > self.auto_master_consecutive):
            card_data.mastered = True

        # 更新下次复习日期
        card_data.due_date = self._add_days(today, card_data.interval)
        card_data.last_reviewed = today

        # 保存更新后的数据
        self._save_card_data(card_data)

        # 返回复习结果
        result = ReviewResult(
            card_id=card_id,
            success=success,
            new_interval=card_data.interval,
            new_e_factor=card_data.e_factor,
            new_due_date=card_data.due_date,
            mastered=card_data.mastered,
            message="复习成功" if success else "需要重新学习"
        )

        return asdict(result)

    def get_due_cards(self, date: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取到期的卡片

        Args:
            date: 检查日期（默认今天）
            limit: 最大返回数量

        Returns:
            List[Dict[str, Any]]: 到期卡片列表
        """
        check_date = date or self._get_today_str()
        due_cards = []

        # 遍历所有卡片文件
        cards_dir = self.data_dir / "cards"
        if not cards_dir.exists():
            return due_cards

        for subdir in cards_dir.iterdir():
            if subdir.is_dir():
                for card_file in subdir.glob("*.json"):
                    try:
                        with open(card_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            card_data = CardData(**data)

                            # 跳过已掌握的卡片
                            if card_data.mastered:
                                continue

                            # 检查是否到期
                            if card_data.due_date <= check_date:
                                due_cards.append(asdict(card_data))

                                # 达到限制数量则停止
                                if len(due_cards) >= limit:
                                    return due_cards
                    except Exception as e:
                        print(f"读取卡片文件失败 {card_file}: {e}")

        return due_cards

    def calculate_next_review_date(self, card_id: str, success: bool) -> Dict[str, Any]:
        """
        计算下次复习日期（不实际更新卡片）

        Args:
            card_id: 卡片ID
            success: 是否回答正确

        Returns:
            Dict[str, Any]: 计算结果
        """
        # 加载卡片数据
        card_data = self._load_card_data(card_id)
        if not card_data:
            return {
                "error": f"卡片不存在: {card_id}",
                "success": False
            }

        today = self._get_today_str()

        # 模拟计算
        if success:
            if card_data.consecutive_correct + 1 == 1:
                new_interval = 1
            elif card_data.consecutive_correct + 1 == 2:
                new_interval = 3
            else:
                new_interval = min(
                    int(card_data.interval * card_data.e_factor),
                    self.max_interval
                )
            new_e_factor = card_data.e_factor  # 保持不变
        else:
            new_interval = 1
            # 模拟eFactor下降
            raw_decrease = 0.54
            new_ef_raw = card_data.e_factor - raw_decrease
            new_ef_clamped = max(new_ef_raw, self.min_e_factor)
            new_e_factor = 0.8 * card_data.e_factor + 0.2 * new_ef_clamped

        new_due_date = self._add_days(today, new_interval)

        return {
            "card_id": card_id,
            "current_interval": card_data.interval,
            "current_e_factor": card_data.e_factor,
            "current_due_date": card_data.due_date,
            "new_interval": new_interval,
            "new_e_factor": new_e_factor,
            "new_due_date": new_due_date,
            "days_until_review": new_interval
        }

    def get_card_stats(self, card_id: str) -> Dict[str, Any]:
        """
        获取卡片统计信息

        Args:
            card_id: 卡片ID

        Returns:
            Dict[str, Any]: 卡片统计信息
        """
        # 加载卡片数据
        card_data = self._load_card_data(card_id)
        if not card_data:
            return {
                "error": f"卡片不存在: {card_id}",
                "success": False
            }

        # 计算正确率
        accuracy = 0
        if card_data.total_reviews > 0:
            accuracy = card_data.correct_reviews / card_data.total_reviews * 100

        # 计算距离下次复习的天数
        today = self._get_today_str()
        try:
            due_date = datetime.datetime.strptime(card_data.due_date, "%Y-%m-%d")
            today_date = datetime.datetime.strptime(today, "%Y-%m-%d")
            days_until_review = max(0, (due_date - today_date).days)
        except ValueError:
            days_until_review = 0

        return {
            "card_id": card_id,
            "question": card_data.question,
            "total_reviews": card_data.total_reviews,
            "correct_reviews": card_data.correct_reviews,
            "accuracy": round(accuracy, 2),
            "consecutive_correct": card_data.consecutive_correct,
            "interval": card_data.interval,
            "e_factor": round(card_data.e_factor, 2),
            "due_date": card_data.due_date,
            "days_until_review": days_until_review,
            "mastered": card_data.mastered,
            "last_reviewed": card_data.last_reviewed,
            "created_date": card_data.created_date
        }


# 全局实例
_reviewer_instance: Optional[LearningReviewer] = None


def get_reviewer(data_dir: str = ".data") -> LearningReviewer:
    """
    获取学习复习器实例

    Args:
        data_dir: 数据目录路径

    Returns:
        LearningReviewer: 学习复习器实例
    """
    global _reviewer_instance
    if _reviewer_instance is None:
        _reviewer_instance = LearningReviewer(data_dir)
    return _reviewer_instance


# 插件函数接口
def initialize_card(question: str, answer: str, **kwargs) -> Dict[str, Any]:
    """
    初始化新卡片

    Args:
        question: 问题内容
        answer: 答案内容
        **kwargs: 其他参数

    Returns:
        Dict[str, Any]: 卡片数据
    """
    reviewer = get_reviewer()
    return reviewer.initialize_card(question, answer, **kwargs)


def update_card_review(card_id: str, success: bool, review_date: str = None) -> Dict[str, Any]:
    """
    更新卡片复习结果

    Args:
        card_id: 卡片ID
        success: 是否回答正确
        review_date: 复习日期

    Returns:
        Dict[str, Any]: 复习结果
    """
    reviewer = get_reviewer()
    return reviewer.update_card_review(card_id, success, review_date)


def get_due_cards(date: str = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    获取到期的卡片

    Args:
        date: 检查日期
        limit: 最大返回数量

    Returns:
        List[Dict[str, Any]]: 到期卡片列表
    """
    reviewer = get_reviewer()
    return reviewer.get_due_cards(date, limit)


def calculate_next_review_date(card_id: str, success: bool) -> Dict[str, Any]:
    """
    计算下次复习日期

    Args:
        card_id: 卡片ID
        success: 是否回答正确

    Returns:
        Dict[str, Any]: 计算结果
    """
    reviewer = get_reviewer()
    return reviewer.calculate_next_review_date(card_id, success)


def get_card_stats(card_id: str) -> Dict[str, Any]:
    """
    获取卡片统计信息

    Args:
        card_id: 卡片ID

    Returns:
        Dict[str, Any]: 卡片统计信息
    """
    reviewer = get_reviewer()
    return reviewer.get_card_stats(card_id)


if __name__ == "__main__":
    # 测试代码
    print("learning_reviewer 插件测试")

    # 创建学习复习器
    reviewer = LearningReviewer(".data/test")

    # 初始化卡片
    card = reviewer.initialize_card(
        question="什么是Python？",
        answer="Python是一种高级编程语言。"
    )
    print(f"初始化卡片: {card['card_id']}")

    # 更新复习结果（正确）
    result = reviewer.update_card_review(card['card_id'], success=True)
    print(f"复习结果（正确）: {result}")

    # 获取卡片统计
    stats = reviewer.get_card_stats(card['card_id'])
    print(f"卡片统计: {stats}")

    # 获取到期卡片
    due_cards = reviewer.get_due_cards()
    print(f"到期卡片数量: {len(due_cards)}")