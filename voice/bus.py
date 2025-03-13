import datetime
import time
import json
import simpleaudio as sa
import io
import text2speech  # text2speech.pyをインポート

import get_time

def check_time(json_file):
    while True:
        with open(json_file, "r") as file:
            data = json.load(file)

        current_time = get_time.get_time()
        current_hour, current_minute = current_time[2], current_time[3]

        for event in data["times"]:
            event_hour = event // 100
            event_minute = event % 100
            
            event_time = datetime.datetime(2000, 1, 1, event_hour, event_minute)
            check_time = event_time - datetime.timedelta(minutes=15)

            if check_time.hour == current_hour and check_time.minute == current_minute:
                # 再生するテキストを作成
                text = "あと15分でバスが出発するのだ!"
                # 音声を生成
                response = text2speech.generate_speech(text)
                # 音声の再生
                sa.WaveObject.from_wave_file(io.BytesIO(response.content)).play().wait_done()

        time.sleep(60)

if __name__ == "__main__":
    check_time("bus.json")
