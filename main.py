import datetime
import json
import os

from telebot import types
from telebot.types import BotCommand, InlineKeyboardMarkup, \
    InlineKeyboardButton
import telebot
from config.auto_search_dir import data_config, path_to_img
import urllib3
from edit_charts.create_new_chart import CreateChart
from edit_charts.delete_user import DeleteUsers
from edit_charts.data_file import DataCharts
from edit_charts.adduser import AddUser
from edit_charts.edit_smens import Editsmens
from edit_charts.get_img_xl import open_site
import threading
import time
import schedule

# Создаем экземпляр бота
bot = telebot.TeleBot(data_config['my_telegram_bot']['bot_token'],
                      parse_mode='HTML')
user_ids = set()
USER_IDS_FILE = 'user_ids.json'


def load_user_ids():
    if os.path.exists(USER_IDS_FILE):
        with open(USER_IDS_FILE, 'r') as file:
            return set(json.load(file))
    return set()


def save_user_ids(userids):
    with open(USER_IDS_FILE, 'w') as file:
        json.dump(list(userids), file)


def create_new_chart():
    new = CreateChart()
    new.new_chart()
    table_data = DataCharts()
    if table_data.list_months[table_data.data_months()[3]] in str(table_data.file.worksheets[-1].title):
        result = True
    else:
        result = False

    for user_id in load_user_ids():
        if result:
            bot.send_message(user_id,
                             f'Создан график на новый месяц ({str(table_data.file.worksheets[-1].title)}), необходимо заполнить. \n\nЧтобы увидеть новый месяц необходимо нажать на /start')
        else:
            bot.send_message(user_id,
                             'Была попытка создать новый график, что то пошло не так, необходимо проверить')


# Отключаем предупреждения
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def job():
    if datetime.datetime.now().day == 20:
        create_new_chart()


schedule.every().day.at("12:00").do(job)


