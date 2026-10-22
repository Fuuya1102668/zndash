# zndash

NiceGUI と Python で動く個人用ダッシュボードです。
画面には石川県の天気、直近の降水強度、RSSニュースを表示します。

## Linux ミニPCへのセットアップ

このアプリはミニPC上で動き、Codex CLIをローカルプロセスとして呼び出します。初回のニュース分析と毎時更新には、ミニPCからのインターネット接続が必要です。

以下は Debian / Ubuntu 系 Linux の例です。Python 3.10 以降を使える環境を用意してください。

### 1. 必要なパッケージを用意

~~~sh
sudo apt update
sudo apt install -y ca-certificates curl git python3 python3-venv
python3 --version
~~~

### 2. Codex CLIをインストール

OpenAI公式のLinux用インストーラーを実行します。

~~~sh
curl -fsSL https://chatgpt.com/codex/install.sh | sh
codex --version
~~~

詳しくは[Codex CLI クイックスタート](https://developers.openai.com/codex/cli/)を参照してください。

### 3. Codexにログイン

アプリを実行するLinuxユーザーでログインし、認証状態を確認します。

~~~sh
codex login
codex login status
~~~

ブラウザーのないミニPCでは、ChatGPTのセキュリティ設定でデバイスコード認証が有効な場合、次を使えます。

~~~sh
codex login --device-auth
~~~

詳細は[Codexの認証方法](https://learn.chatgpt.com/docs/auth)を参照してください。ChatGPTアカウントでログインすると対象プランの利用枠が適用されます。APIキーでログインする場合はOpenAI Platformの従量課金です。

### 4. プロジェクトとPython環境を用意

リポジトリをミニPCにクローンします。REPOSITORY_URL は実際のGitリポジトリURLに置き換えてください。

~~~sh
mkdir -p "$HOME/src"
git clone REPOSITORY_URL "$HOME/src/rabbitfish"
cd "$HOME/src/rabbitfish"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
~~~

Gitを使わずにプロジェクトをコピーした場合は、コピー先に移動してから仮想環境を作成してください。Codexの認証とアプリの起動は同じLinuxユーザーで行います。SQLiteデータベースは zndash/data/news.sqlite3 に保存されます。

### 5. アプリを起動

降水強度の表示にYahoo! JAPAN Web APIを使う場合は、アプリケーションIDを設定します。設定を省略した場合、雨量グラフは表示されません。

~~~sh
export YAHOO_WEATHER_APP_ID="Yahoo! JAPAN Web APIのアプリケーションID"
python -m zndash
~~~

別の端末からは `http://<ミニPCのIPアドレス>:8080/information-landscape` を開きます。IPアドレスは `hostname -I` で確認できます。ニュースは起動時に取得・要約し、その後1時間ごとに更新します。

### 6. 電源投入後に自動起動（任意）

Linuxユーザーサービスを使うと、アプリをバックグラウンドで起動できます。まずCodex CLIの絶対パスを確認します。

~~~sh
command -v codex
mkdir -p "$HOME/.config/zndash" "$HOME/.config/systemd/user"
~~~

環境ファイルを作り、ZNDASH_CODEX_CLI を command -v codex の出力に置き換えます。雨量表示が不要な場合は、YAHOO_WEATHER_APP_ID の行を省略できます。

~~~sh
cat > "$HOME/.config/zndash/environment" <<'EOF'
ZNDASH_CODEX_CLI=/home/ユーザー名/.local/bin/codex
YAHOO_WEATHER_APP_ID=Yahoo! JAPAN Web APIのアプリケーションID
EOF
chmod 600 "$HOME/.config/zndash/environment"
~~~

サービスファイルを作成します。プロジェクトを別の場所に置いた場合は `WorkingDirectory` と `ExecStart` を合わせてください。

~~~sh
cat > "$HOME/.config/systemd/user/zndash.service" <<'EOF'
[Unit]
Description=zndash dashboard
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
WorkingDirectory=%h/src/rabbitfish
EnvironmentFile=%h/.config/zndash/environment
ExecStart=%h/src/rabbitfish/.venv/bin/python -m zndash
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
~~~

サービスを有効にして起動します。

~~~sh
systemctl --user daemon-reload
systemctl --user enable --now zndash.service
systemctl --user status zndash.service
~~~

再起動後、ログイン前からも自動起動させる場合はユーザーのlingerを有効にします。

~~~sh
sudo loginctl enable-linger "$USER"
~~~

ログは `journalctl --user -u zndash.service -f` で確認できます。

## 構成

- zndash/app.py：NiceGUI の起動
- zndash/dashboard.py：ページと表示部品
- zndash/services.py：天気、降水量、RSS の取得
- zndash/news_pipeline.py：毎時ニュース取得、Codex 要約、クラスタリング処理
- zndash/codex_client.py：Codex CLI の構造化要約
- zndash/news_storage.py：SQLite の要約キャッシュと掲示板データ
- zndash/news_digest.py：キーワード正規化と決定的なクラスタリング
- zndash/config.py：外部 API、更新間隔、データ配置
- assets/zundamon/：React 版から移したキャラクター画像と 3D モデル

外部データ取得と画面表示は Python プロセス内で行います。
以前の画面で使っていた JSON データは zndash/data/ に保管していますが、現在の画面では読み込みません。

ニュース掲示板の改造設計は docs/news-digest-design.md を参照してください。

