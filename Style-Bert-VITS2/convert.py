dataset_root = "Data"
assets_root = "model_assets"

# ファイルを読み込む
with open(dataset_root + "/zundamon/recitation_transcript_utf8.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# コンバート
result = []
for line in lines:
    strs = line.split(",")[0].split(":")
    result.append("recitation" + strs[0][-3:] + ".wav|zundamon|JP|" + strs[1] + "\n")

# 変更をファイルに保存
with open(dataset_root + "/zundamon/esd.list", "w", encoding="utf-8") as file:
    file.writelines(result)

# 去々年を含まない行だけを選択
# 去々年の読み方がわからなくてエラーが出る
cleaned_result = [line for line in result if "去々年" not in line]

# ファイルパスを指定
file_path = dataset_root + "/zundamon/esd.list"

# ファイルに変更を保存
with open(file_path, "w", encoding="utf-8") as file:
    file.writelines(cleaned_result)
