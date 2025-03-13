import cv2
import face_recognition
import numpy as np
import os
import datetime
import simpleaudio as sa
import io
import text2speech  # text2speech.pyをインポート

# 顔認識の許容度（値が小さいほど厳密）
tolerance = 0.4

# 画像フォルダのパス
image_folder = 'images/'

# 音声ファイルのディレクトリ
audio_folder = 'audio/'

# 既知の顔のエンコーディングと名前を格納するリスト
known_face_encodings = []
known_face_names = []

# 各人物の最後に音声を再生した日付を記録する辞書
last_played_dates = {}

# フォルダごとに画像を処理
folder_list = [folder for folder in os.listdir(image_folder) if os.path.isdir(os.path.join(image_folder, folder))]

for foldername in folder_list:
    folder_path = os.path.join(image_folder, foldername)
    image_files = [f for f in os.listdir(folder_path) if f.endswith((".jpg", ".jpeg", ".png"))]

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)

        if face_encodings:
            known_face_encodings.append(face_encodings[0])
            known_face_names.append(foldername)
            # 各人物の初期状態として音声未再生の日付を設定
            last_played_dates[foldername] = None

# カメラの起動
video_capture = cv2.VideoCapture(2)

while True:
    # フレームの取得
    ret, frame = video_capture.read()

    # フレームの縮小（処理速度向上のため）
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # BGRからRGBへの変換
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # フレーム内の顔の位置と特徴量の取得
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding in face_encodings:
        # 顔が既知のものと一致するか確認
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance)
        name = "Unknown"

        # 一致する顔が見つかった場合、最初の一致を使用
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

            # 現在の日付を取得
            current_date = datetime.date.today()

            # 音声ファイルの再生（1日1回のみ）
            if name == "fuya":
                if last_played_dates["fuya"] is None or last_played_dates["fuya"] != current_date:
                    # 現在の時刻を取得
                    now = datetime.datetime.now()
                    # 再生するテキストを作成
                    text = f"おはようなのだ！今日は{now.month}月{now.day}日，{now.hour}時{now.minute}分なのだ"
                    # 音声を生成
                    response = text2speech.generate_speech(text)
                    # 音声の再生
                    sa.WaveObject.from_wave_file(io.BytesIO(response.content)).play().wait_done()
                    # 最後に音声を再生した日付を更新
                    last_played_dates["fuya"] = current_date

            if name == "tkg":
                if last_played_dates["tkg"] is None or last_played_dates["tkg"] != current_date:
                    audio_file_path = os.path.join(audio_folder, "tkg.wav")
                    if os.path.exists(audio_file_path):
                        wave_obj = sa.WaveObject.from_wave_file(audio_file_path)
                        play_obj = wave_obj.play()
                        play_obj.wait_done()
                    # 最後に音声を再生した日付を更新
                    last_played_dates["tkg"] = current_date

    # 'q'キーが押されたらループを終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースの解放
video_capture.release()
cv2.destroyAllWindows()
