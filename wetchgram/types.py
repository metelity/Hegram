class InlineKeyboardButton:
    def __init__(self, text: str, callback_data: str = None, url: str = None):
        self.text = text
        self.callback_data = callback_data
        self.url = url
    
    def to_dict(self) -> dict:
        data = {"text": self.text}
        if self.callback_data:
            data["callback_data"] = self.callback_data
        if self.url:
            data["url"] = self.url
        return data

class ReplyKeyboardButton:
    def __init__(self, text: str):
        self.text = text
    
    def to_dict(self) -> dict:
        return {"text": self.text}

class InlineKeyboardMarkup:
    def __init__(self, keyboard: list = None):
        self.inline_keyboard = keyboard or []
    
    def add_row(self, *buttons):
        self.inline_keyboard.append([btn.to_dict() for btn in buttons])
    
    def to_dict(self) -> dict:
        return {"inline_keyboard": self.inline_keyboard}

class ReplyKeyboardMarkup:
    def __init__(self, resize_keyboard: bool = True):
        self.keyboard = []
        self.resize_keyboard = resize_keyboard
    
    def add_row(self, *buttons):
        row = []
        for btn in buttons:
            if isinstance(btn, ReplyKeyboardButton):
                row.append(btn.to_dict())
            else:
                row.append({"text": str(btn)})
        self.keyboard.append(row)
    
    def to_dict(self) -> dict:
        return {
            "keyboard": self.keyboard,
            "resize_keyboard": self.resize_keyboard
        }