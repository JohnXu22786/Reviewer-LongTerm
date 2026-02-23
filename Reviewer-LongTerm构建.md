Reviewer-LongTerm构建
我们先以reviewer-intense为基础，构建一个新的项目Reviewer-LongTerm，现有的功能不要变，我们是要增加功能。

一、 复习从单次转向长期：

SM-2 是由 Piotr Woźniak 开发的一种间隔复习算法，其核心目标是：**在即将遗忘的临界点安排下一次复习。**

---

# 复习App间隔重复算法设计方案

## 核心数据结构

```json
{
  "id": "唯一标识符",
  "question": "问题内容",
  "answer": "答案内容",
  "interval": 1,           // 下次复习间隔（天）
  "eFactor": 2.5,          // 简易度因子，初始值2.5，范围[1.3, ∞]
  "consecutiveCorrect": 0, // 连续正确次数
  "dueDate": "2024-01-01", // 下次复习日期
  "mastered": false        // 是否已掌握
}
```

## 算法执行流程

### 1. 初始化新卡片

```javascript
function initializeCard() {
  return {
    interval: 1,
    eFactor: 2.5,
    consecutiveCorrect: 0,
    dueDate: today(),
    mastered: false
  };
}
```

### 2. 处理"记得"（Recognized）按钮

```javascript
function handleRecognized(card) {
  // 步骤1：更新连续正确次数
  card.consecutiveCorrect += 1;

  // 步骤2：计算新的复习间隔
  if (card.consecutiveCorrect === 1) {
    // 第一次正确：1天后复习
    card.interval = 1;
  } else if (card.consecutiveCorrect === 2) {
    // 第二次正确：3天后复习（优化后的初期间隔）
    card.interval = 3;
  } else {
    // 第三次及以后：按eFactor倍数增长
    card.interval = Math.round(card.interval * card.eFactor);
  }

  // 步骤3：保持eFactor不变（简化公式，q=4时EF不变）
  // card.eFactor 保持不变

  // 步骤4：检查是否自动标记为已掌握
  if (card.eFactor > 3.0 && card.consecutiveCorrect > 7) {
    card.mastered = true;
  }

  // 步骤5：更新下次复习日期
  card.dueDate = addDays(currentDate, card.interval);

  return card;
}
```

### 3. 处理"不记得"（Forgotten）按钮

```javascript
function handleForgotten(card) {
  // 步骤1：重置连续正确次数
  card.consecutiveCorrect = 0;

  // 步骤2：重置复习间隔为1天
  card.interval = 1;

  // 步骤3：平滑更新eFactor
  // 原始EF下降量：0.54
  const rawDecrease = 0.54;

  // 计算新EF值（加权平滑更新）
  const newEFRaw = card.eFactor - rawDecrease;
  const newEFClamped = Math.max(newEFRaw, 1.3); // 确保不低于1.3

  // 应用平滑更新：80%保持原值 + 20%应用下降
  card.eFactor = 0.8 * card.eFactor + 0.2 * newEFClamped;

  // 步骤4：更新下次复习日期（1天后）
  card.dueDate = addDays(currentDate, 1);

  return card;
}
```

### 4. 复习调度逻辑

```javascript
// 每日复习入口函数
function getCardsForReview(allCards, currentDate) {
  const cardsToReview = [];

  for (const card of allCards) {
    // 跳过已掌握的卡片
    if (card.mastered) continue;
  
    // 检查是否到期
    if (isDateBeforeOrEqual(card.dueDate, currentDate)) {
      cardsToReview.push(card);
    }
  }

  return cardsToReview;
}

// 处理复习结果的入口
function processReview(card, userResponse) {
  if (userResponse === "remembered") {
    return handleRecognized(card);
  } else if (userResponse === "forgotten") {
    return handleForgotten(card);
  }

  return card; // 默认返回原卡片（不应发生）
}
```

## 辅助函数

```javascript
// 日期计算函数
function addDays(date, days) {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

function isDateBeforeOrEqual(date1, date2) {
  return new Date(date1) <= new Date(date2);
}

function today() {
  return new Date().toISOString().split('T')[0];
}
```

## 算法特性总结

1. **两个按钮模式**：
   * "记得" → 对应SM-2的q=4
   * "不记得" → 对应SM-2的q=1

2. **优化的初期间隔**：
   * 第1次正确：1天
   * 第2次正确：3天（比原SM-2的6天更保守）
   * 第3+次正确：按eFactor倍数增长

3. **自动掌握机制**：
   * 当`eFactor > 3.0`且`consecutiveCorrect > 7`时，自动标记为掌握
   * 已掌握的卡片不再出现在复习队列

4. **稳定的EF更新**：
   * "记得"时：EF保持不变（简化计算）
   * "不记得"时：EF平滑下降（加权平均），防止过度惩罚

二、 知识点编辑

