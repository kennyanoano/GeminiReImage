"""
履歴表示用のパネルコンポーネント
"""
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal

from config.settings import PROMPT_DISPLAY_LENGTH


class HistoryItemWidget(QFrame):
    """履歴項目ウィジェット"""
    
    # シグナル定義
    reuse_requested = Signal(str)  # 再利用ボタンが押されたとき
    
    def __init__(self, entry: Dict[str, Any], parent=None):
        """
        初期化
        
        Args:
            entry: 履歴エントリ
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.entry_id = entry["id"]
        self.input_image = entry["input_image"]
        self.output_image = entry["output_image"]
        self.prompt = entry["prompt"]
        
        self._setup_ui(entry)
    
    def _setup_ui(self, entry: Dict[str, Any]) -> None:
        """UI部品の初期化"""
        # スタイル設定
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("border: 1px solid #ccc; border-radius: 3px; margin: 2px;")
        
        # レイアウト
        layout = QHBoxLayout(self)
        
        # 日時とプロンプト情報
        info_layout = QVBoxLayout()
        
        # 日時
        date_label = QLabel(entry["timestamp"])
        date_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(date_label)
        
        # プロンプト（短縮表示）
        prompt_short = entry["prompt"]
        if len(prompt_short) > PROMPT_DISPLAY_LENGTH:
            prompt_short = prompt_short[:PROMPT_DISPLAY_LENGTH] + "..."
        prompt_label = QLabel(f'"{prompt_short}"')
        info_layout.addWidget(prompt_label)
        
        layout.addLayout(info_layout, 3)  # 3:1の比率
        
        # 再利用ボタン
        self.reuse_button = QPushButton("再利用")
        self.reuse_button.clicked.connect(self._on_reuse_clicked)
        layout.addWidget(self.reuse_button, 1)  # 3:1の比率
    
    def _on_reuse_clicked(self) -> None:
        """再利用ボタンがクリックされたとき"""
        self.reuse_requested.emit(self.entry_id)


class HistoryPanel(QWidget):
    """履歴表示パネルクラス"""
    
    # シグナル定義
    reuse_entry = Signal(Dict[str, Any])  # 履歴エントリの再利用
    
    def __init__(self, parent=None):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self._setup_ui()
        self.history_items = []
    
    def _setup_ui(self) -> None:
        """UI部品の初期化"""
        # レイアウト
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel("履歴:")
        layout.addWidget(title_label)
        
        # スクロールエリア
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # スクロールエリア内のコンテンツウィジェット
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
    
    def update_history(self, entries: List[Dict[str, Any]]) -> None:
        """
        履歴表示を更新
        
        Args:
            entries: 履歴エントリのリスト
        """
        # 既存の履歴アイテムをクリア
        self.clear_history()
        
        # 新しい履歴アイテムを追加
        for entry in entries:
            history_item = HistoryItemWidget(entry)
            history_item.reuse_requested.connect(self._on_reuse_requested)
            self.content_layout.addWidget(history_item)
            self.history_items.append(history_item)
    
    def clear_history(self) -> None:
        """履歴表示をクリア"""
        for item in self.history_items:
            self.content_layout.removeWidget(item)
            item.deleteLater()
        self.history_items = []
    
    def _on_reuse_requested(self, entry_id: str) -> None:
        """
        再利用リクエストの処理
        
        Args:
            entry_id: 履歴エントリID
        """
        # 該当する履歴アイテムを検索
        for item in self.history_items:
            if item.entry_id == entry_id:
                # エントリ情報を作成
                entry = {
                    "id": item.entry_id,
                    "input_image": item.input_image,
                    "output_image": item.output_image,
                    "prompt": item.prompt
                }
                self.reuse_entry.emit(entry)
                break 