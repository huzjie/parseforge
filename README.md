# parseforge

**全模态文档解析引擎：文档 / 图像 / 图表 / 音视频 → 结构化 JSON**

一个零依赖（纯 Python 标准库）的参考实现，拆解腾讯优图 **Youtu-Parsing-Omni 5B**
背后的三条核心技术路线——「统一多模态编码 + 版面感知解析 + 结构化 JSON 约束解码」，
让你在十几秒内跑通、读懂、照着做。

> 背景一句话：Youtu-Parsing-Omni 用**一个模型**把文档、图像、图表、表格、音视频
> 统一输出成结构化 JSON，在 OmniDocBench 拿到 96.96（开源权重第一）。下面不聊它
> 「多强」，只拆「怎么实现、怎么复用」。

---

## 一、技术原理拆解

### 1. 统一多模态编码：所有输入压进同一个 token 空间

传统方案是「每个模态一个模型 + 一堆后处理」，Youtu-Parsing-Omni 的关键动作是
**共享编码器**：视觉 patch、文本 token、音频帧各自投影到同一个 `dim` 维空间，
拼成一条序列喂给共享自注意力。

```
        文档图片 ──> PatchEmbedding ──> ViT ──┐
        文本     ──> token embedding ────────┤──> 融合序列 ──> 共享自注意力 ──> 单解码头
        音频帧   ──> AudioProjector ────────┘
```

对应代码 `parseforge/model/encoder.py`：`OmniEncoder.encode(image, text, audio)`
返回一条 `n_tokens x dim` 的融合序列，**没有**任何 per-modality head。这是它能
「一个模型吃所有输入」的根因。

### 2. 版面感知解析：先分区域，再识别内容

把「版面切分」和「内容识别」解耦，比一次性端到端更稳、也更好单独评测：

- **区域检测**（`layout/regions.py`）：给每个候选框打分，判定
  `title / text / table / chart / formula / figure`；
- **阅读顺序**（`layout/reading_order.py`）：按「上下分带、带内从左到右」排序，
  保证输出 JSON 保留文档流。

### 3. 结构化 JSON 约束解码：从根上消灭「坏 JSON」

自由文本生成模型直接写 JSON 有三大失效：括号不配平、字段名拼错、类型不对。
约束解码在**每个 token 步**只允许「能保持 JSON 前缀合法」的 token：

- `decode/json_schema.py`：一个极简 JSON Schema 校验器（type / required /
  properties / items），服务端二次兜底；
- `decode/constrained.py`：有限状态机校验「部分 JSON 是否仍是合法前缀」——
  这是 grammar 约束（Outlines / XGrammar）的极简参考实现。

### 4. 三个专用解码头：表格 / 图表 / 公式

| 区域类型 | 输出结构 | 关键实现 | 踩坑点 |
|---|---|---|---|
| 表格 | `{rows, has_header}` | `table/` | 合并单元格首格填值、其余 `null` |
| 图表 | `{series:[{name, points}]}` | `chart/` | 图例单独识别，别让主模型同时认图和图例 |
| 公式 | LaTeX 字符串 | `formula/` | 约束到 LaTeX 语法，往返校验 |

---

## 二、可复用的工程技巧（干货）

1. **Schema 即契约**：把 JSON Schema 直接贴进提示词 + 服务端再校验一次，双保险。
2. **可训练 mock 验证评测管线**：接入真实模型前，先用确定性 mock 验证
   「训练信号 → 评测指标」链路单调（见下），避免「指标不涨却不知道是模型还是评测的锅」。
   - `boost = (skill - 0.5) * 2`，`skill=0.5` 时 `boost=0`（纯随机基线），
     `skill=1.0` 时 `boost=1`（恒正确）——这是 mock 训练信号的铁律；
   - 训练信号**单调趋 1**（delta 恒正），不要「对 +1 错 -1」。
3. **共享 oracle 复现真值**：mock 后端和评测框架用同一组 `oracle_*` 函数（同一
   doc_id/idx 派生），`skill=1.0` 时必然满分——评测数字才可信。
4. **数字后处理放解码后**：千分位/百分号/货币符号统一在结构化输出之后处理，
   别让模型猜。
5. **结构化提取调低温度**：`temperature ≤ 0.3`，减少「创造性改写字段名」。

---

## 三、快速开始

```bash
# 零依赖，Python >= 3.9
python -m parseforge.doctor                 # 自检：5 后端全部跑通
python -m parseforge.cli parse --config configs/default.yaml   # 解析合成文档
python -m parseforge.cli bench --config configs/default.yaml   # OmniDocBench 评测
python -m parseforge.cli train --config configs/default.yaml   # 训练演示
python -m parseforge.cli serve --config configs/default.yaml   # 起 HTTP 服务
```

Python API：

```python
from parseforge import Config, OmniParser
from parseforge.oracle import synthesize_document

parser = OmniParser(Config())
result = parser.parse(synthesize_document("doc-0", n_regions=8))
print(result.to_json())
```

---

## 四、基准（OmniDocBench 风格，训练演示）

`mock` 后端从 `skill=0.5`（随机基线）训练到 `skill=1.0`，四个指标单调（实测）：

| 指标 | 训练前 (skill=0.5) | 训练后 (skill=1.0) | 说明 |
|---|---|---|---|
| region_accuracy | 0.50 | 1.00 | 版面类型识别准确率 |
| cell_accuracy | 0.42 | 1.00 | 表格单元格准确率（含区域误分类的连带损失） |
| series_mse | 0.089 | 0.000 | 图表数据序列均方误差（越低越好） |
| json_structure_f1 | 1.00 | 1.00 | JSON 结构合法性（约束解码保证） |

> 数字由 `python -m parseforge.cli train --steps 20 --lr 0.025` 实测，不手写估算。
> 另：`bench`（8 文档平均）在 skill=0.5 下 region_accuracy=0.469、cell_accuracy=0.172、
> series_mse=23.78，训练后均收敛到满分方向。

---

## 五、目录结构

```
parseforge/
├── vision/        ViT 视觉塔（patch + attention）
├── audio/         音频投影
├── layout/        版面分析（区域 + 阅读顺序）
├── table/         表格识别（结构/单元格/合并）
├── chart/         图表理解（数据序列/图例）
├── formula/       公式识别（LaTeX）
├── decode/        约束 JSON 解码 + Schema 校验
├── model/         多模态编码器 + 结构化解码器
├── backends/      mock / cpu / openai / vllm / transformers
├── bench/         OmniDocBench 评测框架
├── engine.py      端到端 OmniParser
├── cli.py / server.py / doctor.py / train.py
prompts/           可复用提示词与工作流模板
recipes/           端到端可复现配方
examples/          可直接运行的示例脚本
configs/           YAML 配置（default/tiny/document）
deploy/            Docker / K8s / Helm / CI
```

## 六、License

Apache-2.0。本仓库为教学与参考性质，实现的是 Youtu-Parsing-Omni 展示的
「统一编码 + 版面解析 + 约束解码」思想，**不含**其真实模型权重。
