"""
GeminiReImage アプリケーションのエントリーポイント
"""
import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from src.ui.main_window import MainWindow


def excepthook(exc_type, exc_value, exc_traceback):
    """
    未処理の例外ハンドラー
    """
    error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"エラーが発生しました:\n{error_message}", file=sys.stderr)
    
    # メインループが動いている場合はダイアログを表示
    if QApplication.instance():
        QMessageBox.critical(
            None,
            "アプリケーションエラー",
            f"予期しないエラーが発生しました:\n{str(exc_value)}\n\n詳細はコンソールを確認してください。"
        )


def check_environment():
    """
    環境設定のチェック
    """
    # APIキーの存在確認
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        QMessageBox.critical(
            None,
            "設定エラー",
            "GOOGLE_API_KEYが環境変数に設定されていません。\n"
            "環境変数を設定するか、.envファイルを作成してください。"
        )
        return False
    
    return True


def main():
    """
    メイン関数
    """
    # 例外ハンドラの設定
    sys.excepthook = excepthook
    
    # .envファイルからの環境変数読み込み
    load_dotenv()
    
    # QApplicationの作成
    app = QApplication(sys.argv)
    app.setApplicationName("GeminiReImage")
    
    # ハイDPIサポート
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 環境のチェック
    if not check_environment():
        return 1
    
    # メインウィンドウの表示
    window = MainWindow()
    window.show()
    
    # イベントループの開始
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())