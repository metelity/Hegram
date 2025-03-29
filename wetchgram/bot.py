import requests
import time
import os
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from typing import Union, List, Dict, Optional, Any

class Bot:
    def __init__(self, token: str, workers: int = 4):
        self.token = token
        self.routes = {}
        self.callbacks = {}
        self.executor = ThreadPoolExecutor(max_workers=workers)
        print("Hello, wetchgram - tools tg bot.")

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
        
        if not self._validate_token():
            print("[!] Token failed validation")
            return
        
        time.sleep(1.1)
        os.system("clear")
        print("All processes are launched\nWetchgram working (@2025)")
        
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
        """Validate bot token"""
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

    # ==============================
    # Core Message Methods
    # ==============================
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

    def forward_message(self,
                      chat_id: int,
                      from_chat_id: int,
                      message_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/forwardMessage"
        data = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Forward message error: {e}")
            return {}

    def copy_message(self,
                   chat_id: int,
                   from_chat_id: int,
                   message_id: int,
                   caption: Optional[str] = None,
                   reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/copyMessage"
        data = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id
        }
        if caption: data["caption"] = caption
        if reply_markup: data["reply_markup"] = reply_markup
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Copy message error: {e}")
            return {}

    # ==============================
    # Media Methods
    # ==============================
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

    def send_audio(self,
                 chat_id: int,
                 audio: Union[str, bytes],
                 caption: Optional[str] = None,
                 duration: Optional[int] = None,
                 performer: Optional[str] = None,
                 title: Optional[str] = None,
                 reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendAudio"
        data = {"chat_id": chat_id}
        files = None
        
        try:
            if isinstance(audio, str):
                with open(audio, 'rb') as f:
                    files = {'audio': f}
                    if caption: data['caption'] = caption
                    if duration: data['duration'] = duration
                    if performer: data['performer'] = performer
                    if title: data['title'] = title
                    if reply_markup: data['reply_markup'] = reply_markup
                    return requests.post(url, data=data, files=files).json()
            else:
                files = {'audio': audio}
            
            if caption: data['caption'] = caption
            if duration: data['duration'] = duration
            if performer: data['performer'] = performer
            if title: data['title'] = title
            if reply_markup: data['reply_markup'] = reply_markup
            return requests.post(url, data=data, files=files).json()
        except Exception as e:
            print(f"Send audio error: {e}")
            return {}

    def send_video(self,
                 chat_id: int,
                 video: Union[str, bytes],
                 caption: Optional[str] = None,
                 duration: Optional[int] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendVideo"
        data = {"chat_id": chat_id}
        files = None
        
        try:
            if isinstance(video, str):
                with open(video, 'rb') as f:
                    files = {'video': f}
                    if caption: data['caption'] = caption
                    if duration: data['duration'] = duration
                    if width: data['width'] = width
                    if height: data['height'] = height
                    if reply_markup: data['reply_markup'] = reply_markup
                    return requests.post(url, data=data, files=files).json()
            else:
                files = {'video': video}
            
            if caption: data['caption'] = caption
            if duration: data['duration'] = duration
            if width: data['width'] = width
            if height: data['height'] = height
            if reply_markup: data['reply_markup'] = reply_markup
            return requests.post(url, data=data, files=files).json()
        except Exception as e:
            print(f"Send video error: {e}")
            return {}

    def send_voice(self,
                 chat_id: int,
                 voice: Union[str, bytes],
                 caption: Optional[str] = None,
                 duration: Optional[int] = None,
                 reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendVoice"
        data = {"chat_id": chat_id}
        files = None
        
        try:
            if isinstance(voice, str):
                with open(voice, 'rb') as f:
                    files = {'voice': f}
                    if caption: data['caption'] = caption
                    if duration: data['duration'] = duration
                    if reply_markup: data['reply_markup'] = reply_markup
                    return requests.post(url, data=data, files=files).json()
            else:
                files = {'voice': voice}
            
            if caption: data['caption'] = caption
            if duration: data['duration'] = duration
            if reply_markup: data['reply_markup'] = reply_markup
            return requests.post(url, data=data, files=files).json()
        except Exception as e:
            print(f"Send voice error: {e}")
            return {}

    def send_video_note(self,
                      chat_id: int,
                      video_note: Union[str, bytes],
                      duration: Optional[int] = None,
                      length: Optional[int] = None,
                      reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendVideoNote"
        data = {"chat_id": chat_id}
        files = None
        
        try:
            if isinstance(video_note, str):
                with open(video_note, 'rb') as f:
                    files = {'video_note': f}
                    if duration: data['duration'] = duration
                    if length: data['length'] = length
                    if reply_markup: data['reply_markup'] = reply_markup
                    return requests.post(url, data=data, files=files).json()
            else:
                files = {'video_note': video_note}
            
            if duration: data['duration'] = duration
            if length: data['length'] = length
            if reply_markup: data['reply_markup'] = reply_markup
            return requests.post(url, data=data, files=files).json()
        except Exception as e:
            print(f"Send video note error: {e}")
            return {}

    def send_media_group(self,
                       chat_id: int,
                       media: List[Dict[str, Any]],
                       disable_notification: Optional[bool] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendMediaGroup"
        data = {
            "chat_id": chat_id,
            "media": media
        }
        if disable_notification is not None:
            data["disable_notification"] = disable_notification
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Send media group error: {e}")
            return {}

    def edit_message_media(self,
                         chat_id: int,
                         message_id: int,
                         media: Dict[str, Any],
                         reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/editMessageMedia"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "media": media
        }
        if reply_markup: data["reply_markup"] = reply_markup
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Edit message media error: {e}")
            return {}

    def edit_message_caption(self,
                           chat_id: int,
                           message_id: int,
                           caption: Optional[str] = None,
                           reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/editMessageCaption"
        data = {
            "chat_id": chat_id,
            "message_id": message_id
        }
        if caption: data["caption"] = caption
        if reply_markup: data["reply_markup"] = reply_markup
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Edit message caption error: {e}")
            return {}

    # ==============================
    # Stickers and Dice
    # ==============================
    def send_sticker(self,
                   chat_id: int,
                   sticker: Union[str, bytes],
                   reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendSticker"
        data = {"chat_id": chat_id}
        files = None
        
        try:
            if isinstance(sticker, str):
                if sticker.startswith(('http://', 'https://')):
                    data['sticker'] = sticker
                else:
                    with open(sticker, 'rb') as f:
                        files = {'sticker': f}
                        if reply_markup: data['reply_markup'] = reply_markup
                        return requests.post(url, data=data, files=files).json()
            else:
                files = {'sticker': sticker}
            
            if reply_markup: data['reply_markup'] = reply_markup
            return requests.post(url, data=data, files=files).json()
        except Exception as e:
            print(f"Send sticker error: {e}")
            return {}

    def send_dice(self,
                chat_id: int,
                emoji: str = "🎲",
                reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendDice"
        data = {
            "chat_id": chat_id,
            "emoji": emoji
        }
        if reply_markup: data["reply_markup"] = reply_markup
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Send dice error: {e}")
            return {}

    # ==============================
    # Polls and Quizzes
    # ==============================
    def send_poll(self,
                chat_id: int,
                question: str,
                options: List[str],
                is_anonymous: bool = True,
                type: str = "regular",
                allows_multiple_answers: bool = False,
                correct_option_id: Optional[int] = None,
                explanation: Optional[str] = None,
                open_period: Optional[int] = None,
                close_date: Optional[int] = None,
                is_closed: bool = False,
                reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendPoll"
        data = {
            "chat_id": chat_id,
            "question": question,
            "options": options,
            "is_anonymous": is_anonymous,
            "type": type
        }
        if allows_multiple_answers: data["allows_multiple_answers"] = True
        if correct_option_id is not None: data["correct_option_id"] = correct_option_id
        if explanation: data["explanation"] = explanation
        if open_period: data["open_period"] = open_period
        if close_date: data["close_date"] = close_date
        if is_closed: data["is_closed"] = True
        if reply_markup: data["reply_markup"] = reply_markup
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Send poll error: {e}")
            return {}

    def stop_poll(self,
                chat_id: int,
                message_id: int,
                reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/stopPoll"
        data = {
            "chat_id": chat_id,
            "message_id": message_id
        }
        if reply_markup: data["reply_markup"] = reply_markup
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Stop poll error: {e}")
            return {}

    # ==============================
    # Chat Management
    # ==============================
    def get_chat(self, chat_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/getChat"
        data = {"chat_id": chat_id}
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Get chat error: {e}")
            return {}

    def get_chat_administrators(self, chat_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/getChatAdministrators"
        data = {"chat_id": chat_id}
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Get chat administrators error: {e}")
            return {}

    def get_chat_members_count(self, chat_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/getChatMembersCount"
        data = {"chat_id": chat_id}
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Get chat members count error: {e}")
            return {}

    def get_chat_member(self, chat_id: int, user_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/getChatMember"
        data = {
            "chat_id": chat_id,
            "user_id": user_id
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Get chat member error: {e}")
            return {}

    def leave_chat(self, chat_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/leaveChat"
        data = {"chat_id": chat_id}
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Leave chat error: {e}")
            return {}

    def set_chat_title(self, chat_id: int, title: str) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/setChatTitle"
        data = {
            "chat_id": chat_id,
            "title": title
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Set chat title error: {e}")
            return {}

    def set_chat_description(self, chat_id: int, description: str) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/setChatDescription"
        data = {
            "chat_id": chat_id,
            "description": description
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Set chat description error: {e}")
            return {}

    def pin_chat_message(self,
                       chat_id: int,
                       message_id: int,
                       disable_notification: bool = False) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/pinChatMessage"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Pin chat message error: {e}")
            return {}

    def unpin_chat_message(self, chat_id: int, message_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/unpinChatMessage"
        data = {
            "chat_id": chat_id,
            "message_id": message_id
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Unpin chat message error: {e}")
            return {}

    def unpin_all_chat_messages(self, chat_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/unpinAllChatMessages"
        data = {"chat_id": chat_id}
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Unpin all chat messages error: {e}")
            return {}

    def export_chat_invite_link(self, chat_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/exportChatInviteLink"
        data = {"chat_id": chat_id}
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Export chat invite link error: {e}")
            return {}

    def set_chat_photo(self, chat_id: int, photo: Union[str, bytes]) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/setChatPhoto"
        data = {"chat_id": chat_id}
        files = None
        
        try:
            if isinstance(photo, str):
                with open(photo, 'rb') as f:
                    files = {'photo': f}
                    return requests.post(url, data=data, files=files).json()
            else:
                files = {'photo': photo}
                return requests.post(url, data=data, files=files).json()
        except Exception as e:
            print(f"Set chat photo error: {e}")
            return {}

    def delete_chat_photo(self, chat_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/deleteChatPhoto"
        data = {"chat_id": chat_id}
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Delete chat photo error: {e}")
            return {}

    def set_chat_sticker_set(self, chat_id: int, sticker_set_name: str) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/setChatStickerSet"
        data = {
            "chat_id": chat_id,
            "sticker_set_name": sticker_set_name
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Set chat sticker set error: {e}")
            return {}

    def delete_chat_sticker_set(self, chat_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/deleteChatStickerSet"
        data = {"chat_id": chat_id}
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Delete chat sticker set error: {e}")
            return {}

    # ==============================
    # Forum Topics
    # ==============================
    def create_forum_topic(self,
                         chat_id: int,
                         name: str,
                         icon_color: Optional[int] = None,
                         icon_custom_emoji_id: Optional[str] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/createForumTopic"
        data = {
            "chat_id": chat_id,
            "name": name
        }
        if icon_color: data["icon_color"] = icon_color
        if icon_custom_emoji_id: data["icon_custom_emoji_id"] = icon_custom_emoji_id
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Create forum topic error: {e}")
            return {}

    def edit_forum_topic(self,
                       chat_id: int,
                       message_thread_id: int,
                       name: Optional[str] = None,
                       icon_custom_emoji_id: Optional[str] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/editForumTopic"
        data = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id
        }
        if name: data["name"] = name
        if icon_custom_emoji_id: data["icon_custom_emoji_id"] = icon_custom_emoji_id
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Edit forum topic error: {e}")
            return {}

    def close_forum_topic(self,
                        chat_id: int,
                        message_thread_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/closeForumTopic"
        data = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Close forum topic error: {e}")
            return {}

    def reopen_forum_topic(self,
                         chat_id: int,
                         message_thread_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/reopenForumTopic"
        data = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Reopen forum topic error: {e}")
            return {}

    def delete_forum_topic(self,
                         chat_id: int,
                         message_thread_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/deleteForumTopic"
        data = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Delete forum topic error: {e}")
            return {}

    def unpin_all_forum_topic_messages(self,
                                     chat_id: int,
                                     message_thread_id: int) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/unpinAllForumTopicMessages"
        data = {
            "chat_id": chat_id,
            "message_thread_id": message_thread_id
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Unpin all forum topic messages error: {e}")
            return {}

    # ==============================
    # Webhook Methods
    # ==============================
    def set_webhook(self,
                   url: str,
                   max_connections: int = 40,
                   allowed_updates: Optional[List[str]] = None) -> dict:
        webhook_url = f"https://api.telegram.org/bot{self.token}/setWebhook"
        data = {
            "url": url,
            "max_connections": max_connections
        }
        if allowed_updates: data["allowed_updates"] = allowed_updates
        try:
            return requests.post(webhook_url, json=data).json()
        except Exception as e:
            print(f"Set webhook error: {e}")
            return {}

    def delete_webhook(self, drop_pending_updates: bool = False) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/deleteWebhook"
        data = {
            "drop_pending_updates": drop_pending_updates
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Delete webhook error: {e}")
            return {}

    def get_webhook_info(self) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/getWebhookInfo"
        try:
            return requests.get(url).json()
        except Exception as e:
            print(f"Get webhook info error: {e}")
            return {}

    # ==============================
    # Bot Management
    # ==============================
    def set_my_description(self,
                         description: str,
                         language_code: Optional[str] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/setMyDescription"
        data = {"description": description}
        if language_code: data["language_code"] = language_code
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Set my description error: {e}")
            return {}

    def set_my_name(self,
                   name: str,
                   language_code: Optional[str] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/setMyName"
        data = {"name": name}
        if language_code: data["language_code"] = language_code
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Set my name error: {e}")
            return {}

    def set_my_short_description(self,
                               short_description: str,
                               language_code: Optional[str] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/setMyShortDescription"
        data = {"short_description": short_description}
        if language_code: data["language_code"] = language_code
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Set my short description error: {e}")
            return {}

    # ==============================
    # Games
    # ==============================
    def send_game(self,
                chat_id: int,
                game_short_name: str,
                reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendGame"
        data = {
            "chat_id": chat_id,
            "game_short_name": game_short_name
        }
        if reply_markup: data["reply_markup"] = reply_markup
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Send game error: {e}")
            return {}

    def set_game_score(self,
                     user_id: int,
                     score: int,
                     force: bool = False,
                     disable_edit_message: bool = False,
                     chat_id: Optional[int] = None,
                     message_id: Optional[int] = None,
                     inline_message_id: Optional[str] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/setGameScore"
        data = {
            "user_id": user_id,
            "score": score,
            "force": force,
            "disable_edit_message": disable_edit_message
        }
        if chat_id: data["chat_id"] = chat_id
        if message_id: data["message_id"] = message_id
        if inline_message_id: data["inline_message_id"] = inline_message_id
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Set game score error: {e}")
            return {}

    def get_game_high_scores(self,
                           user_id: int,
                           chat_id: Optional[int] = None,
                           message_id: Optional[int] = None,
                           inline_message_id: Optional[str] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/getGameHighScores"
        data = {"user_id": user_id}
        if chat_id: data["chat_id"] = chat_id
        if message_id: data["message_id"] = message_id
        if inline_message_id: data["inline_message_id"] = inline_message_id
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Get game high scores error: {e}")
            return {}

    # ==============================
    # Payments
    # ==============================
    def send_invoice(self,
                   chat_id: int,
                   title: str,
                   description: str,
                   payload: str,
                   provider_token: str,
                   currency: str,
                   prices: List[Dict[str, Union[str, int]]],
                   start_parameter: Optional[str] = None,
                   photo_url: Optional[str] = None,
                   photo_size: Optional[int] = None,
                   photo_width: Optional[int] = None,
                   photo_height: Optional[int] = None,
                   need_name: bool = False,
                   need_phone_number: bool = False,
                   need_email: bool = False,
                   need_shipping_address: bool = False,
                   is_flexible: bool = False,
                   disable_notification: bool = False,
                   reply_markup: Optional[dict] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendInvoice"
        data = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": provider_token,
            "currency": currency,
            "prices": prices,
            "need_name": need_name,
            "need_phone_number": need_phone_number,
            "need_email": need_email,
            "need_shipping_address": need_shipping_address,
            "is_flexible": is_flexible,
            "disable_notification": disable_notification
        }
        if start_parameter: data["start_parameter"] = start_parameter
        if photo_url: data["photo_url"] = photo_url
        if photo_size: data["photo_size"] = photo_size
        if photo_width: data["photo_width"] = photo_width
        if photo_height: data["photo_height"] = photo_height
        if reply_markup: data["reply_markup"] = reply_markup
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Send invoice error: {e}")
            return {}

    def answer_shipping_query(self,
                            shipping_query_id: str,
                            ok: bool,
                            shipping_options: Optional[List[Dict[str, Any]]] = None,
                            error_message: Optional[str] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/answerShippingQuery"
        data = {
            "shipping_query_id": shipping_query_id,
            "ok": ok
        }
        if shipping_options: data["shipping_options"] = shipping_options
        if error_message: data["error_message"] = error_message
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Answer shipping query error: {e}")
            return {}

    def answer_pre_checkout_query(self,
                                pre_checkout_query_id: str,
                                ok: bool,
                                error_message: Optional[str] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/answerPreCheckoutQuery"
        data = {
            "pre_checkout_query_id": pre_checkout_query_id,
            "ok": ok
        }
        if error_message: data["error_message"] = error_message
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Answer pre checkout query error: {e}")
            return {}

    # ==============================
    # Inline Mode
    # ==============================
    def answer_inline_query(self,
                          inline_query_id: str,
                          results: List[Dict[str, Any]],
                          cache_time: int = 300,
                          is_personal: bool = False,
                          next_offset: Optional[str] = None,
                          switch_pm_text: Optional[str] = None,
                          switch_pm_parameter: Optional[str] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/answerInlineQuery"
        data = {
            "inline_query_id": inline_query_id,
            "results": results,
            "cache_time": cache_time,
            "is_personal": is_personal
        }
        if next_offset: data["next_offset"] = next_offset
        if switch_pm_text: data["switch_pm_text"] = switch_pm_text
        if switch_pm_parameter: data["switch_pm_parameter"] = switch_pm_parameter
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Answer inline query error: {e}")
            return {}

    # ==============================
    # Web Apps
    # ==============================
    def answer_web_app_query(self,
                           web_app_query_id: str,
                           result: Dict[str, Any]) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/answerWebAppQuery"
        data = {
            "web_app_query_id": web_app_query_id,
            "result": result
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Answer web app query error: {e}")
            return {}

    # ==============================
    # User Management
    # ==============================
    def promote_chat_member(self,
                          chat_id: int,
                          user_id: int,
                          is_anonymous: bool = False,
                          can_manage_chat: bool = False,
                          can_post_messages: bool = False,
                          can_edit_messages: bool = False,
                          can_delete_messages: bool = False,
                          can_manage_video_chats: bool = False,
                          can_restrict_members: bool = False,
                          can_promote_members: bool = False,
                          can_change_info: bool = False,
                          can_invite_users: bool = False,
                          can_pin_messages: bool = False) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/promoteChatMember"
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "is_anonymous": is_anonymous,
            "can_manage_chat": can_manage_chat,
            "can_post_messages": can_post_messages,
            "can_edit_messages": can_edit_messages,
            "can_delete_messages": can_delete_messages,
            "can_manage_video_chats": can_manage_video_chats,
            "can_restrict_members": can_restrict_members,
            "can_promote_members": can_promote_members,
            "can_change_info": can_change_info,
            "can_invite_users": can_invite_users,
            "can_pin_messages": can_pin_messages
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Promote chat member error: {e}")
            return {}

    def restrict_chat_member(self,
                           chat_id: int,
                           user_id: int,
                           permissions: Dict[str, bool],
                           until_date: Optional[int] = None) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/restrictChatMember"
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "permissions": permissions
        }
        if until_date: data["until_date"] = until_date
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Restrict chat member error: {e}")
            return {}

    def ban_chat_member(self,
                       chat_id: int,
                       user_id: int,
                       until_date: Optional[int] = None,
                       revoke_messages: bool = False) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/banChatMember"
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "revoke_messages": revoke_messages
        }
        if until_date: data["until_date"] = until_date
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Ban chat member error: {e}")
            return {}

    def unban_chat_member(self,
                         chat_id: int,
                         user_id: int,
                         only_if_banned: bool = False) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/unbanChatMember"
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "only_if_banned": only_if_banned
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Unban chat member error: {e}")
            return {}

    # ==============================
    # Keyboard Methods
    # ==============================
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

    # ==============================
    # Utility Methods
    # ==============================
    def send_chat_action(self,
                       chat_id: int,
                       action: str) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendChatAction"
        data = {
            "chat_id": chat_id,
            "action": action
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Send chat action error: {e}")
            return {}

    def get_file(self, file_id: str) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/getFile"
        data = {"file_id": file_id}
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Get file error: {e}")
            return {}

    def download_file(self, file_path: str, destination: str) -> bool:
        url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        try:
            response = requests.get(url, stream=True)
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Download file error: {e}")
            return False

    # ==============================
    # Gifts and Premium
    # ==============================
    def send_gift(self,
                chat_id: int,
                user_id: int,
                gift_option: str) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendGift"
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "gift_option": gift_option
        }
        try:
            return requests.post(url, json=data).json()
        except Exception as e:
            print(f"Send gift error: {e}")
            return {}

    # ==============================
    # User Agent and Load Protection
    # ==============================
    def set_user_agent(self, user_agent: str):
        """Set custom User-Agent for requests"""
        self.user_agent = user_agent

    def enable_load_protection(self, max_requests_per_second: int = 30):
        """Enable rate limiting"""
        self.max_requests_per_second = max_requests_per_second
        self.last_request_time = 0

    def _check_rate_limit(self):
        """Internal method for rate limiting"""
        if hasattr(self, 'max_requests_per_second'):
            current_time = time.time()
            time_diff = current_time - self.last_request_time
            if time_diff < 1 / self.max_requests_per_second:
                time.sleep(1 / self.max_requests_per_second - time_diff)
            self.last_request_time = current_time