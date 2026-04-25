import asyncio
import edge_tts

async def main():
    try:
        comm = edge_tts.Communicate("Hello world", "en-US-GuyNeural")
        await comm.save("test_hello.mp3")
        print("Hello success")
    except Exception as e:
        print("Hello error:", e)

asyncio.run(main())
