from telebot import types
from telebot.types import BotCommand, InlineKeyboardMarkup, \
    InlineKeyboardButton
import telebot
from config.auto_search_dir import data_config
import urllib3
from edit_charts.create_new_chart import CreateChart
from edit_charts.delete_user import DeleteUsers
from edit_charts.data_file import DataCharts
from edit_charts.adduser import AddUser
from edit_charts.edit_smens import Editsmens

# Отключаем предупреждения
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Создаем экземпляр бота
bot = telebot.TeleBot(data_config['my_telegram_bot']['bot_token'],
                      parse_mode='HTML')


class Main:
    # дополнительный аргумент, для создания нового листа
    def __init__(self, new_chart=None):
        self.selected_number = None
        self.status_dict = {}
        self.smens = None
        self.message_ids = []
        self.select_user = None
        self.month = None
        self.select_smens = None
        self.key = None
        self.state_stack = []  # Стек для хранения состояний
        self.selected_employees = getattr(self, 'selected_employees', set())
        self.user_id = None
        self.data_smens = None
        self.selected_month = None
        self.call = None
        self.markup = None
        self.actualy_months = None
        # если передался параметр на создание графика, то выполняем фукнцию, которая создаться график на новый месяц
        self.input_enabled = False  # Флаг для контроля ввода
        if new_chart:
            CreateChart()
        self.delete_user = None
        self.table_data = None
        self.start_main()

    # начальные кнопки, если нет, нового месяца, но используем текущий, или если он есть, то выводим 2 кнопки
    def get_months(self):
        self.table_data = DataCharts()
        # если крайний лист, будет совпадать с текущим месяцем, то значит будет одна кнопка для текущего месяца,
        # если нет, то 2 для нового графика и для старого
        if self.table_data.list_months[
            self.table_data.data_months()[2]] in str(
            self.table_data.last_list.title):
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
            # Удаляем сообщения в диапазоне
            for id_ in range(message.message_id - 10, message.message_id + 1):
                try:
                    bot.delete_message(chat_id=message.chat.id, message_id=id_)
                except telebot.apihelper.ApiTelegramException as e:
                    if e.error_code == 400:
                        # Сообщение не найдено, продолжаем цикл
                        continue
                    else:
                        # Обработка других ошибок, если необходимо
                        print(f"Ошибка при удалении сообщения: {e}")

            # Удаляем текущее сообщение
            try:
                bot.delete_message(chat_id=message.chat.id,
                                   message_id=message.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                if e.error_code == 400:
                    print("Сообщение для удаления не найдено.")
                else:
                    print(f"Ошибка при удалении сообщения: {e}")

            # После завершения цикла и удаления сообщений вызываем метод выбора месяца
            self.show_month_selection()

        @bot.message_handler(commands=['back'])
        def handle_back(message):
            last_state = self.state_stack.pop()

            bot.delete_message(chat_id=message.chat.id,
                               message_id=message.message_id)
            if last_state == self.month:
                for id_ in range(message.message_id - 10,
                                 message.message_id + 1):
                    try:
                        bot.delete_message(chat_id=message.chat.id,
                                           message_id=id_)
                    except telebot.apihelper.ApiTelegramException as e:
                        if e.error_code == 400:
                            # Сообщение не найдено, продолжаем цикл
                            continue
                        else:
                            # Обработка других ошибок, если необходимо
                            print(f"Ошибка при удалении сообщения: {e}")

                # Удаляем текущее сообщение
                try:
                    bot.delete_message(chat_id=message.chat.id,
                                       message_id=message.message_id)
                except telebot.apihelper.ApiTelegramException as e:
                    if e.error_code == 400:
                        print("Сообщение для удаления не найдено.")
                    else:
                        print(f"Ошибка при удалении сообщения: {e}")
            self.handle_back_state(last_state)

        @bot.callback_query_handler(func=lambda call: True)
        def handle_query(call):
            self.call = call
            if 'Текущий месяц' in self.call.data or 'Следующий месяц' in self.call.data:
                self.state_stack.append(self.call.data)
                # Сохраняем выбранный месяц
                self.selected_month = self.call.data
                # После выбора месяца показываем кнопки "Смены / подработки" и "Сотрудники"
                self.show_sments_dop_sments()

            elif self.call.data == 'shifts_jobs':
                self.state_stack.append(self.call.data)
                # Создаем новую клавиатуру
                self.show_shifts_jobs_selection()

            elif self.call.data in ['smens', 'dop_smens']:
                self.smens = self.call.data
                self.state_stack.append(self.call.data)
                self.smens_users()
            elif self.call.data in ['employees', 'cancel_delete']:
                self.state_stack.append(self.call.data)
                # Обработка кнопки "Сотрудники"
                self.add_del_employees()

            elif self.call.data == 'add_employees':
                self.state_stack.append(self.call.data)
                self.add_employees()
            elif self.call.data == 'dell_employee':
                self.state_stack.append(self.call.data)
                self.dell_employee()

            elif self.call.data.startswith('select_employee_'):
                self.state_stack.append(self.call.data)
                employee_name = self.call.data.split('_', 2)[2]
                if employee_name in self.selected_employees:
                    self.selected_employees.remove(employee_name)
                else:
                    self.selected_employees.add(employee_name)
                self.dell_employee()
            elif self.call.data.startswith('user_'):
                self.table = Editsmens()
                month = str(self.selected_month).replace('Текущий месяц (',
                                                         '').replace(')',
                                                                     '').replace(
                    'Следующий месяц (', '').replace(')', '')
                self.status_dict = self.table.smens(month,
                                                    str(self.call.data).replace(
                                                        'user_', ''))
                self.actualy_smens()
                # print(f'Вы выбрали пользователя: {self.call.data}')
            # если выбран сотрудник на удаление, то вызываем функию для
            # удаления
            elif self.call.data == 'confirm_delete':
                self.state_stack.append(self.call.data)
                if self.selected_employees:
                    self.delete_user = DeleteUsers()
                    self.delete_user.delete(list(self.selected_employees),
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
                self.select_user = str(self.call.data).replace(
                    (self.smens + '_'), '')
                key, current_value = self.call.data.split((self.smens + '_'))
                self.key = int(key)
                if self.smens == 'smens':
                    if current_value == 'None':
                        self.status_dict[self.key] = 1
                        self.actualy_smens()
                    elif current_value == '1':
                        self.status_dict[self.key] = None
                        self.actualy_smens()
                    else:
                        response_text = "Чтобы изменить подработку, перейдите пожалуйста в раздел 'Подработки'."
                        bot.answer_callback_query(call.id, response_text,
                                                  show_alert=True)
                if self.smens == 'dop_smens':
                    if current_value == '1':
                        response_text = "Чтобы изменить смену, перейдите пожалуйста в раздел 'Смены'."
                        bot.answer_callback_query(call.id, response_text,
                                                  show_alert=True)
                    else:
                        self.selected_number = self.status_dict[self.key]
                        self.dop_smens()

                # Обновляем кнопки
            elif self.call.data.startswith("number_"):
                selected_number = int(call.data.split("_")[1])
                # Проверяем, выбран ли номер
                if self.selected_number == selected_number:
                    self.selected_number = None  # Снимаем выбор, если номер уже выбран
                else:
                    self.selected_number = selected_number  # Сохраняем новый выбранный номер

                self.dop_smens()  # Обновляем кнопки
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
                response_text = "Изменения сохранены."
                bot.answer_callback_query(call.id, response_text,
                                          show_alert=True)
                self.smens_users()
            elif self.call.data in ['cancel_all_smens']:
                self.smens_users()

    def handle_back_state(self, last_state):

        if last_state in ['shifts_jobs', 'employees']:

            self.show_sments_dop_sments()

        elif last_state in ['smens', 'dop_smens']:

            self.show_shifts_jobs_selection()

        elif last_state in ['add_employees', 'dell_employee']:
            self.А()
        elif last_state == self.month:
            self.show_month_selection()

    def show_month_selection(self):
        self.markup = InlineKeyboardMarkup()
        buttons = []

        for month in self.get_months():
            self.month = month
            item = InlineKeyboardButton(month, callback_data=self.month)

            buttons.append(item)

        self.markup = InlineKeyboardMarkup([buttons])

        bot.send_message(self.user_id, "Выберите месяц:",
                         reply_markup=self.markup)

    def show_sments_dop_sments(self):
        self.markup = InlineKeyboardMarkup()
        item2 = InlineKeyboardButton("Смены / подработки",
                                     callback_data='shifts_jobs')
        item3 = InlineKeyboardButton("Сотрудники", callback_data='employees')
        self.markup.add(item2, item3)

        # Обновляем клавиатуру в том же сообщении
        bot.edit_message_text(
            f"Вы находитесь в разделе: {self.selected_month}.\n\nИспользуй кнопки для навигации. Чтобы "
            f"вернуться на шаг назад, используй команду /back. В начало /start\n\nВыберете раздел:",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=self.markup)

    def show_shifts_jobs_selection(self):

        self.markup = InlineKeyboardMarkup()

        item2 = InlineKeyboardButton("Смены", callback_data='smens')

        item3 = InlineKeyboardButton("Подработки", callback_data='dop_smens')

        self.markup.add(item2, item3)

        bot.edit_message_text(

            f"Вы находитесь в разделе: {self.selected_month}.\n\nИспользуй кнопки для навигации. Чтобы "

            f"вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберите раздел:",

            chat_id=self.call.message.chat.id,

            message_id=self.call.message.message_id,

            reply_markup=self.markup

        )

    def add_del_employees(self):
        new_markup = types.InlineKeyboardMarkup()
        item4 = types.InlineKeyboardButton("Добавить сотрудника",
                                           callback_data='add_employees')
        item5 = types.InlineKeyboardButton("Убрать сотрудника",
                                           callback_data='dell_employee')
        new_markup.add(item4, item5)

        bot.edit_message_text(
            f"Вы находитесь в разделе: {self.selected_month}.\n\nИспользуй кнопки для навигации. Чтобы "
            f"вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберите раздел:",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=new_markup)

    def add_employees(self):
        # Редактируем текущее сообщение, чтобы запросить имя сотрудника
        bot.edit_message_text(
            f"Вы находитесь в разделе: {self.selected_month}.\n\nИспользуй кнопки для навигации. Чтобы "
            f"вернуться на шаг назад, используй команду /back. В начало /start \n\nНапишите имя сотрудника "
            f"для добавления",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id
        )

        # Устанавливаем состояние ожидания ответа от пользователя
        bot.register_next_step_handler(self.call.message,
                                       self.process_employee_name)

    def process_employee_name(self, message):
        if message.text not in ['/back', '/start']:
            employee_name = message.text  # Получаем введенное имя сотрудника
            add_users = AddUser()
            add_users.add(employee_name, self.actualy_months)
            bot.delete_message(chat_id=message.chat.id,
                               message_id=message.message_id)
            # Здесь вы можете обработать имя сотрудника, например, сохранить его в базе данных
            response_text = f"Сотрудник {employee_name} добавлен."
            bot.answer_callback_query(self.call.id, response_text,
                                      show_alert=True)
        self.add_del_employees()

    def dell_employee(self):

        employees = self.table_data.get_users()  # Получаем список сотрудников за последний месяц

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
            f"Вы находитесь в разделе: {self.selected_month}. \n\nИспользуй кнопки для навигации. Чтобы "
            f"вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберите сотрудников для удаления:",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=new_markup
        )

    def smens_users(self):
        self.markup = types.InlineKeyboardMarkup()
        buttons = []
        # Получаем список пользователей
        users = self.table_data.get_users()

        for user in users:
            # Используем имя пользователя в качестве callback_data
            item = types.InlineKeyboardButton(user,
                                              callback_data=f'user_{user}')
            buttons.append(item)

        self.markup.add(*buttons)

        bot.edit_message_text(
            f"Вы находитесь в разделе: {self.selected_month}. \n\nИспользуй кнопки для навигации. Чтобы "
            f"вернуться на шаг назад, используй команду /back. В начало /start \n\nВыберите сотрудника:",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=self.markup
        )

    def actualy_smens(self):
        self.markup = types.InlineKeyboardMarkup()
        buttons = []
        for key, value in self.status_dict.items():
            if value is None:
                emoji = "❌"  # Красный крестик
            elif value == 1:
                emoji = "✅"  # Зеленая галочка
            else:
                emoji = "🟠"  # Знак будильника

            button_text = f"{key} {emoji}"
            item = types.InlineKeyboardButton(button_text,
                                              callback_data=f"{key}{self.smens}_{value}")
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
            f"Вы находитесь в разделе: {self.selected_month}. \n\nИспользуй кнопки для навигации. Чтобы "
            f"вернуться на шаг назад, используй команду /back. В начало /start \n\nРаздел '{smen}':\n❌ - выходной\n✅ - смена\n🟠 - подработка",
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
                button_text = f"{i} ✅"  # Зеленая галочка для выбранного номера
            else:
                button_text = f"{i} ❌"  # Красный крестик для невыбранного номера
            item = types.InlineKeyboardButton(button_text,
                                              callback_data=f"number_{i}")
            self.markup.add(item)

        # Добавляем кнопки "Отмена" и "Сохранить"
        cancel_button = types.InlineKeyboardButton("Отмена",
                                                   callback_data='cancel')
        save_button = types.InlineKeyboardButton("💾 Сохранить!",
                                                 callback_data='save_smens')
        self.markup.add(cancel_button, save_button)

        # Отправляем сообщение с кнопками
        bot.edit_message_text(
            f"Вы находитесь в разделе: {self.selected_month}. \n\nИспользуй кнопки для навигации. Чтобы "
            f"вернуться на шаг назад, используй команду /back. В начало /start \n\nРаздел 'Подработки\ч':\n❌ - не выбранные часы\n✅ - выбранные часы",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=self.markup
        )


# Main(sys.argv)
Main()
bot.infinity_polling(timeout=90, long_polling_timeout=5)
