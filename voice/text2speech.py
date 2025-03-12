import requests

def generate_speech(text):
    url = "http://localhost:4649/voice"
    headers = {"accept":"audio/wav"}
    params = {
        "text":text,
        "encodeng":"utf-8",
        "model_name":"zundamon",
    }
    
    return requests.post(url, headers=headers, params=params)

if __name__ == "__main__":
    import simpleaudio as sa
    import io

    while True:
        text = input("音声にしたいテキスト：")
        response = generate_speech(text)
        sa.WaveObject.from_wave_file(io.BytesIO(response.content)).play().wait_done()

