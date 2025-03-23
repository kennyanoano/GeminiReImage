import os
import json
import shutil
from datetime import datetime
from PIL import Image
from utils.config import Config
import glob

class FileManager:
    @staticmethod
    def get_image_save_path(thread_id, edit_number=None):
        """画像ファイルの保存パスを取得"""
        base_dir = Config.SAVE_DIRECTORY
        if edit_number is not None:
            # 編集番号が指定されている場合は通常の保存パス
            return os.path.join(base_dir, f"{thread_id}_edit_{edit_number:02d}.png")
        else:
            # 編集番号が指定されていない場合は最新の編集結果
            return os.path.join(base_dir, f"{thread_id}_latest.png")
    
    @staticmethod
    def save_image(image, filename=None, thread_id=None):
        """画像を保存する"""
        try:
            # 保存ディレクトリの設定
            base_dir = Config.SAVE_DIRECTORY
            
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
            
            # ファイル名が指定されていない場合は自動生成
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"gemini_img_{timestamp}.png"
            
            # threadIDが指定されている場合はスレッドフォルダに保存
            if thread_id:
                thread_dir = os.path.join(base_dir, "threads", thread_id)
                os.makedirs(thread_dir, exist_ok=True)
                file_path = os.path.join(thread_dir, filename)
            else:
                file_path = os.path.join(base_dir, filename)
            
            # PILImageオブジェクトを保存
            image.save(file_path)
            print(f"画像を保存しました: {file_path}")
            
            return file_path
        except Exception as e:
            print(f"画像保存エラー: {e}")
            return None
    
    @staticmethod
    def save_thread_data(thread_id, thread_data):
        """スレッドデータをJSONファイルとして保存"""
        try:
            threads_dir = Config.THREADS_DIRECTORY
            os.makedirs(threads_dir, exist_ok=True)
            
            file_path = os.path.join(threads_dir, f"{thread_id}.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(thread_data, f, ensure_ascii=False, indent=2)
            
            print(f"スレッドデータを保存: {file_path}")
            return True
        except Exception as e:
            print(f"スレッドデータ保存エラー: {e}")
            return False
    
    @staticmethod
    def load_thread_data(thread_id):
        """スレッドデータをJSONファイルから読み込む"""
        try:
            threads_dir = Config.THREADS_DIRECTORY
            file_path = os.path.join(threads_dir, f"{thread_id}.json")
            
            if not os.path.exists(file_path):
                print(f"スレッドデータが存在しません: {thread_id}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                thread_data = json.load(f)
            
            print(f"スレッドデータを読み込み: {thread_id}")
            return thread_data
        except Exception as e:
            print(f"スレッドデータ読み込みエラー: {e}")
            return None
    
    @staticmethod
    def get_all_thread_ids():
        """すべてのスレッドIDリストを取得"""
        threads_dir = Config.THREADS_DIRECTORY
        try:
            thread_files = [f for f in os.listdir(threads_dir) if f.endswith(".json")]
            return [os.path.splitext(f)[0] for f in thread_files]
        except Exception as e:
            print(f"スレッドリストの取得に失敗しました: {e}")
            return []
    
    @staticmethod
    def open_save_directory():
        """保存ディレクトリをエクスプローラーで開く"""
        save_dir = Config.SAVE_DIRECTORY
        os.startfile(save_dir)
    
    @staticmethod
    def list_threads():
        """利用可能なスレッドの一覧を取得"""
        try:
            save_dir = Config.THREADS_DIRECTORY
            
            if not os.path.exists(save_dir):
                return []
            
            # JSONファイルを検索
            thread_files = glob.glob(os.path.join(save_dir, "*.json"))
            threads = []
            
            for file_path in thread_files:
                thread_id = os.path.basename(file_path).replace(".json", "")
                threads.append(thread_id)
            
            return threads
        except Exception as e:
            print(f"スレッド一覧取得エラー: {e}")
            return []
