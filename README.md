# GeminiImgEditor

Gemini APIを使用した会話型画像編集アプリケーション
履歴とかまだうまくいってない


## 使用方法

```bash
python app/main.py
```

## 動作環境

- Windows 10以上
- Python 3.8以上

## ディレクトリ構造

```
app/
  |- main.py             # アプリケーションのエントリーポイント
  |- ui/                 # UIコンポーネント
  |   |- main_window.py  # メインウィンドウ
  |   |- image_view.py   # 画像表示コンポーネント
  |   |- chat_panel.py   # 会話パネル
  |
  |- services/
  |   |- gemini_service.py  # Gemini API連携
  |   |- image_service.py   # 画像処理
  |
  |- models/
  |   |- thread_manager.py  # スレッドと会話の管理
  |
  |- utils/
      |- config.py          # 設定管理
      |- file_manager.py    # ファイル操作とパス管理
