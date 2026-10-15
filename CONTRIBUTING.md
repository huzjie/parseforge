# 贡献指南

## 环境

零第三方依赖，Python ≥ 3.9 即可。建议 `pip install -e .` 开发。

## 提交流程

1. fork 并 clone；
2. 新建分支 `feat/xxx`；
3. 改动后运行：

```bash
python -m compileall -q parseforge
python -m unittest discover -s tests -t .
python -m parseforge.doctor
```

4. 提交 PR。

## 代码约定

- 保持零依赖：不引入 numpy/torch/requests 等第三方库。
- 确定性优先：随机一律走 `parseforge.utils.hash`。
- 新后端用 `@register_backend`，新基准指标加进 `bench/metrics.py`。
