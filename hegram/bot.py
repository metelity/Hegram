import requests
import time
import os
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from typing import Union, List, Dict, Optional

class Bot:
    def __init__(self, token: str, workers: int = 4):
        self.token = token
        self.routes = {}
        self.callbacks = {}
        self.executor = ThreadPoolExecutor(max_workers=workers)
        print("Hello there, are you happy to Hegram?")

    def function(self, command: str):
        def decorator(func):
            self.routes[command] = func
            return func
        return decorator

    def callback(self, callback_data: str):
        def decorator(func):
            self.callbacks[callback_data] = func
            return func
        return decorator

    def runing(self):
        os.system("clear")
        print("[!] Warn: token checking...")
        
        # Проверка токена перед запуском
        if not self._validate_token():
            print("[!] Token failed validation")
            return
        
        time.sleep(1.1)
        os.system("clear")
        print("All processes are launched\nHegram working (@2025)")
        
        offset = 0
        while True:
            try:
                updates = self._get_updates(offset)
                for update in updates:
                    offset = update["update_id"] + 1
                    self.executor.submit(self._handle_update, update)
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(0.1)

    def _validate_token(self) -> bool:
        """Проверяет валидность токена бота"""
        url = f"https://api.telegram.org/bot{self.token}/getMe"
        try:
            response = requests.get(url, timeout=10)
            return response.json().get("ok", False)
        except Exception as e:
            print(f"Token validation error: {e}")
            return False

    def _get_updates(self, offset: int) -> list:
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        params = {"offset": offset, "timeout": 20, "limit": 100}
        try:
            response = requests.get(url, params=params, timeout=25)
            return response.json().get("result", [])
        except requests.exceptions.RequestException as e:
            print(f"Update error: {e}")
            return []

    def _handle_update(self, update: dict):
        if "message" in update:
            self._handle_message(update["message"])
        elif "callback_query" in update:
            self._handle_callback(update["callback_query"])

    def _handle_message(self, message: dict):
        text = message.get("text", "")
        if not text:
            return
            
        parts = text.split()
        command = parts[0]
        
        for registered_command, handler in self.routes.items():
            if command == registered_command:
                try:
                    handler(message)
                except Exception as e:
                    print(f"Handler error: {e}")
                return

    def _handle_callback(self, callback_query: dict):
        data = callback_query.get("data", "")
        for callback_data, handler in self.callbacks.items():
            if data == callback_data:
                try:
                    handler(callback_query)
                except Exception as e:
                    print(f"Callback error: {e}")

    # Message methods
    def send_message(self, 
                   chat_id: int, 
                   text: str, 
                   reply_markup: Optional[dict] = None,
                   parse_mode: Optional[str] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        if reply_markup: data["reply_markup"] = reply_markup
        if parse_mode: data["parse_mode"] = parse_mode
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Send message error: {e}")
            return {}

    def edit_message(self,
                    chat_id: int,
                    message_id: int,
                    text: str,
                    reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/editMessageText"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
        if reply_markup: data["reply_markup"] = reply_markup
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Edit message error: {e}")
            return {}

    # Media methods
    def send_photo(self,
                 chat_id: int,
                 photo: Union[str, bytes],
                 caption: Optional[str] = None,
                 reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        data = {"chat_id": chat_id}
        files = None
        
        try:
            if isinstance(photo, str):
                if photo.startswith(('http://', 'https://')):
                    data['photo'] = photo
                else:
                    with open(photo, 'rb') as f:
                        files = {'photo': f}
                        if caption: data['caption'] = caption
                        if reply_markup: data['reply_markup'] = reply_markup
                        return requests.post(url, data=data, files=files).json()
            else:
                files = {'photo': photo}
            
            if caption: data['caption'] = caption
            if reply_markup: data['reply_markup'] = reply_markup
            return requests.post(url, data=data, files=files).json()
        except Exception as e:
            print(f"Send photo error: {e}")
            return {}

    def send_document(self,
                    chat_id: int,
                    document: Union[str, bytes],
                    caption: Optional[str] = None,
                    reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendDocument"
        data = {"chat_id": chat_id}
        files = None
        
        try:
            if isinstance(document, str):
                with open(document, 'rb') as f:
                    files = {'document': f}
                    if caption: data['caption'] = caption
                    if reply_markup: data['reply_markup'] = reply_markup
                    return requests.post(url, data=data, files=files).json()
            else:
                files = {'document': document}
            
            if caption: data['caption'] = caption
            if reply_markup: data['reply_markup'] = reply_markup
            return requests.post(url, data=data, files=files).json()
        except Exception as e:
            print(f"Send document error: {e}")
            return {}

    # Keyboard methods
    def create_inline_keyboard(self, buttons: List[List[dict]]) -> dict:
        return {"inline_keyboard": buttons}

    def create_reply_keyboard(self, 
                            buttons: List[List[str]],
                            resize_keyboard: bool = True,
                            one_time_keyboard: bool = False) -> dict:
        return {
            "keyboard": [[{"text": btn} for btn in row] for row in buttons],
            "resize_keyboard": resize_keyboard,
            "one_time_keyboard": one_time_keyboard
        }

    def answer_callback(self,
                      callback_query_id: str,
                      text: Optional[str] = None,
                      show_alert: bool = False) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/answerCallbackQuery"
        data = {
            "callback_query_id": callback_query_id,
            "show_alert": show_alert
        }
        if text: data["text"] = text
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Callback answer error: {e}")
            return {}
            
    def delete_message(self, chat_id: int, message_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/deleteMessage"
        data = {
            "chat_id": chat_id,
            "message_id": message_id
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Delete message error: {e}")
            return {}