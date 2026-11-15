#!/bin/bash

# Определяем абсолютный путь к директории, где лежит этот скрипт
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)

# Переходим в эту директорию
cd "$PROJECT_DIR"

# Запускаем приложение через uv только на localhost
uv run streamlit run app.py --server.address=localhost --browser.gatherUsageStats false
