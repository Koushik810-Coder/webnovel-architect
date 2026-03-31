import pytest
import os

@pytest.mark.skipif(
    not os.path.exists("kokoro-v0_19.onnx"),
    reason="Kokoro model files (kokoro-v0_19.onnx / voices-v1.0.bin) not present in repo."
)
def test_kokoro_loads():
    """Verify Kokoro model loads successfully when model files are present."""
    from kokoro_onnx import Kokoro
    model = Kokoro("kokoro-v0_19.onnx", "voices-v1.0.bin")
    assert model is not None
