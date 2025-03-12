from webui_train import preprocess_all

# `Data/{model_name}/`
model_name = "zundamon"

# JP-Extra （日本語特化版）を使うかどうか。日本語の能力が向上する代わりに英語と中国語は使えなくなります。
#use_jp_extra = True
use_jp_extra = False

# 学習のバッチサイズ。VRAMのはみ出具合に応じて調整してください。
batch_size = 4

# 学習のエポック数（データセットを合計何周するか）。
# 100ぐらいで十分かもしれませんが、もっと多くやると質が上がるのかもしれません。
epochs = 100

# 保存頻度。何ステップごとにモデルを保存するか。分からなければデフォルトのままで。
save_every_steps = 1000

# 音声ファイルの音量を正規化するかどうか
normalize = True

# 音声ファイルの開始・終了にある無音区間を削除するかどうか
trim = True

# 読みのエラーが出た場合にどうするか。
# "raise"ならテキスト前処理が終わったら中断、"skip"なら読めない行は学習に使わない、"use"なら無理やり使う
yomi_error = "skip"

preprocess_all(
    model_name=model_name,
    batch_size=batch_size,
    epochs=epochs,
    save_every_steps=save_every_steps,
    num_processes=2,
    normalize=normalize,
    trim=trim,
    freeze_EN_bert=False,
    freeze_JP_bert=False,
    freeze_ZH_bert=False,
    freeze_style=False,
    freeze_decoder=False, # ここをTrueにするともしかしたら違う結果になるかもしれません。
    use_jp_extra=use_jp_extra,
    val_per_lang=0,
    log_interval=200,
    yomi_error=yomi_error
)

