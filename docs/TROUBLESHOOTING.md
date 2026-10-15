# 故障排查

## `ModuleNotFoundError: No module named 'parseforge'`

在项目根目录 `pip install -e .`，或运行示例前先确保项目根在 `sys.path`（示例已处理）。

## `KeyError: unknown backend`

后端名写错。用 `python -c "from parseforge.backends import list_backends; print(list_backends())"` 查看。

## region_accuracy 恒为 1.0

说明 `skill` 已被训练到 1.0（cpu 后端天然 1.0）。换 mock 且 `skill=0.5` 再看。

## 服务启动后 curl 无响应

默认绑定 `127.0.0.1:8000`，确认端口未被占用；先 `curl http://127.0.0.1:8000/health` 探活。
