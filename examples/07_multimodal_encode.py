import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
"""Encode text + image + audio through the omni encoder."""
from parseforge.config import Config
from parseforge.model.encoder import OmniEncoder
from parseforge.audio.features import mel_frames

cfg = Config()
enc = OmniEncoder(cfg)
image = [[0.5 for _ in range(cfg.vision.img_size)]
         for _ in range(cfg.vision.img_size)]
audio = mel_frames("audio-0", cfg.audio.frame_size, cfg.audio.n_frames)
pooled = enc.pooled(image=image, text="hello world", audio_frames=audio)
print("pooled dim =", len(pooled))
