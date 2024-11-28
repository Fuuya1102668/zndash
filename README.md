# zndash
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
vue create frontend
cd frontend
npm run serve
```

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

