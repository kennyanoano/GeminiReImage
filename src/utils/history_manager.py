"""
プロンプト履歴を管理するユーティリティモジュール
"""
import os
import json
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from config.settings import HISTORY_FILE, HISTORY_MAX_ITEMS


class HistoryManager:
    """プロンプト履歴の管理クラス"""
    
    def __init__(self):
        """履歴管理の初期化"""
        self.history_file = HISTORY_FILE
        self.history_data = {"history": []}
        self._load_history()
    
    def _load_history(self) -> None:
        """履歴ファイルの読み込み"""
        # 履歴ファイルのディレクトリがなければ作成
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                # ファイルが破損している場合は新規作成
                self.history_data = {"history": []}
                self._save_history()
    
    def _save_history(self) -> None:
        """履歴ファイルへの保存"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"履歴ファイルの保存中にエラーが発生しました: {str(e)}")
    
    def add_entry(self, prompt: str, input_image: str, output_image: str) -> str:
        """
        履歴エントリの追加
        
        Args:
            prompt: 使用されたプロンプト
            input_image: 入力画像のパス
            output_image: 出力画像のパス
            
        Returns:
            追加されたエントリのID
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = {
            "id": entry_id,
            "timestamp": timestamp,
            "prompt": prompt,
            "input_image": str(Path(input_image).absolute()),
            "output_image": str(Path(output_image).absolute())
        }
        
        # 履歴の先頭に追加
        self.history_data["history"].insert(0, entry)
        
        # 最大件数を超えた場合は古いエントリを削除
        if len(self.history_data["history"]) > HISTORY_MAX_ITEMS:
            self.history_data["history"] = self.history_data["history"][:HISTORY_MAX_ITEMS]
        
        # 保存
        self._save_history()
        
        return entry_id
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        履歴エントリの取得
        
        Args:
            limit: 取得する最大件数
            
        Returns:
            履歴エントリのリスト
        """
        entries = self.history_data["history"]
        if limit:
            entries = entries[:limit]
        return entries
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        特定のIDの履歴エントリを取得
        
        Args:
            entry_id: 取得するエントリのID
            
        Returns:
            履歴エントリまたはNone
        """
        for entry in self.history_data["history"]:
            if entry["id"] == entry_id:
                return entry
        return None
    
    def clear_history(self) -> None:
        """履歴の全消去"""
        self.history_data = {"history": []}
        self._save_history() 