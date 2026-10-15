"""Audio branch: turns an audio clip into a shared-space token sequence."""
from .features import mel_frames
from .projector import AudioProjector

__all__ = ["mel_frames", "AudioProjector"]
