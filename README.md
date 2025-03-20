# GeminiReImage

Gemini APIを使用して画像を編集・生成するためのシンプルなGUIアプリケーションです。

## 機能

- 既存画像のドラッグ＆ドロップによる読み込み
- テキストプロンプトによる画像編集指示
- 生成結果の簡単な再利用
- プロンプト履歴の保存と再利用

## 必要条件

- Windows OS
- Python 3.8以上
- Gemini API キー

## セットアップ

1. リポジトリをクローン:
```
git clone https://github.com/yourusername/GeminiReImage.git
cd GeminiReImage
```

2. 依存関係のインストール:
```
pip install -r requirements.txt
```

3. 環境変数の設定:
   - `GOOGLE_API_KEY`: Gemini APIキーを設定

## 使用方法

1. アプリケーションを起動:
```
python main.py
```

2. 画像を入力パネルにドラッグ＆ドロップ
3. プロンプトを入力して「生成」ボタンをクリック
4. 生成結果を再利用する場合は「入力画像にする」ボタンをクリック

## 注意事項

- 画像サイズは最大4MBまで対応
- サポートしている画像形式: JPG, PNG, WEBP
- 生成結果は自動的に`Pictures\Gemini`フォルダに保存されます 