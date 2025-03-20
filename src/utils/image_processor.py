"""
画像処理関連のユーティリティ関数モジュール
"""
import os
import uuid
import datetime
from pathlib import Path
from typing import Tuple, Optional
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QSize, Qt

from config.settings import PICTURES_DIR, SUPPORTED_FORMATS, MAX_IMAGE_SIZE


def create_output_directory() -> None:
    """画像保存用ディレクトリを作成"""
    if not PICTURES_DIR.exists():
        PICTURES_DIR.mkdir(parents=True, exist_ok=True)


def validate_image_file(file_path: str) -> bool:
    """
    画像ファイルの形式とサイズをチェック
    
    Args:
        file_path: 確認する画像ファイルのパス
        
    Returns:
        有効な画像ファイルならTrue
    """
    path = Path(file_path)
    
    # 拡張子のチェック
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        return False
    
    # ファイルサイズのチェック
    if path.stat().st_size > MAX_IMAGE_SIZE:
        return False
    
    return True


def generate_image_filename(prompt: str, is_original: bool = False) -> str:
    """
    一意なファイル名を生成
    
    Args:
        prompt: プロンプトテキスト
        is_original: 元画像かどうか
        
    Returns:
        生成されたファイル名
    """
    # タイムスタンプ
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # プロンプトの短縮版（最初の10文字）
    short_prompt = prompt[:10].replace(" ", "_")
    
    # UUID生成
    unique_id = str(uuid.uuid4())[:8]
    
    # ファイル名の作成
    img_type = "original" if is_original else "generated"
    filename = f"{timestamp}_{short_prompt}_{img_type}_{unique_id}.png"
    
    return filename


def save_image_copy(source_path: str, prompt: str, is_original: bool = False) -> str:
    """
    元画像をPicturesフォルダにコピー保存
    
    Args:
        source_path: ソース画像のパス
        prompt: プロンプトテキスト
        is_original: 元画像かどうか
        
    Returns:
        保存された画像の絶対パス
    """
    create_output_directory()
    
    # 新しいファイル名を生成
    filename = generate_image_filename(prompt, is_original)
    destination_path = PICTURES_DIR / filename
    
    # ファイルのコピー
    with open(source_path, "rb") as src_file:
        content = src_file.read()
        with open(destination_path, "wb") as dst_file:
            dst_file.write(content)
    
    return str(destination_path.absolute())


def scale_pixmap(pixmap: QPixmap, target_size: QSize) -> QPixmap:
    """
    画像をターゲットサイズに縮小しつつアスペクト比を維持
    
    Args:
        pixmap: 元のピクスマップ
        target_size: 目標サイズ
        
    Returns:
        サイズ調整されたピクスマップ
    """
    return pixmap.scaled(
        target_size, 
        Qt.KeepAspectRatio, 
        Qt.SmoothTransformation
    ) 