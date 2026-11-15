import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Принудительно очищаем переменные прокси, чтобы httpx не падал на socks://
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('ALL_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

import streamlit as st
import ollama
from src.history_manager import init_history, save_chat, list_chats, load_chat, update_chat, delete_chat, clear_all_chats

# Инициализируем папку истории
init_history()

# Настройки страницы
st.set_page_config(page_title='Ollama Chat', page_icon='💬')
st.title('💬 Ollama Chat Interface')

# Получаем модель из переменных окружения или используем дефолтную
def get_default_model():
    return os.getenv('OLLAMA_MODEL', 'llama3')

# Инициализация состояния
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

# Боковая панель
with st.sidebar:
    st.header('Настройки')
    model_name = st.text_input('Модель', value=get_default_model())

    st.divider()
    st.header('История чатов')

    if st.button('➕ Новый чат'):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()

    # Список чатов
    chats = list_chats()
    for chat in chats:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(f"{chat['title']}", key=f"btn_{chat['id']}"):
                st.session_state.messages = chat['messages']
                st.session_state.current_chat_id = chat['id']
                st.rerun()
        with col2:
            if st.button('🗑', key=f"del_{chat['id']}"):
                delete_chat(chat['id'])
                st.rerun()

    st.divider()
    if st.button('Новая сессия', type='primary'):
        if st.session_state.current_chat_id:
            st.session_state.messages = []
            st.session_state.current_chat_id = None
            st.rerun()

    if st.button('🔥 Очистить ВСЁ', type='primary'):
        clear_all_chats()
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()

# Отображение истории сообщений
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Поле ввода сообщения
if prompt := st.chat_input('Введите ваше сообщение...'):
    # Добавляем сообщение пользователя в историю
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    # Если это первый запрос в новом чате, создаем запись
    if st.session_state.current_chat_id is None:
        st.session_state.current_chat_id = save_chat(st.session_state.messages)

    # Ответ от Ollama
    with st.chat_message('assistant'):
        response_placeholder = st.empty()
        full_response = ''

        try:
            # Используем стриминг для эффекта 'печати' текста
            stream = ollama.chat(
                model=model_name,
                messages=st.session_state.messages,
                stream=True,
            )

            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                response_placeholder.markdown(full_response + '▌')

            response_placeholder.markdown(full_response)

            # Сохраняем ответ ассистента
            st.session_state.messages.append({'role': 'assistant', 'content': full_response})

            # Обновляем историю в файле
            if st.session_state.current_chat_id:
                update_chat(st.session_state.current_chat_id, st.session_state.messages)

        except Exception as e:
            st.error(f'Ошибка подключения к Ollama: {e}')
            st.info(f'Убедитесь, что Ollama запущена и модель доступна (команда: ollama run {model_name})')

