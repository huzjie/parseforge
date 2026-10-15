"""Omni-modal encoder: fuse vision, text and audio into one token space.

This is the architectural heart of Youtu-Parsing-Omni's "one model, any input"
property: every modality is projected to a shared ``dim``-dimensional embedding,
concatenated, and fed to a shared self-attention stack. The output is a single
sequence the decoder consumes -- no per-modality heads.
"""
from ..tensor import Tensor, matmul, layernorm
from ..vision.vit import VisionTower
from ..vision.attention import MultiHeadAttention
from ..audio.projector import AudioProjector
from ..utils.text import tokenize_ascii
from ..utils.hash import stable_vector


class OmniEncoder:
    def __init__(self, cfg):
        self.dim = cfg.vision.dim
        self.vision = VisionTower(cfg.vision.img_size, cfg.vision.patch_size,
                                  cfg.vision.dim, cfg.vision.depth, cfg.vision.heads)
        self.audio = AudioProjector(cfg.audio.frame_size, cfg.audio.dim)
        self.fusion = MultiHeadAttention(cfg.vision.dim, cfg.vision.heads)
        # token embedding table (deterministic)
        self.token_emb = {}

    def _embed_text(self, text):
        tokens = tokenize_ascii(text)
        vecs = []
        for t in tokens:
            if t not in self.token_emb:
                self.token_emb[t] = stable_vector("tok:%s" % t, self.dim, -0.2, 0.2)
            vecs.append(self.token_emb[t])
        return vecs if vecs else [stable_vector("tok:<empty>", self.dim, -0.2, 0.2)]

    def encode(self, image=None, text="", audio_frames=None):
        """Return a fused ``Tensor`` (n_tokens x dim)."""
        parts = []
        if image is not None:
            x = self.vision.encode(image)
            parts.extend(x.data)
        if text:
            parts.extend(self._embed_text(text))
        if audio_frames is not None:
            av = self.audio(audio_frames)
            parts.append(av)
        if not parts:
            parts = [stable_vector("tok:<empty>", self.dim, -0.2, 0.2)]
        seq = Tensor(parts)
        fused = layernorm(seq + self.fusion(seq))
        return fused

    def pooled(self, image=None, text="", audio_frames=None):
        """A single summary vector for the whole multimodal input."""
        seq = self.encode(image, text, audio_frames)
        n = len(seq.data)
        return [sum(seq.data[i][c] for i in range(n)) / n for c in range(self.dim)]
