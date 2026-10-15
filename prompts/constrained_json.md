# 结构化 JSON 约束解码（核心）

## 为什么约束解码
自由文本生成模型直接「写 JSON」有三大失效：括号不配平、字段名拼错、类型不对。
约束解码在每个 token 步只允许「能保持 JSON 前缀合法」的 token，从根上消除语法错误。

## 通用提示词模板
```
请从下面的文档提取信息，输出严格符合 JSON Schema 的结构化数据：

Schema:
<JSON Schema 文本>

要求：
1. 只输出 JSON，不加 Markdown 代码块标记；
2. 所有字段必须出现（required）；
3. 数字用 number 类型，不要带引号。
```

## 工程要点
- **Schema 即契约**：把 JSON Schema 直接贴进提示词 + 服务端再校验一次（`decode/json_schema.py`），
  双保险。
- **温度调低**：结构化提取建议 temperature ≤ 0.3，减少「创造性改写字段名」。
- **状态机校验**：`decode/constrained.py` 的有限状态机可作为「前缀合法性」的参考实现，
  真实部署时用 grammar 约束（如 Outlines / XGrammar）替换。
