#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication

# 相対パスを使用したインポート
print("アプリ起動開始...")
from ui.main_window import MainWindow
from utils.config import Config

def main():
    """アプリケーションのメインエントリーポイント"""
    print("main関数開始")
    
    # アプリケーション情報を設定
    QCoreApplication.setApplicationName(Config.APP_NAME)
    QCoreApplication.setApplicationVersion(Config.APP_VERSION)
    QCoreApplication.setOrganizationName("GeminiImgEditor")
    
    # PySide6アプリケーションを作成
    print("QApplicationを作成")
    app = QApplication(sys.argv)
    
    # メインウィンドウを作成
    print("MainWindowを作成")
    window = MainWindow()
    print("ウィンドウを表示")
    window.show()
    
    # アプリケーションを実行
    print("アプリケーション実行開始")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
