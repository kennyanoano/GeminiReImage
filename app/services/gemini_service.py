import os
import io
import base64
import certifi
import httplib2
from PIL import Image
from google import genai
from utils.config import Config
from datetime import datetime

class GeminiService:
    def __init__(self):
        """Gemini API連携サービスの初期化"""
        self._setup_api()
    
    def _setup_api(self):
        """API初期化とSSL証明書の設定"""
        # APIキーの設定
        api_key = Config.API_KEY
        
        if not api_key:
            print("エラー: Google API キーが設定されていません。")
            return False
        
        # SSL証明書の設定
        cert_path = os.environ.get("SSL_CERT_FILE")
        if cert_path and os.path.exists(cert_path):
            os.environ["SSL_CERT_FILE"] = cert_path
            print(f"SSL証明書を使用: {cert_path}")
        else:
            # 証明書が設定されていない場合、certifiのパスを使用
            default_cert = certifi.where()
            os.environ["SSL_CERT_FILE"] = default_cert
            os.environ["REQUESTS_CA_BUNDLE"] = default_cert
            print(f"標準SSL証明書を使用: {default_cert}")
        
        # HTTPクライアントのCA証明書を設定
        self.http = httplib2.Http(ca_certs=os.environ["SSL_CERT_FILE"])
        
        # 絵を改造させる.pyと同じ方法でクライアント初期化
        try:
            self.client = genai.Client(api_key=api_key)
            print("genai.Client を使用して初期化しました")
        except Exception as e:
            print(f"genai.Client 初期化エラー: {e}")
            self.client = None
            return False
        
        print("Gemini API初期化が完了しました")
        return True
    
    def modify_image(self, image, instruction_text, thread_id=None):
        """画像を指定した指示に基づいて編集する"""
        print(f"画像編集開始: スレッドID={thread_id}, 指示テキスト={instruction_text}")
        
        try:
            # サンプルコードと同じモデル名を使用
            model_name = "gemini-2.0-flash-exp"
            print(f"使用モデル: {model_name}")
            
            # 結果格納用
            result = {"text": "", "image": None}
            
            # 設定オブジェクト - テキストと画像の両方を返すように設定
            print("GenerateContentConfig で設定")
            from google.genai.types import GenerateContentConfig
            config = GenerateContentConfig(response_modalities=['Text', 'Image'])
            
            if self.client:
                try:
                    print("Geminiに改造リクエストを送信中...")
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=[
                            instruction_text,
                            image  # 画像オブジェクトをそのまま使用
                        ],
                        config=config,
                    )
                    
                    print(f"レスポンスタイプ: {type(response)}")
                    
                    # レスポンスから画像とテキストを取り出す（サンプルコードに合わせる）
                    if hasattr(response, 'candidates') and response.candidates:
                        parts = response.candidates[0].content.parts
                        print(f"レスポンスのパート数: {len(parts)}")
                        
                        for i, part in enumerate(parts):
                            if hasattr(part, 'inline_data') and part.inline_data:
                                # 画像データを取得
                                print(f"Part {i} は画像データです")
                                image_data = part.inline_data.data
                                mime_type = part.inline_data.mime_type
                                print(f"MIMEタイプ: {mime_type}")
                                
                                # ファイル拡張子を決定
                                ext = mime_type.split('/')[-1]
                                
                                try:
                                    # サンプルコードと同様のBase64デコード処理
                                    if isinstance(image_data, str):
                                        # 引用符などの余分な文字を削除
                                        if image_data.startswith('"') and image_data.endswith('"'):
                                            image_data = image_data[1:-1]
                                        # Base64デコード
                                        image_bytes = base64.b64decode(image_data)
                                    else:
                                        # すでにバイナリデータの場合
                                        image_bytes = image_data
                                    
                                    # デバッグ情報
                                    print(f"デコード後バイト長: {len(image_bytes)}")
                                    print(f"デコード後バイト先頭: {image_bytes[:20]}")
                                    
                                    # デバッグ用ファイル保存
                                    debug_path = os.path.join(Config.SAVE_DIRECTORY, f"debug_raw.{ext}")
                                    with open(debug_path, "wb") as f:
                                        f.write(image_bytes)
                                    print(f"デバッグ用に生データを保存: {debug_path}")
                                    
                                    # 画像を開く
                                    result_image = Image.open(io.BytesIO(image_bytes))
                                    print(f"画像を正常に開きました: サイズ={result_image.size}, モード={result_image.mode}")
                                    result["image"] = result_image
                                    
                                    # デバッグ用に保存
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    debug_image_path = os.path.join(Config.SAVE_DIRECTORY, f"debug_image_{timestamp}.{ext}")
                                    result_image.save(debug_image_path)
                                    print(f"デバッグ用に画像を保存: {debug_image_path}")
                                    
                                except Exception as img_err:
                                    print(f"画像処理エラー: {img_err}")
                                    import traceback
                                    traceback.print_exc()
                                    
                                    # バイナリ形式で直接保存を試みる（サンプルコードと同様）
                                    try:
                                        if isinstance(image_bytes, bytes):
                                            bin_path = os.path.join(Config.SAVE_DIRECTORY, f"direct_binary_{timestamp}.{ext}")
                                            with open(bin_path, "wb") as f:
                                                f.write(image_bytes)
                                            print(f"バイナリとして直接保存しました: {bin_path}")
                                    except Exception as bin_error:
                                        print(f"バイナリ保存エラー: {bin_error}")
                            
                            elif hasattr(part, 'text') and part.text:
                                # テキストを取得
                                print(f"Part {i} はテキストデータです: {part.text[:50]}...")
                                result["text"] += part.text
                    else:
                        print("レスポンスにcandidatesが含まれていません")
                
                except Exception as e:
                    print(f"Gemini API呼び出しエラー: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("Clientが初期化されていないため、リクエストを送信できません")
            
            # 画像がない場合は、バックアップモデルを試す
            if not result["image"]:
                print("画像が取得できなかったため、画像生成専用モデルで再試行します")
                try:
                    # バックアップはサンプルコードとは異なるAPIを使用
                    backup_model_name = "gemini-2.0-flash-exp-image-generation"
                    print(f"バックアップモデル使用: {backup_model_name}")
                    
                    # genaiモジュールを直接使用
                    import google.generativeai as genai_alt
                    genai_alt.configure(api_key=Config.API_KEY)
                    model = genai_alt.GenerativeModel(backup_model_name)
                    
                    # 設定
                    generation_config = {
                        "temperature": 0.4,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 8192,
                    }
                    
                    # 安全設定を緩和
                    safety_settings = {
                        "harassment": "block_none",
                        "hate_speech": "block_none",
                        "dangerous_content": "block_none"
                    }
                    
                    # バイト配列に変換
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format=image.format or 'PNG')
                    img_byte_arr.seek(0)
                    
                    print("バックアップモデルにリクエスト送信...")
                    response = model.generate_content(
                        [instruction_text, {"mime_type": "image/png", "data": img_byte_arr.getvalue()}],
                        generation_config=generation_config,
                        safety_settings=safety_settings
                    )
                    
                    # レスポンスの処理
                    if hasattr(response, "parts"):
                        parts = response.parts
                        print(f"バックアップモデル: レスポンスのパート数: {len(parts)}")
                        
                        for i, part in enumerate(parts):
                            if hasattr(part, 'inline_data') and part.inline_data:
                                # 画像データを取得
                                print(f"Part {i} は画像データです")
                                image_data = part.inline_data.data
                                
                                try:
                                    # サンプルコードと同様のBase64デコード処理
                                    if isinstance(image_data, str):
                                        # 引用符などの余分な文字を削除
                                        if image_data.startswith('"') and image_data.endswith('"'):
                                            image_data = image_data[1:-1]
                                    
                                    # Base64デコード
                                    image_bytes = base64.b64decode(image_data)
                                    
                                    # 画像を開く
                                    backup_image = Image.open(io.BytesIO(image_bytes))
                                    print(f"バックアップ画像を取得: サイズ={backup_image.size}, モード={backup_image.mode}")
                                    result["image"] = backup_image
                                    
                                    # デバッグ用に保存
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    debug_path = os.path.join(Config.SAVE_DIRECTORY, f"backup_image_{timestamp}.png")
                                    backup_image.save(debug_path)
                                    print(f"バックアップ画像を保存: {debug_path}")
                                    
                                except Exception as img_err:
                                    print(f"バックアップ画像処理エラー: {img_err}")
                    
                    # テキスト応答の処理
                    if hasattr(response, "text") and not result["text"]:
                        result["text"] = response.text
                
                except Exception as backup_err:
                    print(f"バックアップモデルでのリトライ中にエラー: {backup_err}")
                    import traceback
                    traceback.print_exc()
            
            print("画像編集が完了しました")
            if not result["image"]:
                print("警告: 画像データが応答に含まれていませんでした")
            
            return result
            
        except Exception as e:
            print(f"画像編集中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            raise

    def generate_text(self, text_prompt, thread_id=None):
        """テキスト生成リクエスト"""
        # ... existing code ...