class Main:
    # дополнительный аргумент, для создания нового листа
    def __init__(self):
        self.selected_number = None
        self.status_dict = {}
        self.select_invent = None
        self.smens = None
        self.image_message_id = None
        self.message_ids = []
        self.select_user = None
        self.select_new_invent = None
        self.select_n = None
        self.month = None
        self.select_smens = None
        self.key = None
        self.state_stack = {}  # Стек для хранения состояний
        self.selected_employees = getattr(self, 'selected_employees', set())
        self.user_id = None
        self.data_smens = None
        self.selected_month = None
        self.call = None
        self.markup = None
        self.actualy_months = None
        # если передался параметр на создание графика, то выполняем фукнцию, которая создаться график на новый месяц
        self.input_enabled = False  # Флаг для контроля ввода
        self.delete_user = None
        self.table_data = None
        self.last_list = None
        self.start_main()

    # начальные кнопки, если нет, нового месяца, но используем текущий, или если он есть, то выводим 2 кнопки
    def get_months(self):
        self.table_data = DataCharts()
        self.last_list = self.table_data.file.worksheets[-1]
        # если крайний лист, будет совпадать с текущим месяцем, то значит будет одна кнопка для текущего месяца,
        # если нет, то 2 для нового графика и для старого
        if self.table_data.list_months[self.table_data.data_months()[2]] in str(self.last_list.title):
            self.actualy_months = [
                self.table_data.list_months[self.table_data.data_months()[2]]]
            return [
                f'Текущий месяц ({self.table_data.list_months[self.table_data.data_months()[2]]})']
        else:
            self.actualy_months = [
                self.table_data.list_months[self.table_data.data_months()[2]],
                self.table_data.list_months[self.table_data.data_months()[3]]]
            return [
                f'Текущий месяц ({self.table_data.list_months[self.table_data.data_months()[2]]})',
                f'Следующий месяц ({self.table_data.list_months[self.table_data.data_months()[3]]})']

    def start_main(self):
        commands = [
            BotCommand("start", "В начало"),
            BotCommand("back", "Назад")
        ]
        bot.set_my_commands(commands)

        @bot.message_handler(commands=['start'])
        def handle_start_main(message):
            self.user_id = message.chat.id
            user_ids.add(self.user_id)
            save_user_ids(user_ids)
            # Удаляем сообщения в диапазоне
            for id_ in range(message.message_id - 20, message.message_id + 1):
                try:
                    bot.delete_message(chat_id=message.chat.id,
                                       message_id=id_)
                except:
                    continue
            # После завершения цикла и удаления сообщений вызываем метод выбора месяца
            self.show_month_selection()

        @bot.message_handler(commands=['back'])
        def handle_back(message):
            bot.delete_message(chat_id=message.chat.id,
                               message_id=message.message_id)

            last_key, last_function = self.state_stack.popitem()
            if message == 'get_image':
                handle_start_main(message)
            if 'Текущий месяц' in str(last_key) or 'Следующий месяц' in str(
                    last_key):
                for id_ in range(message.message_id - 20,
                                 message.message_id + 1):
                    try:
                        bot.delete_message(chat_id=message.chat.id,
                                           message_id=id_)
                    except:
                        continue
                last_function()
            else:
                # for id_ in range(message.message_id - 20,
                #                  message.message_id + 1):
                #     try:
                #         bot.delete_message(chat_id=message.chat.id,
                #                            message_id=id_)
                #     except:
                #         continue
                last_function()

        @bot.callback_query_handler(
            func=lambda call: call.data == 'start_command')
        def handle_start_command(call):
            # Вызываем команду /start
            handle_start_main(call.message)

        @bot.callback_query_handler(func=lambda call: True)
        def handle_query(call):
            self.call = call
            if 'Текущий месяц' in self.call.data or 'Следующий месяц' in self.call.data:
                self.state_stack[self.call.data] = self.show_month_selection

            if not self.state_stack or (
                    'Текущий месяц' not in str(list(self.state_stack.keys())[0]) and
                    'Следующий месяц' not in str(list(self.state_stack.keys())[0])):
                # Если кнопок нет, сбрасываем состояние и начинаем заново
                handle_start_main(call.message)
            else:
                if 'Текущий месяц' in self.call.data or 'Следующий месяц' in self.call.data:
                    self.state_stack[
                        self.call.data] = self.show_month_selection
                    # Сохраняем выбранный месяц
                    self.selected_month = self.call.data
                    self.month = str(self.selected_month).replace(
                        'Текущий месяц (',
                        '').replace(')',
                                    '').replace(
                        'Следующий месяц (', '').replace(')', '')
                    # После выбора месяца показываем кнопки "Смены / подработки" и "Сотрудники"
                    self.show_sments_dop_sments()
                elif self.call.data in ['image']:
                    response_text = f"""Заявка на создание картинки 'График работы' создана. Пожалуйста ожидайте. В течении 30сек картинка отправиться."""
                    bot.answer_callback_query(self.call.id, response_text,
                                              show_alert=True)
                    open_site(self.month)
                    # Отправляем изображение
                    with open(path_to_img,
                              'rb') as photo:
                        bot.send_photo(self.call.message.chat.id, photo)
                elif self.call.data in ['shifts_jobs', 'employees',
                                        'get_image']:
                    self.state_stack[
                        self.call.data] = self.show_sments_dop_sments

                    if self.call.data == 'shifts_jobs':
                        # Создаем новую клавиатуру
                        self.show_shifts_jobs_selection()

                    elif self.call.data == 'employees':
                        self.add_del_employees()
                    elif self.call.data == 'get_image':
                        self.data_image()

                elif self.call.data in ['smens', 'dopsmens']:
                    self.state_stack[
                        self.call.data] = self.show_shifts_jobs_selection
                    self.smens = self.call.data
                    self.smens_users()
                elif self.call.data in ['add_employees']:
                    self.state_stack[self.call.data] = self.add_del_employees
                    self.add_employees()

                elif self.call.data in ['dell_employee']:
                    self.state_stack[self.call.data] = self.add_del_employees
                    self.dell_employee()

                elif self.call.data.startswith('select_employee_'):
                    employee_name = self.call.data.split('_', 2)[2]
                    if employee_name in self.selected_employees:
                        self.selected_employees.remove(employee_name)
                    else:
                        self.selected_employees.add(employee_name)
                    self.dell_employee()

                elif self.call.data in ['cancel_delete']:
                    self.add_del_employees()
                #     self.state_stack[self.call.data] = self.dell_employee

                elif self.call.data.startswith('user_'):
                    self.table = Editsmens()
                    self.select_user = str(self.call.data).replace(
                        'user_', '')
                    self.status_dict = self.table.smens(self.month,
                                                        self.select_user)
                    self.actualy_smens()
                # если выбран сотрудник на удаление, то вызываем функию для
                # удаления
                elif self.call.data == 'confirm_delete':
                    if self.selected_employees:

                        delete_user = DeleteUsers()
                        delete_user.delete(list(self.selected_employees),
                                           self.actualy_months)

                        response_text = "Сотрудник(и) удален(ы)"
                        bot.answer_callback_query(call.id, response_text,
                                                  show_alert=True)
                        self.add_del_employees()
                    else:
                        response_text = "Чтобы изменить подработку, перейдите пожалуйста в раздел 'Подработки'."
                        bot.answer_callback_query(call.id, response_text,
                                                  show_alert=True)

                    # Обработка статусов
                elif (self.smens + '_') in self.call.data:
                    key, day, smens, current_value = self.call.data.split('_')
                    self.key = key
                    if self.smens == 'smens':
                        if current_value == 'None' and 'i' not in str(
                                key) and 'сб' not in str(day) and 'вс' not in str(day):
                            self.status_dict[int(self.key)] = 1
                            self.actualy_smens()
                        elif current_value == '1' and 'i' not in str(key) and 'сб' not in str(day) and 'вс' not in str(
                                day):
                            self.status_dict[int(self.key)] = None
                            self.actualy_smens()
                        elif ('сб' in str(day) or 'вс' in str(day) or 'i' in str(key)) and current_value == '1':
                            self.select_invent = key
                            self.select_n = 1

                            self.invent()
                        elif ('сб' in str(day) or 'вс' in str(day) or 'i' in str(key)) and current_value == 'None':
                            self.status_dict[int(self.key)] = 1
                            self.select_invent = key
                            self.select_n = 1
                            self.invent()
                        else:
                            response_text = """Чтобы изменить подработку, перейдите пожалуйста в раздел "Подработки"."""
                            bot.answer_callback_query(call.id, response_text,
                                                      show_alert=True)

                    elif self.smens == 'dopsmens':

                        if current_value == '1':
                            response_text = "Чтобы изменить смену, перейдите пожалуйста в раздел 'Смены'."
                            bot.answer_callback_query(call.id, response_text,
                                                      show_alert=True)
                        else:
                            self.key = self.key if 'i' in self.key else int(
                                self.key)
                            self.selected_number = self.status_dict[self.key]
                            self.dop_smens()
                elif call.data == "invent_selected":
                    self.select_new_invent = f'{self.select_invent}i'
                    self.select_invent = self.select_new_invent
                    self.invent()
                elif call.data == "invent_not_selected":
                    if type(self.select_invent) == str:
                        self.select_new_invent = int(
                            str(self.select_invent).replace('i',
                                                            ''))  # Убираем элемент из выбранных
                    else:
                        self.select_new_invent = f'{self.select_invent}i'
                    self.select_invent = self.select_new_invent
                    self.invent()
                    # Обновляем кнопки
                elif self.call.data.startswith("number_"):
                    selected_number = int(call.data.split("_")[1])
                    # Проверяем, выбран ли номер
                    if self.selected_number == selected_number:
                        self.selected_number = None  # Снимаем выбор, если номер уже выбран
                    else:
                        self.selected_number = selected_number  # Сохраняем новый выбранный номер

                    self.dop_smens()  # Обновляем кнопки
                elif call.data == 'save_invent':
                    if 'i' not in str(self.key):
                        self.key = int(self.key)

                    # print(int(self.key))
                    self.status_dict = {
                        key if key != self.key else self.select_new_invent: value
                        for key, value in
                        self.status_dict.items()}
                    self.status_dict[self.select_new_invent] = self.select_n

                    self.actualy_smens()
                elif call.data == 'cancel_invent':
                    if 'i' not in str(self.key):
                        self.key = int(self.key)

                    # print(int(self.key))
                    self.status_dict = {
                        key if key != self.key else int(
                            str(self.key).replace('i', '')): value
                        for key, value in
                        self.status_dict.items()}
                    self.status_dict[
                        int(str(self.key).replace('i', ''))] = None
                    self.actualy_smens()
                elif call.data == 'cancel':
                    # Логика для отмены
                    self.actualy_smens()
                elif call.data == 'save_smens':
                    self.status_dict[self.key] = self.selected_number
                    response_text = "Подработка сохранена"
                    bot.answer_callback_query(call.id, response_text,
                                              show_alert=True
                                              )

                    self.actualy_smens()
                elif self.call.data in ['save_all_smens']:
                    self.table.edit_smens(self.month, self.select_user,
                                          self.status_dict)

                    response_text = "Изменения сохранены."
                    bot.answer_callback_query(call.id, response_text,
                                              show_alert=True)
                    self.smens_users()
                elif self.call.data in ['cancel_all_smens']:
                    self.smens_users()

    def show_month_selection(self):
        self.markup = InlineKeyboardMarkup()
        buttons = []

        for month in self.get_months():
            item = InlineKeyboardButton(month, callback_data=month)
            buttons.append(item)

        self.markup = InlineKeyboardMarkup([buttons])

        try:
            bot.edit_message_text(
                f"Выберите месяц:",
                chat_id=self.call.message.chat.id,
                message_id=self.call.message_id,
                reply_markup=self.markup
            )

        except:
            bot.send_message(self.user_id, "Выберите месяц:",
                             reply_markup=self.markup)

    def show_sments_dop_sments(self):
        self.markup = InlineKeyboardMarkup()
        item1 = InlineKeyboardButton("Смены / подработки",
                                     callback_data='shifts_jobs')
        item2 = InlineKeyboardButton("Сотрудники", callback_data='employees')
        item3 = InlineKeyboardButton("Посмотреть график",
                                     callback_data='get_image')  # url=data_config["URL"]

        self.markup.add(item1, item2)
        self.markup.add(item3)
        # Обновляем клавиатуру в том же сообщении
        bot.edit_message_text(
            f"""Вы находитесь в разделе: "<u>{self.selected_month}</u>".\n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start\n\nВыберете раздел:""",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=self.markup)

    def show_shifts_jobs_selection(self):

        self.markup = InlineKeyboardMarkup()

        item1 = InlineKeyboardButton("Смены", callback_data='smens')

        item2 = InlineKeyboardButton("Подработки", callback_data='dopsmens')

        self.markup.add(item1, item2)

        bot.edit_message_text(

            f"""Вы находитесь в разделе: "{self.selected_month}" - "<u>Смены / подработки</u>".\n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберите раздел:""",

            chat_id=self.call.message.chat.id,

            message_id=self.call.message.message_id,

            reply_markup=self.markup

        )

    def add_del_employees(self):
        self.markup = InlineKeyboardMarkup()
        item4 = InlineKeyboardButton("Добавить сотрудника",
                                     callback_data='add_employees')
        item5 = InlineKeyboardButton("Удалить сотрудника",
                                     callback_data='dell_employee')
        self.markup.add(item4, item5)
        try:
            bot.edit_message_text(
                f"""Вы находитесь в разделе: "{self.selected_month}" - "<u>Сотрудники</u>".\n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберите раздел:""",
                chat_id=self.call.message.chat.id,
                message_id=self.call.message.message_id,
                reply_markup=self.markup)
        except:

            bot.send_message(self.user_id,
                             f"""Вы находитесь в разделе: "{self.selected_month}" - "<u>Сотрудники</u>".\n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберите раздел:""",
                             reply_markup=self.markup)

    def data_image(self):
        self.markup = InlineKeyboardMarkup()
        item4 = InlineKeyboardButton("Перейти на сайт",
                                     callback_data='site_image', url=data_config["URL"], disable_web_page_preview=True)
        item5 = InlineKeyboardButton("Показать картинку ",
                                     callback_data='image',
                                     )
        self.markup.add(item4, item5)
        try:
            bot.edit_message_text(
                f"""Вы находитесь в разделе: "{self.selected_month}" - "<u>Посмотреть график</u>".\n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберите раздел:""",
                chat_id=self.call.message.chat.id,
                message_id=self.call.message.message_id,
                reply_markup=self.markup)
        except:

            bot.send_message(self.user_id,
                             f"""В""ы находитесь в разделе: "{self.selected_month}" - "<u>Посмотреть график</u>".\n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберите раздел:""",
                             reply_markup=self.markup)

    def add_employees(self):
        # Редактируем текущее сообщение, чтобы запросить имя сотрудника
        bot.edit_message_text(
            f"""Вы находитесь в разделе: {self.selected_month}.\n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start \n\nНапишите имя сотрудника для добавления""",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id
        )

        # Устанавливаем состояние ожидания ответа от пользователя
        bot.register_next_step_handler(self.call.message,
                                       self.process_employee_name)

    def process_employee_name(self, message):
        users = DataCharts()
        if message.text not in ['/back',
                                '/start'] and message.text not in users.get_users(self.month):
            employee_name = message.text  # Получаем введенное имя сотрудника

            add_users = AddUser()
            add_users.add(str(employee_name), self.actualy_months)
            bot.delete_message(chat_id=message.chat.id,
                               message_id=message.message_id)
            # Здесь вы можете обработать имя сотрудника, например, сохранить его в базе данных
            response_text = f"Сотрудник {employee_name} добавлен."
            bot.answer_callback_query(self.call.id, response_text,
                                      show_alert=True)

            self.add_del_employees()
        # elif message.text in ['/back']:
        #     bot.delete_message(chat_id=message.chat.id,
        #                        message_id=message.message_id)
        #     # self.add_del_employees()
        else:
            for id_ in range(message.message_id - 1, message.message_id + 1):
                try:
                    bot.delete_message(chat_id=message.chat.id,
                                       message_id=message.message_id)
                except:
                    continue
            # bot.delete_message(chat_id=message.chat.id,
            #                    message_id=message.message_id)
            if message.text in users.get_users(self.month):
                self.state_stack.popitem()
                response_text = f"Данное имя уже есть в таблице, пожалуйста, напишите другое"
                bot.answer_callback_query(self.call.id, response_text,
                                          show_alert=True)

            if message.text == '/back':
                self.state_stack.popitem()
                self.add_del_employees()

    def dell_employee(self):
        self.table_data = DataCharts()
        employees = self.table_data.get_users(
            self.month)  # Получаем список сотрудников за последний месяц

        new_markup = InlineKeyboardMarkup()

        # Добавляем кнопки для сотрудников по 2 в строке
        for i in range(0, len(employees), 2):
            # Берем два сотрудника за раз
            row_buttons = []
            for j in range(2):
                if i + j < len(
                        employees):  # Проверяем, чтобы не выйти за пределы списка
                    employee = employees[i + j]
                    is_selected = employee in self.selected_employees
                    button_text = f"{employee} {'❌' if is_selected else '✅'}"
                    item = InlineKeyboardButton(button_text,
                                                callback_data=f'select_employee_{employee}')
                    row_buttons.append(item)

            # Добавляем кнопки в строку
            new_markup.row(*row_buttons)

        # Добавляем кнопку "Удалить"
        delete_button = InlineKeyboardButton("🗑️ Удалить!",
                                             callback_data='confirm_delete')
        cancel_delete = InlineKeyboardButton("Отмена!",
                                             callback_data='cancel_delete')
        new_markup.add(cancel_delete, delete_button)

        bot.edit_message_text(
            f"""Вы находитесь в разделе: "{self.selected_month}" - "Сотрудники" - "<u>Удалить сотрудника</u>". \n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберите сотрудников для удаления:""",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=new_markup
        )

    def smens_users(self):
        self.markup = types.InlineKeyboardMarkup()
        buttons = []
        # Получаем список пользователей
        users = self.table_data.get_users(self.month)

        for user in users:
            # Используем имя пользователя в качестве callback_data
            item = types.InlineKeyboardButton(user,
                                              callback_data=f'user_{user}')
            buttons.append(item)

        self.markup.add(*buttons)
        smen = 'Смены' if self.smens == 'smens' else 'Подработки'
        bot.edit_message_text(
            f"""Вы находитесь в разделе: "{self.selected_month}" - "Смены / подработки" - "<u>{smen}</u>". \n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберите сотрудника:""",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=self.markup
        )

    def actualy_smens(self):
        self.markup = types.InlineKeyboardMarkup()
        table = Editsmens()
        get_days = table.get_days(self.month)
        buttons = []

        for key, value in self.status_dict.items():

            if value is None:
                emoji = "❌"  # Красный крестик
            elif value == 1 and type(key) == int:
                emoji = "✅"  # Зеленая галочка
            elif value == 1 and type(key) == str:
                emoji = "🟦"  # Зеленая галочка
            else:
                emoji = "🟠"  # Знак будильника

            button_text = f"{str(key).replace('i', '')}д ({get_days[int(str(key).replace('i', ''))]}) {emoji}"
            item = types.InlineKeyboardButton(button_text,
                                              callback_data=f"{key}_{get_days[int(str(key).replace('i', ''))]}_"
                                                            f"{self.smens}_{value}")
            buttons.append(item)

        self.markup.add(*buttons)
        # Добавляем кнопку "Сохранить"
        save_smens = InlineKeyboardButton("💾 Сохранить!",
                                          callback_data='save_all_smens')
        cancel_smens = InlineKeyboardButton("Отмена!",
                                            callback_data='cancel_all_smens')
        self.markup.add(cancel_smens, save_smens)
        smen = 'Смены' if self.smens == 'smens' else 'Подработки'
        bot.edit_message_text(
            f"""Вы находитесь в разделе:  "{self.selected_month}" - "Смены / подработки" - "{smen}"  - "<u>{self.select_user}</u>". \n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберете раздел:\n❌ - выходной\n✅ - смена\n🟠 - подработка\n🟦 - смена (инвентаризация)""",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=self.markup
        )

    def invent(self):
        self.markup = types.InlineKeyboardMarkup()

        # Проверяем, выбран ли номер, и устанавливаем соответствующий текст кнопки
        if 'i' in str(self.select_invent):
            button_text = "✅"  # Зеленая галочка для выбранного номера
            callback_data = "invent_not_selected"  # Изменяем состояние
        else:
            button_text = "❌"  # Красный крестик для невыбранного номера
            callback_data = "invent_selected"  # Изменяем состояние

        item = types.InlineKeyboardButton(button_text,
                                          callback_data=callback_data)
        self.markup.add(item)

        # Добавляем кнопки "Отмена" и "Сохранить"
        cancel_button = types.InlineKeyboardButton("Убрать смену",
                                                   callback_data='cancel_invent')
        save_button = types.InlineKeyboardButton("💾 Сохранить!",
                                                 callback_data='save_invent')
        self.markup.add(cancel_button, save_button)
        smen = 'Смены' if self.smens == 'smens' else 'Подработки'
        # Обновляем клавиатуру в том же сообщении
        bot.edit_message_text(
            f"""Вы находитесь в разделе: "{self.selected_month}" - "Смены / подработки" - "<u>{smen}</u>".\n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start\n\nБудет ли инвентаризация?\n✅ - Да\n❌ - Нет""",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=self.markup
        )

    def dop_smens(self):
        self.markup = types.InlineKeyboardMarkup()
        # Создаем кнопки от 1 до 12
        for i in range(2, 13):
            # Проверяем, выбран ли номер, и устанавливаем соответствующий текст кнопки
            if self.selected_number == i:
                button_text = f"{i}ч ✅"  # Зеленая галочка для выбранного номера
            else:
                button_text = f"{i}ч ❌"  # Красный крестик для невыбранного номера
            item = types.InlineKeyboardButton(button_text,
                                              callback_data=f"number_{i}")
            self.markup.add(item)

        # Добавляем кнопки "Отмена" и "Сохранить"
        cancel_button = types.InlineKeyboardButton("Отмена",
                                                   callback_data='cancel')
        save_button = types.InlineKeyboardButton("💾 Сохранить!",
                                                 callback_data='save_smens')
        self.markup.add(cancel_button, save_button)
        smen = 'Смены' if self.smens == 'smens' else 'Подработки'
        # Отправляем сообщение с кнопками
        bot.edit_message_text(
            f"""Вы находитесь в разделе: "{self.selected_month}" - "Смены / подработки" - "<u>{smen}</u>". \n\nИспользуй кнопки для навигации. Чтобы вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберете подработку:\n❌ - не выбранные часы\n✅ - выбранные часы""",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=self.markup
        )


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Запускаем планировщик в отдельном потоке
schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()
Main()
bot.infinity_polling(timeout=90, long_polling_timeout=5)
