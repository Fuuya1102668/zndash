from style_bert_vits2.nlp import bert_models
from style_bert_vits2.constants import Languages
from pathlib import Path
from style_bert_vits2.tts_model import TTSModel
import sounddevice as sd

bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")

#モデルの重みが格納されているpath
model_file = "zundamon/zundamon_e100_s16200.safetensors"
config_file = "zundamon/config.json"
style_file = "zundamon/style_vectors.npy"

assets_root = Path("model_assets")

#モデルインスタンスの作成
model = TTSModel(
    model_path=assets_root / model_file,
    config_path=assets_root / config_file,
    style_vec_path=assets_root / style_file,
    device="cuda",
)

#「こんにちは」と発話
sr, audio = model.infer(text="こんにちは")
#再生
sd.play(audio, sr)
sd.wait()

