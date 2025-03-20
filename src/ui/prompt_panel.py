"""
プロンプト入力用のパネルコンポーネント
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, Slot

from config.settings import MAX_PROMPT_LENGTH


class PromptPanel(QWidget):
    """プロンプト入力パネルクラス"""
    
    # シグナル定義
    generate_requested = Signal(str)  # 生成ボタンが押されたとき
    
    def __init__(self, parent=None):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """UI部品の初期化"""
        # レイアウト
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel("プロンプト入力:")
        layout.addWidget(title_label)
        
        # テキスト入力エリア
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("画像の変更内容を入力してください")
        self.prompt_text.setMinimumHeight(80)  # 最低3行表示
        self.prompt_text.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.prompt_text)
        
        # 文字数カウンター
        self.counter_label = QLabel(f"0 / {MAX_PROMPT_LENGTH}")
        self.counter_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.counter_label)
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        
        # 生成ボタン
        self.generate_button = QPushButton("生成")
        self.generate_button.setEnabled(False)  # 初期状態は無効化
        self.generate_button.clicked.connect(self._on_generate_clicked)
        button_layout.addWidget(self.generate_button)
        
        # クリアボタン
        self.clear_button = QPushButton("クリア")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
    
    def _on_text_changed(self) -> None:
        """テキストが変更されたときの処理"""
        text = self.prompt_text.toPlainText()
        count = len(text)
        
        # 文字数表示更新
        self.counter_label.setText(f"{count} / {MAX_PROMPT_LENGTH}")
        
        # 最大文字数を超えた場合はカットして選択位置を保持
        if count > MAX_PROMPT_LENGTH:
            cursor = self.prompt_text.textCursor()
            position = cursor.position()
            overflow = count - MAX_PROMPT_LENGTH
            new_position = max(0, position - overflow)
            
            # テキストをカット
            self.prompt_text.setPlainText(text[:MAX_PROMPT_LENGTH])
            
            # カーソル位置を復元
            cursor.setPosition(new_position)
            self.prompt_text.setTextCursor(cursor)
        
        # 生成ボタンの有効/無効を切り替え
        self.generate_button.setEnabled(bool(text.strip()))
    
    def _on_generate_clicked(self) -> None:
        """生成ボタンがクリックされたとき"""
        text = self.prompt_text.toPlainText().strip()
        if text:
            self.generate_requested.emit(text)
    
    def _on_clear_clicked(self) -> None:
        """クリアボタンがクリックされたとき"""
        self.prompt_text.clear()
    
    def get_prompt(self) -> str:
        """
        現在のプロンプトテキストを取得
        
        Returns:
            プロンプトテキスト
        """
        return self.prompt_text.toPlainText().strip()
    
    def set_prompt(self, text: str) -> None:
        """
        プロンプトテキストを設定
        
        Args:
            text: 設定するテキスト
        """
        self.prompt_text.setPlainText(text) 