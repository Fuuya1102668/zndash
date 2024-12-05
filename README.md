## zndash

### installation
```
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

```
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

```
python3 -m venv venv
source venv/bin/activate
```

```
pip install flask fastapi uvicorn requests
pip install pydantic slack_sdk
```

```
npm install -g @vue/cli
npx create-react-app frontend
cd frontend
npm run serve
```

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
source ~/.bashrc
```

```
nvm install --lts
nvm use --lts
```

```
node -v
npm -v
```

```
mkdir backend
cd backend
npm init -y
```

```
touch index.js
"scripts": {
  "start": "node index.js",
  "dev": "nodemon index.js"
}
```

```
npm start
```


### ディレクトリ構成
```
project-root/
├── backend/
│   ├── app.py           # Flask/FastAPIアプリケーション
│   ├── requirements.txt # Pythonパッケージ
│   └── data/            # 固定データ(JSON)
├── frontend/
│   └── ...              # React/Vue.jsプロジェクト
├── docker-compose.yml    # Docker構成
└── README.md             # プロジェクト説明
```

### やりたいこと
#### 天気予報
OpenWeatherMapなどから現在の天気，明日の天気，今日の降水量などをとりたい．

#### slack
PD-2025の最新の投稿を取得し，表示する．

#### 時刻
現在の日時を表示し，次のゼミの案内を出す．

#### バスの案内
次のバスの出発時刻を表示する．

#### ずんだもん
ずんだもんは欠かせないので，2Dずんだもんを表示する．\\
また，必要に応じて，ずんだもんにテキストを読ませる．

