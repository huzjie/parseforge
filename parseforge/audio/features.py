"""Deterministic audio features (no numpy / librosa).

Models a ``frame_size`` x ``n_frames`` spectrogram. Real audio would be fed by a
mel filterbank; here the values come from a deterministic source so the whole
pipeline is reproducible without external files.
"""
from ..utils.hash import stable_float


def mel_frames(key, frame_size, n_frames):
    """Return a deterministic ``n_frames x frame_size`` float grid for ``key``."""
    out = []
    for f in range(n_frames):
        out.append([stable_float("%s:%d:%d" % (key, f, t), 0.0, 1.0)
                    for t in range(frame_size)])
    return out
