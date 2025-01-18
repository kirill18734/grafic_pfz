
# График работы

## Описание
Проект позволяет управлять графиком работы в формате `*.xlsx` через Telegram. Можно использовать Google Диск для удаленного доступа или работать локально.

## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/kirill18734/grafic_pfz.git
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Настройка Google Диска (опционально):
   - Скачайте [Google Диск](https://ipv4.google.com/intl/ru_ALL/drive/download/).
   - Укажите путь к JSON-файлу сервиса в `config/auto_search_dir.py` (переменная `path_to_test1_json`).
   - Укажите URL файла в `config/config.json`.

4. Создайте Telegram-бота через [BotFather](https://web.telegram.org/k/#@BotFather):
   - Вставьте токен в `config/config.json` (`bot_token`).
   - Укажите `chat_id`.

## Структура проекта
- `main.py` — основной скрипт.
- `config/` — конфигурации.
- `edit_charts/` — обработка графиков.

## Использование
Запустите проект:
```bash
python main.py
```
Взаимодействуйте с ботом для управления графиком.

