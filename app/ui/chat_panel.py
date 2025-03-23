from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QComboBox, QScrollArea, 
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage

class MessageWidget(QWidget):
    """メッセージ表示用ウィジェット"""
    def __init__(self, message, is_user=True, image=None, parent=None):
        super().__init__(parent)
        self.setup_ui(message, is_user, image)
    
    def setup_ui(self, message, is_user, image):
        """UIの初期化"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # メッセージの背景色とアライメントを設定
        if is_user:
            self.setStyleSheet("background-color: #e1f5fe; border-radius: 10px;")
            layout.setAlignment(Qt.AlignRight)
        else:
            self.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")
            layout.setAlignment(Qt.AlignLeft)
        
        # テキストメッセージ
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(message_label)
        
        # 画像があれば表示
        if image:
            if isinstance(image, str):
                # 画像ファイルパス
                pixmap = QPixmap(image)
                image_label = QLabel()
                image_label.setPixmap(pixmap.scaled(
                    300, 300,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                layout.addWidget(image_label)
            elif isinstance(image, QPixmap) or isinstance(image, QImage):
                # ピクセルマップまたはQImage
                image_label = QLabel()
                if isinstance(image, QImage):
                    pixmap = QPixmap.fromImage(image)
                else:
                    pixmap = image
                image_label.setPixmap(pixmap.scaled(
                    300, 300,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                layout.addWidget(image_label)
        
        self.setLayout(layout)

class ChatPanel(QWidget):
    """チャットパネルコンポーネント"""
    
    # メッセージが送信されたときのシグナル
    message_sent = Signal(str)
    new_thread_requested = Signal()
    thread_changed = Signal(str)
    open_save_dir_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UIの初期化"""
        # メインレイアウト
        main_layout = QVBoxLayout()
        
        # ツールバー
        toolbar_layout = QHBoxLayout()
        
        # スレッドセレクタ
        self.thread_selector = QComboBox()
        self.thread_selector.currentTextChanged.connect(self._on_thread_changed)
        toolbar_layout.addWidget(QLabel("スレッド:"))
        toolbar_layout.addWidget(self.thread_selector)
        
        # 新規会話ボタン
        self.new_thread_button = QPushButton("新規会話")
        self.new_thread_button.clicked.connect(self._on_new_thread_clicked)
        toolbar_layout.addWidget(self.new_thread_button)
        
        # 保存フォルダを開くボタン
        self.open_dir_button = QPushButton("保存フォルダを開く")
        self.open_dir_button.clicked.connect(self._on_open_dir_clicked)
        toolbar_layout.addWidget(self.open_dir_button)
        
        main_layout.addLayout(toolbar_layout)
        
        # メッセージ表示エリア
        self.messages_area = QScrollArea()
        self.messages_area.setWidgetResizable(True)
        self.messages_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setSpacing(10)
        
        self.messages_area.setWidget(self.messages_container)
        main_layout.addWidget(self.messages_area)
        
        # 入力エリア
        input_layout = QHBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("メッセージを入力...")
        self.message_input.setMaximumHeight(80)
        input_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("送信")
        self.send_button.clicked.connect(self._on_send_clicked)
        self.send_button.setEnabled(False)  # 初期状態は無効
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
        # メッセージ入力時にボタンの有効/無効を切り替え
        self.message_input.textChanged.connect(self._on_input_changed)
        
        self.setLayout(main_layout)
    
    def _on_input_changed(self):
        """入力エリアの内容が変わったときの処理"""
        # 入力があれば送信ボタンを有効化
        self.send_button.setEnabled(bool(self.message_input.toPlainText().strip()))
    
    def _on_send_clicked(self):
        """送信ボタンがクリックされたときの処理"""
        message = self.message_input.toPlainText().strip()
        if message:
            self.add_user_message(message)
            self.message_sent.emit(message)
            self.message_input.clear()
    
    def _on_new_thread_clicked(self):
        """新規会話ボタンがクリックされたときの処理"""
        self.new_thread_requested.emit()
    
    def _on_thread_changed(self, thread_name):
        """スレッド選択が変更されたときの処理"""
        if thread_name:
            # 表示名からスレッドIDを取得（辞書逆引き）
            thread_id = None
            for tid, name in self.thread_display_names.items():
                if name == thread_name:
                    thread_id = tid
                    break
            
            if thread_id:
                self.thread_changed.emit(thread_id)
    
    def _on_open_dir_clicked(self):
        """保存フォルダを開くボタンがクリックされたときの処理"""
        self.open_save_dir_requested.emit()
    
    def update_thread_list(self, thread_titles, current_thread_id):
        """スレッドリストを更新"""
        self.thread_display_names = thread_titles
        
        # 現在の選択を保存
        current_selection = self.thread_selector.currentText()
        
        # コンボボックスをクリア
        self.thread_selector.clear()
        
        # スレッドリストを追加
        for thread_id, title in thread_titles.items():
            self.thread_selector.addItem(title)
        
        # 現在のスレッドを選択
        if current_thread_id in thread_titles:
            self.thread_selector.setCurrentText(thread_titles[current_thread_id])
        elif current_selection and current_selection in self.thread_selector.model():
            self.thread_selector.setCurrentText(current_selection)
        
        # シグナルの接続がブロックされていたら解除
        if self.thread_selector.signalsBlocked():
            self.thread_selector.blockSignals(False)
    
    def clear_messages(self):
        """メッセージを全てクリア"""
        for i in reversed(range(self.messages_layout.count())):
            item = self.messages_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    self.messages_layout.removeItem(item)
    
    def add_user_message(self, message, image=None):
        """ユーザーメッセージを追加"""
        self.add_message(message, True, image)
    
    def add_assistant_message(self, message, image=None):
        """アシスタントメッセージを追加"""
        self.add_message(message, False, image)
    
    def add_message(self, message, is_user=True, image=None):
        """メッセージを追加"""
        message_widget = MessageWidget(message, is_user, image)
        
        # メッセージが多すぎる場合は一部削除
        if self.messages_layout.count() > 100:  # 最大メッセージ数
            # 最初の方のメッセージを削除
            for i in range(min(10, self.messages_layout.count() - 90)):
                item = self.messages_layout.itemAt(0)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
                    self.messages_layout.removeItem(item)
        
        self.messages_layout.addWidget(message_widget)
        
        # スクロールエリアを最下部にスクロール
        self.messages_area.verticalScrollBar().setValue(
            self.messages_area.verticalScrollBar().maximum()
        )
    
    def set_processing_state(self, is_processing):
        """処理中の状態を設定"""
        self.send_button.setEnabled(not is_processing)
        self.message_input.setEnabled(not is_processing)
        if is_processing:
            self.send_button.setText("処理中...")
        else:
            self.send_button.setText("送信")
    
    def load_conversation_history(self, conversations):
        """会話履歴をロード"""
        self.clear_messages()
        
        for message in conversations:
            role = message.get("role", "")
            content = message.get("content", "")
            image_path = message.get("image_path")
            
            if role == "user":
                self.add_user_message(content, image_path)
            elif role == "assistant":
                self.add_assistant_message(content, image_path)
