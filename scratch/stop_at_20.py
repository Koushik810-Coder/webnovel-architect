import json, time, os
story_uuid = 'd6278b7b-4b5b-486f-8d05-f2f0f656963b'
path = os.path.join('data', story_uuid, 'runtime_db.json')
print('Monitoring for chapter 20...')
while True:
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                d = json.load(f)
                if d.get('chapter_counter', 0) >= 20:
                    with open('cancel_ingestion.flag', 'w') as flag:
                        flag.write('cancel')
                    print('Reached chapter 20, stop flag written.')
                    break
    except Exception as e:
        print("Error:", e)
    time.sleep(5)
