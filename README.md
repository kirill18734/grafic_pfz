
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

3. Настройка Google Диска (опционально (если нужна необходимость смотреть по url через Google Диск )):
   - Скачайте [Google Диск](https://ipv4.google.com/intl/ru_ALL/drive/download/).
   - После успешной установки, у вас должен создаться диск "Google Диск"
   - Нужно переместить файл `График работы.xlsx` в этот диск в нужную вам директорию 
   - Укажите путь  в проекте по пути `config/auto_search_dir.py` (переменная `path_to_test1_json`) путь до вашего файла `График работы.xlsx`.
   - Укажите URL файла `График работы.xlsx` в `config/config.json` в переменной "URL".

4. Создайте Telegram-бота через [BotFather](https://web.telegram.org/k/#@BotFather):
   - Вставьте токен в `config/config.json` (`bot_token`).
   - Укажите `chat_id` (его можно узнать если перейти в нового бота и посмотреть ссылку, он будет в конце в виде цифр .
   
5. Необходимо найти файл `График работы.xlsx` и подготовить его: 
   - переименовать лист на название текущего месяца, переименовать имя сотрудинка на нужное вам  , проставить актульные дни недели для текущего месяца и количество дней,  сохранить. Остальное можно отредактировать через бота  
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

