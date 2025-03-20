"""
Gemini APIとの通信を行うクライアントモジュール
"""
import os
import base64
import mimetypes
import certifi
import httplib2
from pathlib import Path
from typing import Optional, Tuple, Generator, Dict, Any
import google.generativeai as genai
from google.genai import types

from config.settings import GEMINI_MODEL, API_TIMEOUT


class GeminiClient:
    """Gemini APIクライアントクラス"""
    
    def __init__(self):
        """APIクライアントの初期化と認証設定"""
        self._configure_ssl()
        self._setup_api()
        
    def _configure_ssl(self):
        """SSL証明書の設定"""
        # 会社の証明書がある場合は使用、なければデフォルトを使用
        cert_path = os.environ.get("SSL_CERT_FILE")
        if cert_path and Path(cert_path).exists():
            httplib2.CA_CERTS = str(Path(cert_path))
            print(f"DEBUG: Using company SSL certificate: {cert_path}")
        else:
            default_cert = certifi.where()
            os.environ["SSL_CERT_FILE"] = default_cert
            os.environ["REQUESTS_CA_BUNDLE"] = default_cert
            print(f"DEBUG: Using system default certificate: {default_cert}")
    
    def _setup_api(self):
        """APIキーの設定と初期化"""
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEYが環境変数に設定されていません")
        
        # クライアントの初期化 - gemini_api.pyと同じ
        genai.configure(api_key=api_key, transport="rest")
        print("DEBUG: Gemini API configured")
    
    def upload_image(self, image_path: str) -> Any:
        """画像をGemini APIにアップロード
        
        Args:
            image_path: 画像ファイルのパス
            
        Returns:
            アップロードされたファイルオブジェクト
        """
        # gemini_api.pyからそのままコピー
        print(f"DEBUG: Starting upload_to_gemini for path: {image_path}")
        
        # MIMEタイプの推測
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            mime_type = "image/jpeg"  # Default to JPEG
            print("DEBUG: MIME type not provided, defaulting to 'image/jpeg'")
        else:
            print(f"DEBUG: Provided MIME type: {mime_type}")

        # ファイルの存在確認
        print(f"DEBUG: Checking if file exists at: {image_path}")
        if not Path(image_path).exists():
            print(f"DEBUG: File not found at: {image_path}")
            raise FileNotFoundError(f"ファイルが見つかりません: {image_path}")

        try:
            print("DEBUG: Attempting to upload file...")
            file = genai.upload_file(image_path, mime_type=mime_type)
            print(f"DEBUG: Successfully uploaded file '{file.display_name}' as: {file.uri}")
            return file
        except Exception as e:
            print(f"DEBUG: Exception occurred during upload: {str(e)}")
            raise Exception(f"画像アップロード中にエラーが発生しました: {str(e)}")
    
    def generate_image(self, 
                       image_file: Any, 
                       prompt: str, 
                       callback=None) -> Generator[Dict[str, Any], None, None]:
        """画像生成のリクエストを送信し、ストリーミングレスポンスを返す
        
        Args:
            image_file: アップロードされたファイルオブジェクト
            prompt: 画像生成のためのプロンプト
            callback: 進捗通知用のコールバック関数（オプション）
            
        Returns:
            生成結果のストリーム
        """
        # モデルの初期化
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)
        
        # 入力コンテンツの作成
        contents = [
            {
                "role": "user",
                "parts": [
                    {"file_data": {"file_uri": image_file.uri, "mime_type": image_file.mime_type}},
                    {"text": prompt}
                ]
            }
        ]
        
        # 生成設定
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        
        try:
            print(f"DEBUG: Starting image generation with prompt: {prompt}")
            # ストリーミングリクエスト送信
            stream = model.generate_content(
                contents=contents,
                generation_config=generation_config,
                stream=True
            )
            
            # ストリームの処理
            for chunk in stream:
                # コールバックがあれば呼び出し
                if callback:
                    callback(chunk)
                
                print(f"DEBUG: Got chunk: {chunk}")
                yield chunk
                
        except Exception as e:
            print(f"DEBUG: Error in generate_image: {str(e)}")
            raise Exception(f"画像生成中にエラーが発生しました: {str(e)}")
    
    def save_generated_image(self, chunk: Any, file_path: str) -> bool:
        """生成された画像を保存
        
        Args:
            chunk: 画像データを含むレスポンスチャンク
            file_path: 保存先のファイルパス
            
        Returns:
            保存成功時はTrue
        """
        try:
            # 画像データを保存
            print(f"DEBUG: Checking chunk for image data: {chunk}")
            
            # chunksの構造を確認（google.generativeaiを使った場合）
            if hasattr(chunk, 'parts'):
                for part in chunk.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        with open(file_path, "wb") as f:
                            f.write(part.inline_data.data)
                        print(f"DEBUG: Saved generated image to: {file_path}")
                        return True
            
            print("DEBUG: No image data found in chunk")
            return False
        except Exception as e:
            print(f"DEBUG: Error in save_generated_image: {str(e)}")
            raise Exception(f"画像保存中にエラーが発生しました: {str(e)}") 