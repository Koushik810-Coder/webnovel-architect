import asyncio
import edge_tts

async def main():
    try:
        comm = edge_tts.Communicate("Sylver Sezari. 10th tier arch necromance...", "en-US-DavisNeural")
        await comm.save("test_chunk1.mp3")
        print("Chunk 1 success")
    except Exception as e:
        print("Chunk 1 error:", e)

    try:
        comm = edge_tts.Communicate("A…Ariane...", "en-US-TonyNeural")
        await comm.save("test_chunk4.mp3")
        print("Chunk 4 success")
    except Exception as e:
        print("Chunk 4 error:", e)

    try:
        comm = edge_tts.Communicate("-", "en-US-GuyNeural")
        await comm.save("test_dash.mp3")
        print("Dash success")
    except Exception as e:
        print("Dash error:", e)

asyncio.run(main())
