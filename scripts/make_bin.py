import json
import numpy as np
with open('voices.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
voices = {}
for k, v in d.items():
    if isinstance(v, dict) and "data" in v:
        v = v["data"]
    voices[k] = np.array(v, dtype=np.float32)
np.save("voices.bin", voices, allow_pickle=True)
print("voices.bin saved!")
