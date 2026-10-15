# 模块 backends

五后端（mock/cpu/openai/vllm/transformers）。

## 相关文件

见 `parseforge/backends/`。

## 设计要点

- 零依赖、确定性优先。
- 接口稳定，供上层引擎与评测复用。
