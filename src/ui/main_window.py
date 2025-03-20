"""
アプリケーションのメインウィンドウ
"""
import os
import time
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QProgressBar,
    QApplication, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer

from config.settings import WINDOW_WIDTH, WINDOW_HEIGHT, PICTURES_DIR
from src.api.gemini_client import GeminiClient
from src.utils.history_manager import HistoryManager
from src.utils.image_processor import validate_image_file, save_image_copy, create_output_directory

from src.ui.image_panel import ImagePanel
from src.ui.prompt_panel import PromptPanel
from src.ui.history_panel import HistoryPanel


class GenerateImageThread(QThread):
    """画像生成用スレッド"""
    
    # シグナル定義
    progress = Signal(int)  # 進捗状況
    finished_generation = Signal(str)  # 生成完了時
    error = Signal(str)  # エラー発生時
    
    def __init__(self, client: GeminiClient, image_path: str, prompt: str):
        """
        初期化
        
        Args:
            client: Gemini APIクライアント
            image_path: 入力画像のパス
            prompt: 生成プロンプト
        """
        super().__init__()
        self.client = client
        self.image_path = image_path
        self.prompt = prompt
        self.result_path = None
    
    def run(self):
        """スレッド実行時の処理"""
        try:
            # 進捗状況の初期化
            self.progress.emit(10)
            
            # 画像のアップロード
            self.progress.emit(30)
            image_file = self.client.upload_image(self.image_path)
            
            # 一時ファイルの作成（生成結果の保存用）
            _, temp_file = tempfile.mkstemp(suffix=".png")
            self.result_path = temp_file
            
            # 生成処理
            self.progress.emit(50)
            
            image_saved = False
            for i, chunk in enumerate(self.client.generate_image(image_file, self.prompt)):
                # 進捗状況の更新（50%〜90%）
                progress_value = min(90, 50 + i * 5)
                self.progress.emit(progress_value)
                
                # 画像データが含まれている場合は保存
                if self.client.save_generated_image(chunk, self.result_path):
                    image_saved = True
                    break
            
            # 画像が保存されなかった場合はエラー
            if not image_saved:
                raise Exception("生成された画像データがありません")
            
            # 完了
            self.progress.emit(100)
            self.finished_generation.emit(self.result_path)
            
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""
    
    def __init__(self, parent=None):
        """初期化"""
        super().__init__(parent)
        
        self.input_image_path = None
        self.output_image_path = None
        self.current_prompt = ""
        
        # APIクライアントの初期化
        self.client = GeminiClient()
        
        # 履歴管理の初期化
        self.history_manager = HistoryManager()
        
        # 保存先ディレクトリの作成
        create_output_directory()
        
        # UIのセットアップ
        self._setup_ui()
        
        # 履歴の読み込み
        self._load_history()
    
    def _setup_ui(self) -> None:
        """UI部品の初期化"""
        # ウィンドウ設定
        self.setWindowTitle("GeminiReImage")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        main_layout = QVBoxLayout(central_widget)
        
        # 上部レイアウト: 画像パネル部分
        top_layout = QHBoxLayout()
        
        # 入力画像パネル
        self.input_panel = ImagePanel("入力画像", is_input=True)
        self.input_panel.image_dropped.connect(self._on_image_dropped)
        top_layout.addWidget(self.input_panel)
        
        # 出力画像パネル
        self.output_panel = ImagePanel("生成結果", is_input=False)
        self.output_panel.image_dropped.connect(self._on_image_dropped)
        top_layout.addWidget(self.output_panel)
        
        main_layout.addLayout(top_layout)
        
        # 下部レイアウト: プロンプトと履歴
        bottom_splitter = QSplitter(Qt.Vertical)
        
        # プロンプトパネル
        self.prompt_panel = PromptPanel()
        self.prompt_panel.generate_requested.connect(self._on_generate_requested)
        bottom_splitter.addWidget(self.prompt_panel)
        
        # 履歴パネル
        self.history_panel = HistoryPanel()
        self.history_panel.reuse_entry.connect(self._on_history_reuse)
        bottom_splitter.addWidget(self.history_panel)
        
        # スプリッターの初期サイズ比率の設定
        bottom_splitter.setSizes([200, 300])
        
        main_layout.addWidget(bottom_splitter)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
    
    def _load_history(self) -> None:
        """履歴の読み込みと表示"""
        entries = self.history_manager.get_history()
        self.history_panel.update_history(entries)
    
    def _on_image_dropped(self, image_path: str) -> None:
        """
        画像がドロップされたときの処理
        
        Args:
            image_path: ドロップされた画像のパス
        """
        if not validate_image_file(image_path):
            QMessageBox.warning(
                self,
                "無効な画像",
                "サポートされていない形式か、サイズが大きすぎます。\n"
                "JPG, PNG, WEBP形式で4MB以下の画像を使用してください。"
            )
            return
        
        # 入力画像パネルに表示
        self.input_panel.set_image(image_path)
        self.input_image_path = image_path
        
        # 出力画像パネルをクリア
        self.output_panel.clear_image()
        self.output_image_path = None
    
    def _on_generate_requested(self, prompt: str) -> None:
        """
        生成ボタンが押されたときの処理
        
        Args:
            prompt: 入力されたプロンプト
        """
        if not self.input_image_path:
            QMessageBox.warning(
                self,
                "入力画像がありません",
                "まず画像をドロップしてください。"
            )
            return
        
        # 現在のプロンプトを保存
        self.current_prompt = prompt
        
        # プログレスバーの表示
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # ウィジェットの無効化
        self._set_widgets_enabled(False)
        
        # 生成スレッドの開始
        self.generate_thread = GenerateImageThread(
            self.client, self.input_image_path, prompt
        )
        self.generate_thread.progress.connect(self._on_generation_progress)
        self.generate_thread.finished_generation.connect(self._on_generation_finished)
        self.generate_thread.error.connect(self._on_generation_error)
        self.generate_thread.start()
    
    def _on_generation_progress(self, value: int) -> None:
        """
        生成中の進捗状況の更新
        
        Args:
            value: 進捗値（0-100）
        """
        self.progress_bar.setValue(value)
        QApplication.processEvents()
    
    def _on_generation_finished(self, result_path: str) -> None:
        """
        生成完了時の処理
        
        Args:
            result_path: 生成結果の一時ファイルパス
        """
        # 生成結果をPicturesフォルダにコピー
        try:
            permanent_path = save_image_copy(
                result_path, self.current_prompt, is_original=False
            )
            
            # 入力画像も保存（初回のみ）
            if not Path(self.input_image_path).parent.samefile(PICTURES_DIR):
                saved_input_path = save_image_copy(
                    self.input_image_path, self.current_prompt, is_original=True
                )
                self.input_image_path = saved_input_path
            
            # 出力画像パネルに表示
            self.output_panel.set_image(permanent_path)
            self.output_image_path = permanent_path
            
            # 履歴に追加
            self.history_manager.add_entry(
                self.current_prompt,
                self.input_image_path,
                self.output_image_path
            )
            
            # 履歴表示を更新
            self._load_history()
            
            # 一時ファイルの削除
            if os.path.exists(result_path):
                os.remove(result_path)
                
        except Exception as e:
            QMessageBox.warning(
                self,
                "保存エラー",
                f"生成結果の保存中にエラーが発生しました: {str(e)}"
            )
        
        # UI要素の状態を元に戻す
        self._set_widgets_enabled(True)
        
        # プログレスバーを非表示に
        # タイマーで少し待ってから非表示に（完了を確認しやすくするため）
        QTimer.singleShot(500, lambda: self.progress_bar.setVisible(False))
    
    def _on_generation_error(self, error_message: str) -> None:
        """
        生成エラー時の処理
        
        Args:
            error_message: エラーメッセージ
        """
        QMessageBox.critical(
            self,
            "生成エラー",
            f"画像生成中にエラーが発生しました:\n{error_message}"
        )
        
        # UI要素の状態を元に戻す
        self._set_widgets_enabled(True)
        
        # プログレスバーを非表示に
        self.progress_bar.setVisible(False)
    
    def _on_history_reuse(self, entry: Dict[str, Any]) -> None:
        """
        履歴から再利用する処理
        
        Args:
            entry: 再利用する履歴エントリ
        """
        # 入力画像パスのファイル存在確認
        input_path = entry["input_image"]
        if not Path(input_path).exists():
            QMessageBox.warning(
                self,
                "ファイルが見つかりません",
                f"入力画像が見つかりません: {input_path}"
            )
            return
        
        # 入力画像を設定
        self.input_panel.set_image(input_path)
        self.input_image_path = input_path
        
        # 出力画像を設定（存在する場合）
        output_path = entry["output_image"]
        if Path(output_path).exists():
            self.output_panel.set_image(output_path)
            self.output_image_path = output_path
        else:
            self.output_panel.clear_image()
            self.output_image_path = None
        
        # プロンプトを設定
        self.prompt_panel.set_prompt(entry["prompt"])
    
    def _set_widgets_enabled(self, enabled: bool) -> None:
        """
        UI要素の有効/無効切り替え
        
        Args:
            enabled: 有効にするならTrue
        """
        self.prompt_panel.setEnabled(enabled)
        self.history_panel.setEnabled(enabled) 