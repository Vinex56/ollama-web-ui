import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional

HISTORY_DIR = "history"

def init_history():
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

def save_chat(messages: List[Dict[str, str]], title: str = None) -> str:
    chat_id = str(uuid.uuid4())
    # Если названия нет, берем первое сообщение пользователя
    if not title:
        for m in messages:
            if m['role'] == 'user' and m['content']:
                title = m['content'][:30] + "..." if len(m['content']) > 30 else m['content']
                break

    if not title:
        title = "Новый чат"

    data = {
        "id": chat_id,
        "title": title,
        "timestamp": datetime.now().isoformat(),
        "messages": messages
    }

    file_path = os.path.join(HISTORY_DIR, f"{chat_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return chat_id

def list_chats() -> List[Dict]:
    chats = []
    for filename in os.listdir(HISTORY_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(HISTORY_DIR, filename), 'r', encoding='utf-8') as f:
                chats.append(json.load(f))
    # Сортируем по дате (новые сверху)
    return sorted(chats, key=lambda x: x['timestamp'], reverse=True)

def load_chat(chat_id: str) -> Optional[Dict]:
    file_path = os.path.join(HISTORY_DIR, f"{chat_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def update_chat(chat_id: str, messages: List[Dict[str, str]]):
    data = load_chat(chat_id)
    if data:
        data['messages'] = messages
        data['timestamp'] = datetime.now().isoformat()
        file_path = os.path.join(HISTORY_DIR, f"{chat_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def delete_chat(chat_id: str):
    file_path = os.path.join(HISTORY_DIR, f"{chat_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)

def clear_all_chats():
    for filename in os.listdir(HISTORY_DIR):
        if filename.endswith('.json'):
            os.remove(os.path.join(HISTORY_DIR, filename))

