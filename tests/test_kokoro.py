import traceback
from kokoro_onnx import Kokoro
try:
    Kokoro('kokoro-v0_19.onnx', 'voices-v1.0.bin')
    print("Success")
except Exception as e:
    traceback.print_exc()
