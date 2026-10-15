import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
"""Start the HTTP server (Ctrl-C to stop)."""
from parseforge.config import Config
from parseforge.server import run_server

cfg = Config()
run_server(cfg.serving.host, cfg.serving.port, cfg)
