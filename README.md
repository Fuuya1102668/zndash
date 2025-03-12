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
npm install three-mesh-bvh@0.8.0
npm install react@18.3.1 react-dom@18.3.1
npm install @react-three/fiber@latest @react-three/drei@latest three@latest
```

### ずんだもんの音声案内
毎日通学したら挨拶と今日の日付，今の時間を教えてくれる．

バスの時間を通知してくれる．

