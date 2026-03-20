import json
print("Loading voices.json...")
with open('voices.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
changed = False
for k, v in d.items():
    if isinstance(v, list):
        d[k] = {"data": v}
        changed = True
if changed:
    print("Fixing voices.json format to match kokoro-onnx expectations.")
    with open('voices.json', 'w', encoding='utf-8') as f:
        json.dump(d, f)
    print("Fixed!")
else:
    print("No fix needed.")
