"""
GeminiReImageの設定ファイル
"""
import os
from pathlib import Path

# アプリケーション設定
APP_NAME = "GeminiReImage"
APP_VERSION = "1.0.0"

# ウィンドウサイズ設定
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

# 画像パネル設定
IMAGE_PANEL_SIZE = 400  # 幅と高さ (正方形)

# APIモデル設定
GEMINI_MODEL = "gemini-2.0-flash-exp-image-generation"
API_TIMEOUT = 60  # 秒

# 保存先設定
PICTURES_DIR = Path(os.path.expanduser("~")) / "Pictures" / "Gemini"
HISTORY_FILE = Path("data") / "history.json"

# プロンプト設定
MAX_PROMPT_LENGTH = 500
HISTORY_MAX_ITEMS = 20
PROMPT_DISPLAY_LENGTH = 30  # 履歴表示時の最大文字数

# サポートする画像形式
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".webp"]
MAX_IMAGE_SIZE = 4 * 1024 * 1024  # 4MB 