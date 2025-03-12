# 学習に必要なファイルや途中経過が保存されるディレクトリ
dataset_root = "Data"

# 学習結果（音声合成に必要なファイルたち）が保存されるディレクトリ
assets_root = "model_assets"

import yaml


with open("configs/paths.yml", "w", encoding="utf-8") as f:
    yaml.dump({"dataset_root": dataset_root, "assets_root": assets_root}, f)
