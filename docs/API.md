# API 参考

## 顶层

- `parseforge.OmniParser(cfg=None)`：端到端解析器。
  - `.parse(document) -> ParseResult`
  - `.train_step()` / `.skill` / `.backend_name`
- `parseforge.Config` / `parseforge.load_config(path=None)`
- `parseforge.get_backend(name, cfg)` / `parseforge.list_backends()`

## 核心数据

- `parseforge.parse.Document(doc_id, text, image, audio_frames, candidates)`
- `parseforge.parse.ParseResult(doc_id, blocks, schema_valid)`
  - `.as_dict()` / `.to_json()`

## 各模块

- `parseforge.vision.vit.VisionTower.encode(image)` / `.cls(image)`
- `parseforge.audio.projector.AudioProjector(frames)`
- `parseforge.layout.regions.RegionDetector.detect(candidates)`
- `parseforge.table.cells.cells_to_rows(key, n_rows, n_cols)`
- `parseforge.chart.series.extract_series(key, n_series, n_points, trend)`
- `parseforge.formula.latex.latex_from_ids(tokens)`
- `parseforge.decode.constrained.ConstrainedDecoder`
- `parseforge.decode.json_schema.Schema` / `validate`
- `parseforge.bench.omnidocbench.OmniDocBench`

## 配置项（YAML）

```yaml
vision: {patch_size, img_size, dim, depth, heads}
audio:  {frame_size, n_frames, dim}
layout: {min_area, score_threshold}
table:  {max_rows, max_cols}
chart:  {max_series, max_points}
decode: {max_tokens, temperature, top_p, schema_mode}
model:  {name, dim, skill}
serving:{host, port}
```
