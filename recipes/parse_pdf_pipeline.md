# 配方 1：PDF 文档解析流水线

## 目标
把一份 PDF 变成结构化 JSON（版面 + 表格 + 图表 + 公式）。

## 步骤
1. PDF → 逐页渲染为图片（外部工具）；
2. 每页跑版面分析（`prompts/layout_analysis.md`）；
3. 对 table/chart/formula 区域分别调用专用头（对应 prompts 目录三个模板）；
4. 按阅读顺序拼装 blocks；
5. 用 JSON Schema 校验，输出。

## 复现命令
```bash
python -m parseforge.cli parse --config configs/document.yaml --doc-id invoice-1 --regions 12
```
