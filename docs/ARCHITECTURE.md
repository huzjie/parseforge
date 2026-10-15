# 架构说明

## 总览

```
                 ┌─────────────────────────────────────────────┐
                 │                 OmniParser (engine)           │
                 │   backend.parse(document) -> ParseResult      │
                 │   + JSON Schema 校验                           │
                 └──────────────────┬────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
 ┌─────────────┐           ┌─────────────────┐         ┌─────────────────┐
 │  OmniEncoder │           │  RegionDetector  │         │  backends        │
 │  (vision/    │           │  + reading_order │         │  mock/cpu/openai │
 │   audio/text)│           └─────────────────┘         │  vllm/transf.    │
 └─────────────┘                                         └─────────────────┘
```

## 数据流

1. `Document`（文本 + 可选图片 + 可选音频 + 版面候选框）进入 `OmniParser.parse`；
2. 后端（`backends.py`）产出一个 `ParseResult`（有序 blocks）；
3. `engine` 用 `decode/json_schema.py` 校验结果结构合法性；
4. 返回带 `schema_valid` 标志的 `ParseResult`。

## 后端抽象

所有后端共享 `_build_result(doc, boost, cfg)`，差异只在 `boost`：

| 后端 | boost | 用途 |
|---|---|---|
| mock | `(skill-0.5)*2` | 可训练、确定性、演示信号单调 |
| cpu | `1.0` | 本地确定性、恒正确 |
| openai/vllm/transformers | `1.0` | API 适配器，无端点时回退本地 |

## 设计取舍

- **零依赖**：张量用 Python 列表，YAML 用内置子集解析器，HTTP 用 stdlib ——
  「读代码学习 + 秒级跑通」优先于性能。
- **oracle 单一来源**：`parseforge/oracle.py` 是 mock 与评测共享的真值来源，
  保证「skill=1.0 → 满分」严格成立。
