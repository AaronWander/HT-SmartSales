# 客户专属穿搭方案

说明：

- 这是一个可直接渲染的 Markdown 模板（已移除多余转义和错误代码块）。
- 占位符建议用 Hermes 方案模板约定：`{{slot:...}}` / `{{sys:...}}` / `{{rag:...}}` / `{{ai:...}}` / `{{ext:...}}`。
- 当前系统默认会填 `sys` 与 `slot`，`rag` 会按模板驱动检索（每轮最多 1 次），`ai/ext` 目前默认留空。

---

## 0. 基本信息

| 项目 | 内容 |
|---|---|
| 设计师/工作室 | 侧石工作室 |
| 方案日期 | {{sys:date}} |
| 客户姓名 | {{slot:customer_name}} |

---

## 1. 客户基础信息（核心参考）

| 项目 | 具体内容 |
|---|---|
| 身高 | {{slot:height_cm}} cm |
| 体重 | {{slot:weight_kg}} kg |
| 胸围 | {{slot:bust_cm}} cm |
| 腰围 | {{slot:waist_cm}} cm |
| 臀围 | {{slot:hip_cm}} cm |
| 身材特点简述 | {{ai}} |
| 偏好风格 | {{slot:style_preferences}} |
| 核心穿搭需求 | {{slot:core_needs}} |
| 禁忌元素 | {{slot:avoid_elements}} |

---

## 2. 使用场景与约束（补充信息）

| 项目 | 具体内容 |
|---|---|
| 日常场景 | {{ai}} |
| 预算范围（单件/整套） | {{slot:budget_range}} |
| 气候/城市 | {{slot:climate_city}} |
| 职业/通勤强度 | {{slot:work_context}} |
| 穿着习惯 | {{slot:size_habits}} |

---

## 3. 整体穿搭核心思路（预填草案，可按客户信息调整）

1. 版型选择：{{ai}}。  
2. 色系方向：{{ai}}。  
3. 面料质感：{{ai}}。  
4. 设计细节：{{ai}}。  

---
