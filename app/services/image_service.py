import os
from PIL import Image
from utils.file_manager import FileManager
from utils.config import Config

class ImageService:
    def __init__(self, thread_manager):
        """画像処理サービスの初期化"""
        self.thread_manager = thread_manager
        self.current_image = None
        self.current_image_path = None
    
    def load_image(self, image_path):
        """画像をロード"""
        try:
            if not os.path.exists(image_path):
                print(f"エラー: 画像が見つかりません: {image_path}")
                return False
                
            # PIL Imageとして読み込み
            image = Image.open(image_path)
            self.current_image = image
            self.current_image_path = image_path
            
            print(f"画像をロードしました: {image_path}")
            return True
        except Exception as e:
            print(f"画像のロード中にエラーが発生しました: {e}")
            return False
    
    def load_latest_image(self):
        """現在のスレッドの最新画像をロード"""
        image_path = self.thread_manager.get_latest_image_path()
        if image_path and os.path.exists(image_path):
            return self.load_image(image_path)
        return False
    
    def save_edited_image(self, image_data, thread_id=None):
        """編集された画像を保存"""
        if thread_id is None:
            thread_id = self.thread_manager.current_thread_id
            
        if not thread_id:
            print("エラー: スレッドIDが指定されていません")
            return None
            
        # 編集番号を取得（現在の会話数）
        thread = self.thread_manager.get_current_thread()
        if not thread:
            print("エラー: 現在のスレッドが見つかりません")
            return None
            
        edit_number = len(thread["conversations"]) + 1
        
        # 保存パスを取得
        save_path = FileManager.get_image_save_path(thread_id, edit_number)
        latest_path = FileManager.get_image_save_path(thread_id)
        
        # 画像を保存
        if FileManager.save_image(image_data, save_path):
            # 最新の編集結果も保存
            FileManager.save_image(image_data, latest_path)
            
            # 現在の画像を更新
            if isinstance(image_data, Image.Image):
                self.current_image = image_data
            else:
                self.current_image = Image.open(save_path)
                
            self.current_image_path = save_path
            
            return save_path
        
        return None
        
    def get_current_image(self):
        """現在ロードされている画像を取得"""
        return self.current_image
        
    def get_current_image_path(self):
        """現在ロードされている画像のパスを取得"""
        return self.current_image_path
