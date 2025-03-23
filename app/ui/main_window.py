import os
import sys
import threading
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QThreadPool, QRunnable, Slot, Signal, QObject
from PySide6.QtGui import QPixmap

# 相対パスを使用したインポート
from ui.image_view import ImageView
from ui.chat_panel import ChatPanel
from services.gemini_service import GeminiService
from services.image_service import ImageService
from models.thread_manager import ThreadManager
from utils.file_manager import FileManager
from utils.config import Config

class WorkerSignals(QObject):
    """ワーカーシグナル定義"""
    finished = Signal(dict)
    error = Signal(str)

class ImageEditWorker(QRunnable):
    """画像編集処理用ワーカー"""
    
    def __init__(self, gemini_service, image, instruction):
        super().__init__()
        self.gemini_service = gemini_service
        self.image = image
        self.instruction = instruction
        self.signals = WorkerSignals()
    
    @Slot()
    def run(self):
        try:
            # 画像編集処理を実行
            result = self.gemini_service.modify_image(self.image, self.instruction)
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))

class MainWindow(QMainWindow):
    """メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        print("MainWindow初期化開始")
        
        # モデルの初期化
        print("ThreadManager初期化")
        self.thread_manager = ThreadManager()
        
        # サービスの初期化
        print("GeminiService初期化")
        self.gemini_service = GeminiService()
        print("ImageService初期化")
        self.image_service = ImageService(self.thread_manager)
        
        # スレッドプール
        self.thread_pool = QThreadPool()
        
        # UIの初期化
        print("UI初期化")
        self.setup_ui()
        self.setup_connections()
        
        # 設定の検証
        if not Config.validate_config():
            QMessageBox.warning(
                self,
                "設定エラー",
                "Google API キーが設定されていません。環境変数 GOOGLE_API_KEY を設定してください。"
            )
        
        # 起動時に既存のスレッドがあれば会話履歴を読み込む
        self.load_current_thread()
    
    def setup_ui(self):
        """UIの初期化"""
        self.setWindowTitle(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.setMinimumSize(1000, 600)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        main_layout = QHBoxLayout(central_widget)
        
        # 分割ウィジェット
        self.splitter = QSplitter(Qt.Horizontal)
        
        # 画像表示エリア
        self.image_view = ImageView()
        self.splitter.addWidget(self.image_view)
        
        # チャットパネル
        self.chat_panel = ChatPanel()
        self.splitter.addWidget(self.chat_panel)
        
        # 分割の比率を設定（7:3）
        self.splitter.setSizes([700, 300])
        
        main_layout.addWidget(self.splitter)
    
    def setup_connections(self):
        """シグナル/スロット接続"""
        # 画像読み込み
        self.image_view.image_loaded.connect(self.on_image_loaded)
        
        # メッセージ送信
        self.chat_panel.message_sent.connect(self.on_message_sent)
        
        # スレッド管理
        self.chat_panel.new_thread_requested.connect(self.on_new_thread_requested)
        self.chat_panel.thread_changed.connect(self.on_thread_changed)
        self.chat_panel.open_save_dir_requested.connect(self.on_open_save_dir)
    
    def load_current_thread(self):
        """現在のスレッドデータをロード"""
        # スレッドリストを更新
        thread_titles = self.thread_manager.get_thread_titles()
        current_thread_id = self.thread_manager.current_thread_id
        
        self.chat_panel.update_thread_list(thread_titles, current_thread_id)
        
        # 会話履歴を読み込み
        conversations = self.thread_manager.get_conversation_history()
        self.chat_panel.load_conversation_history(conversations)
        
        # 最新の画像があれば読み込み
        self.image_service.load_latest_image()
        current_image = self.image_service.get_current_image()
        if current_image:
            self.image_view.set_pil_image(current_image)
    
    def on_image_loaded(self, image_path):
        """画像が読み込まれたときの処理"""
        # 画像サービスで画像を読み込み
        if self.image_service.load_image(image_path):
            print(f"画像を読み込みました: {image_path}")
    
    def on_message_sent(self, message):
        """メッセージが送信されたときの処理"""
        # 処理中状態に設定
        self.chat_panel.set_processing_state(True)
        
        # ユーザーメッセージをスレッドに追加
        self.thread_manager.add_message("user", message)
        
        # 現在の画像を取得
        current_image = self.image_service.get_current_image()
        if not current_image:
            # 画像がなければエラーメッセージ
            self.chat_panel.add_assistant_message("画像が読み込まれていません。画像を開いてください。")
            self.chat_panel.set_processing_state(False)
            return
        
        # 画像編集ワーカーを作成
        worker = ImageEditWorker(self.gemini_service, current_image, message)
        
        # 完了時の処理
        worker.signals.finished.connect(self.on_image_edit_finished)
        
        # エラー時の処理
        worker.signals.error.connect(self.on_image_edit_error)
        
        # ワーカーを開始
        self.thread_pool.start(worker)
    
    def on_image_edit_finished(self, result):
        """画像編集が完了したときの処理"""
        response_text = result.get("text", "")
        response_image = result.get("image")
        
        if not response_image:
            self.chat_panel.add_assistant_message("画像の生成に失敗しました: " + response_text)
            self.chat_panel.set_processing_state(False)
            return
        
        # 編集結果を表示
        self.image_view.set_pil_image(response_image)
        
        # 編集結果を保存
        image_path = self.image_service.save_edited_image(response_image)
        
        # 応答メッセージをスレッドに追加
        self.thread_manager.add_message("assistant", response_text, image_path)
        
        # 応答をチャットパネルに表示
        self.chat_panel.add_assistant_message(response_text, image_path)
        
        # 処理中状態を解除
        self.chat_panel.set_processing_state(False)
    
    def on_image_edit_error(self, error_message):
        """画像編集でエラーが発生したときの処理"""
        self.chat_panel.add_assistant_message(f"エラーが発生しました: {error_message}")
        self.chat_panel.set_processing_state(False)
    
    def on_new_thread_requested(self):
        """新規会話が要求されたときの処理"""
        # 新しいスレッドを作成
        self.thread_manager.create_new_thread()
        
        # スレッドリストを更新
        thread_titles = self.thread_manager.get_thread_titles()
        current_thread_id = self.thread_manager.current_thread_id
        
        self.chat_panel.update_thread_list(thread_titles, current_thread_id)
        
        # メッセージをクリア
        self.chat_panel.clear_messages()
        
        # 画像表示をクリア
        self.image_view.image_path = None
        self.image_view.image_label.setText("ここに画像をドラッグ＆ドロップするか、「画像を開く」をクリックしてください")
        self.image_view.image_label.setPixmap(QPixmap())  # 空のQPixmapを設定
        
        # 画像サービスの状態をリセット
        self.image_service.current_image = None
        self.image_service.current_image_path = None
    
    def on_thread_changed(self, thread_id):
        """スレッドが変更されたときの処理"""
        # 現在のスレッドを変更
        if self.thread_manager.set_current_thread(thread_id):
            # 会話履歴を読み込み
            conversations = self.thread_manager.get_conversation_history()
            self.chat_panel.load_conversation_history(conversations)
            
            # 最新の画像があれば読み込み
            self.image_service.load_latest_image()
            current_image = self.image_service.get_current_image()
            if current_image:
                self.image_view.set_pil_image(current_image)
            else:
                # 画像がなければ表示をクリア
                self.image_view.image_path = None
                self.image_view.image_label.setText("ここに画像をドラッグ＆ドロップするか、「画像を開く」をクリックしてください")
                self.image_view.image_label.setPixmap(QPixmap())  # 空のQPixmapを設定
    
    def on_open_save_dir(self):
        """保存フォルダを開く"""
        FileManager.open_save_directory()
    
    def closeEvent(self, event):
        """ウィンドウが閉じられるときの処理"""
        # スレッドプールが終了するのを待つ
        self.thread_pool.waitForDone()
        event.accept()
