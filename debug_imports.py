import sys
import time

def test_import(module_name):
    start = time.time()
    print(f"Importing {module_name}...", end="", flush=True)
    try:
        __import__(module_name)
        print(f" Done ({time.time() - start:.2f}s)")
    except Exception as e:
        print(f" Failed: {e}")

print("--- Starting Import Debug ---")
test_import("yaml")
test_import("networkx")
test_import("litellm")
test_import("adapters.llm_adapter")
test_import("adapters.graph_adapter")
test_import("adapters.tts_adapter")
test_import("core.ingestion")
test_import("core.graduation")
print("--- Finished ---")
