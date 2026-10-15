# parseforge

Omni-modal document parsing engine: documents / images / charts / audio-video -> structured JSON.

A zero-dependency (stdlib-only) reference implementation unpacking the three core
technical routes behind Tencent Youtu's **Youtu-Parsing-Omni 5B**: unified
omni-modal encoding, layout-aware parsing, and constrained JSON decoding.

```bash
python -m parseforge.doctor
python -m parseforge.cli bench --config configs/default.yaml
python -m parseforge.cli serve --config configs/default.yaml
```

See `README.md` (Chinese) for the full technical deep-dive, reusable engineering
tips, and prompt templates.
