import os
import json
import datetime
from utils.config import Config
from utils.file_manager import FileManager

class ThreadManager:
    def __init__(self):
        """スレッド管理の初期化"""
        self.threads = {}  # thread_id をキーとした辞書
        self.current_thread_id = None
        self._load_existing_threads()
        
        # 既存のスレッドがなければ新規作成
        if not self.threads:
            self.create_new_thread()
    
    def _load_existing_threads(self):
        """既存のスレッドを読み込み"""
        thread_ids = FileManager.get_all_thread_ids()
        for thread_id in thread_ids:
            thread_data = FileManager.load_thread_data(thread_id)
            if thread_data:
                self.threads[thread_id] = thread_data
        
        # 既存のスレッドがあれば最初のスレッドを現在のスレッドに設定
        if thread_ids:
            self.current_thread_id = thread_ids[0]
    
    def create_new_thread(self, title="新規会話"):
        """新しいスレッドを作成"""
        thread_id = f"thread_{len(self.threads) + 1:02d}"
        current_time = datetime.datetime.now().isoformat()
        
        thread_data = {
            "thread_id": thread_id,
            "created_at": current_time,
            "last_updated_at": current_time,
            "title": title,
            "conversations": [],
            "latest_image_path": None
        }
        
        self.threads[thread_id] = thread_data
        self.current_thread_id = thread_id
        
        # スレッドデータを保存
        FileManager.save_thread_data(thread_id, thread_data)
        
        return thread_id
    
    def get_current_thread(self):
        """現在のスレッドデータを取得"""
        if not self.current_thread_id or self.current_thread_id not in self.threads:
            return None
        return self.threads[self.current_thread_id]
    
    def set_current_thread(self, thread_id):
        """現在のスレッドを設定"""
        if thread_id in self.threads:
            self.current_thread_id = thread_id
            return True
        return False
    
    def add_message(self, role, content, image_path=None):
        """メッセージを追加"""
        if not self.current_thread_id:
            return False
        
        thread = self.threads[self.current_thread_id]
        current_time = datetime.datetime.now().isoformat()
        
        message_id = len(thread["conversations"]) + 1
        message = {
            "message_id": message_id,
            "timestamp": current_time,
            "role": role,
            "content": content
        }
        
        if image_path:
            message["image_path"] = image_path
            # 最新の画像パスを更新
            thread["latest_image_path"] = image_path
        
        thread["conversations"].append(message)
        thread["last_updated_at"] = current_time
        
        # スレッドデータを保存
        FileManager.save_thread_data(self.current_thread_id, thread)
        
        return message_id
    
    def get_thread_titles(self):
        """全スレッドのタイトルと識別子を取得"""
        return {thread_id: data["title"] for thread_id, data in self.threads.items()}
    
    def get_conversation_history(self):
        """現在のスレッドの会話履歴を取得"""
        if not self.current_thread_id:
            return []
        
        thread = self.threads[self.current_thread_id]
        return thread["conversations"]
    
    def get_latest_image_path(self):
        """現在のスレッドの最新画像パスを取得"""
        if not self.current_thread_id:
            return None
            
        thread = self.threads[self.current_thread_id]
        return thread.get("latest_image_path")
    
    def update_thread_title(self, title):
        """現在のスレッドのタイトルを更新"""
        if not self.current_thread_id:
            return False
            
        thread = self.threads[self.current_thread_id]
        thread["title"] = title
        
        # スレッドデータを保存
        FileManager.save_thread_data(self.current_thread_id, thread)
        return True
