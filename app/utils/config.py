import os
import json
from pathlib import Path
from dotenv import load_dotenv

# .envファイルがあれば読み込む
load_dotenv()

class Config:
    # APIキー設定
    API_KEY = os.environ.get("GOOGLE_API_KEY")
    
    # モデル設定
    MODEL_NAME = "gemini-2.0-flash-exp"
    
    # アプリケーション設定
    APP_NAME = "GeminiImgEditor"
    APP_VERSION = "1.0.0"
    
    # ファイル保存設定
    # 画像保存ディレクトリ
    SAVE_DIRECTORY = os.path.join(os.path.expanduser("~"), "Pictures", "GeminiImgEditor")
    os.makedirs(SAVE_DIRECTORY, exist_ok=True)
    
    # スレッド情報保存ディレクトリ
    THREADS_DIRECTORY = os.path.join(SAVE_DIRECTORY, "threads")
    os.makedirs(THREADS_DIRECTORY, exist_ok=True)
    
    # 設定のバリデーション
    @classmethod
    def validate_config(cls):
        """設定が有効かどうか確認"""
        if not cls.API_KEY:
            print("警告: GOOGLE_API_KEYが設定されていません。環境変数を設定してください。")
            return False
        return True
