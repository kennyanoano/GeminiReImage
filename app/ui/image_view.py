from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFileDialog, QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt, Signal, QMimeData

class ImageView(QWidget):
    """画像表示コンポーネント"""
    
    # 画像が読み込まれたときのシグナル
    image_loaded = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_path = None
        self.setup_ui()
    
    def setup_ui(self):
        """UIの初期化"""
        # メインレイアウト
        main_layout = QVBoxLayout()
        
        # ツールバー
        toolbar_layout = QHBoxLayout()
        
        # 画像を開くボタン
        self.open_button = QPushButton("画像を開く")
        self.open_button.clicked.connect(self.open_image)
        toolbar_layout.addWidget(self.open_button)
        
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
        # 画像表示領域
        self.image_label = QLabel("ここに画像をドラッグ＆ドロップするか、「画像を開く」をクリックしてください")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet("border: 2px dashed #aaa; border-radius: 5px;")
        main_layout.addWidget(self.image_label)
        
        # ドラッグ＆ドロップの設定
        self.setAcceptDrops(True)
        
        self.setLayout(main_layout)
    
    def set_image(self, image_path):
        """画像を設定"""
        if not image_path:
            return False
            
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"エラー: 画像を読み込めませんでした: {image_path}")
            return False
            
        # 表示領域のサイズに合わせてリサイズ
        pixmap = pixmap.scaled(
            self.image_label.width(), 
            self.image_label.height(),
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(pixmap)
        self.image_path = image_path
        self.image_loaded.emit(image_path)
        return True
    
    def set_pil_image(self, pil_image):
        """PIL画像を設定"""
        if not pil_image:
            return False
            
        # PIL ImageをQImageに変換
        img = pil_image.convert("RGBA")
        data = img.tobytes("raw", "RGBA")
        qimage = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
        
        # QImageをQPixmapに変換
        pixmap = QPixmap.fromImage(qimage)
        
        # 表示領域のサイズに合わせてリサイズ
        pixmap = pixmap.scaled(
            self.image_label.width(), 
            self.image_label.height(),
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(pixmap)
        return True
    
    def open_image(self):
        """画像をファイルダイアログで開く"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "画像を開く",
            "",
            "画像ファイル (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.set_image(file_path)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """ドラッグ開始イベント"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """ドロップイベント"""
        mime_data = event.mimeData()
        
        if mime_data.hasUrls():
            url = mime_data.urls()[0]
            file_path = url.toLocalFile()
            
            # 画像ファイルかチェック
            file_extension = file_path.lower().split('.')[-1]
            if file_extension in ['png', 'jpg', 'jpeg', 'bmp', 'gif']:
                self.set_image(file_path)
                event.acceptProposedAction()
    
    def resizeEvent(self, event):
        """リサイズイベント - 画像を再表示"""
        super().resizeEvent(event)
        
        if hasattr(self, 'image_path') and self.image_path:
            pixmap = QPixmap(self.image_path)
            pixmap = pixmap.scaled(
                self.image_label.width(), 
                self.image_label.height(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
    
    def get_image_path(self):
        """現在表示中の画像パスを取得"""
        return self.image_path
