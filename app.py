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

# Настройки страницы
st.set_page_config(page_title="Ollama Chat", page_icon="💬")
st.title("💬 Ollama Chat Interface")

# Получаем модель из переменных окружения или используем дефолтную
def get_default_model():
    return os.getenv("OLLAMA_MODEL", "llama3")

# Инициализация истории чата
if "messages" not in st.session_state:
    st.session_state.messages = []

# Боковая панель для настроек
with st.sidebar:
    st.header("Настройки")
    model_name = st.text_input("Модель", value=get_default_model())
    if st.button("Очистить историю"):
        st.session_state.messages = []
        st.rerun()

# Отображение истории сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода сообщения
if prompt := st.chat_input("Введите ваше сообщение..."):
    # Добавляем сообщение пользователя в историю
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ответ от Ollama
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            # Используем стриминг для эффекта "печати" текста
            stream = ollama.chat(
                model=model_name,
                messages=st.session_state.messages,
                stream=True,
            )

            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

            # Сохраняем ответ ассистента
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Ошибка подключения к Ollama: {e}")
            st.info(f"Убедитесь, что Ollama запущена и модель доступна (команда: ollama run {model_name})")
