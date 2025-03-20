"""
画像表示用のパネルコンポーネント
"""
from typing import Optional, Callable
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent

from config.settings import IMAGE_PANEL_SIZE
from src.utils.image_processor import scale_pixmap, validate_image_file


class ImagePanel(QWidget):
    """画像表示パネルクラス"""
    
    # シグナル定義
    image_dropped = Signal(str)  # 画像がドロップされたとき
    
    def __init__(self, title: str, is_input: bool = True, parent=None):
        """
        初期化
        
        Args:
            title: パネルのタイトル
            is_input: 入力パネルならTrue、出力パネルならFalse
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.is_input = is_input
        self.image_path = None
        self.pixmap = None
        
        self._setup_ui(title)
    
    def _setup_ui(self, title: str) -> None:
        """UI部品の初期化"""
        self.setAcceptDrops(True)  # ドラッグ&ドロップを有効化
        
        # レイアウト設定
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 画像表示部分
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(QSize(IMAGE_PANEL_SIZE, IMAGE_PANEL_SIZE))
        self.image_label.setMaximumSize(QSize(IMAGE_PANEL_SIZE, IMAGE_PANEL_SIZE))
        self.image_label.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #ccc;"
        )
        self.image_label.setText("ここに画像をドロップ")
        layout.addWidget(self.image_label)
        
        # 出力パネルの場合は「入力画像にする」ボタンを表示
        if not self.is_input:
            button_layout = QHBoxLayout()
            self.reuse_button = QPushButton("入力画像にする")
            self.reuse_button.setEnabled(False)
            self.reuse_button.clicked.connect(self._on_reuse_clicked)
            button_layout.addWidget(self.reuse_button)
            layout.addLayout(button_layout)
    
    def _on_reuse_clicked(self) -> None:
        """再利用ボタンがクリックされたとき"""
        if self.image_path:
            self.image_dropped.emit(self.image_path)
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """ドラッグが入ってきたときのイベント"""
        if event.mimeData().hasUrls() and self.is_input:
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent) -> None:
        """ドロップされたときのイベント"""
        if not self.is_input:
            return
            
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            
            # 画像ファイルの検証
            if validate_image_file(file_path):
                self.set_image(file_path)
                self.image_dropped.emit(file_path)
                break
    
    def set_image(self, image_path: str) -> None:
        """
        画像を設定
        
        Args:
            image_path: 画像ファイルのパス
        """
        if not Path(image_path).exists():
            return
            
        self.image_path = image_path
        self.pixmap = QPixmap(image_path)
        
        # サイズ調整
        scaled_pixmap = scale_pixmap(
            self.pixmap, 
            QSize(IMAGE_PANEL_SIZE, IMAGE_PANEL_SIZE)
        )
        
        self.image_label.setPixmap(scaled_pixmap)
        
        # 出力パネルの場合、再利用ボタンを有効化
        if not self.is_input and hasattr(self, 'reuse_button'):
            self.reuse_button.setEnabled(True)
    
    def clear_image(self) -> None:
        """画像表示をクリア"""
        self.image_path = None
        self.pixmap = None
        self.image_label.clear()
        self.image_label.setText("ここに画像をドロップ")
        
        # 出力パネルの場合、再利用ボタンを無効化
        if not self.is_input and hasattr(self, 'reuse_button'):
            self.reuse_button.setEnabled(False) 