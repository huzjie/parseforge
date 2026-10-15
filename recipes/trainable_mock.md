# 配方 3：用可训练 mock 验证评测管线

## 目标
在接入真实模型前，先用 mock 后端验证「训练信号 → 评测指标」这条链路是单调的。

## 步骤
```bash
python -m parseforge.cli train --config configs/default.yaml --steps 20 --lr 0.025
python -m parseforge.cli bench --config configs/default.yaml
```

## 期望
- region_accuracy / cell_accuracy 从 ~0.5 爬向 1.0；
- series_mse 单调下降；
- skill 单调趋 1（delta 恒正）。
