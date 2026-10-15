# 模块 vision

视觉塔（patch embedding / 多头自注意力 / ViT），把图片压成 token 序列。

## 相关文件

见 `parseforge/vision/`。

## 设计要点

- 零依赖、确定性优先。
- 接口稳定，供上层引擎与评测复用。
