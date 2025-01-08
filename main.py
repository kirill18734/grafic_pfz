from telebot import types
from telebot.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
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
        self.select_user = None
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
        if self.table_data.list_months[self.table_data.data_months()[2]] in str(self.table_data.last_list.title):
            self.actualy_months = [self.table_data.list_months[self.table_data.data_months()[2]]]
            return [f'Текущий месяц ({self.table_data.list_months[self.table_data.data_months()[2]]})']
        else:
            self.actualy_months = [self.table_data.list_months[self.table_data.data_months()[2]],
                                   self.table_data.list_months[self.table_data.data_months()[3]]]
            return [f'Текущий месяц ({self.table_data.list_months[self.table_data.data_months()[2]]})',
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
            self.show_month_selection()

        @bot.message_handler(commands=['back'])
        def handle_back(message):
            if self.state_stack:
                last_state = self.state_stack.pop()
                self.handle_back_state(last_state)
            else:
                bot.send_message(message.chat.id, "Вы находитесь на начальном экране. Нельзя вернуться назад.")

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

            elif self.call.data == 'sments':
                self.smens = self.call.data
                self.state_stack.append(self.call.data)
                self.smens_users()
            elif self.call.data == 'dop_smens':
                self.smens = self.call.data
                self.state_stack.append(self.call.data)
                self.smens_users()
            elif self.call.data == 'employees':
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
                month = str(self.selected_month).replace('Текущий месяц (', '').replace(')', '')

                self.status_dict = self.table.smens(month, str(self.call.data).replace('user_', ''))
                self.actualy_smens()
                # print(f'Вы выбрали пользователя: {self.call.data}')
            # если выбран сотрудник на удаление, то вызываем функию для удаления
            elif self.call.data == 'confirm_delete':
                self.state_stack.append(self.call.data)
                if self.selected_employees:
                    self.delete_user = DeleteUsers()
                    self.delete_user.delete(list(self.selected_employees), self.actualy_months)
                else:
                    print('Никто не выбран, некого удалять')
                # Обработка статусов
            elif 'smens_' in self.call.data:
                self.select_user = str(self.call.data).replace('smens_', '')
                key, current_value = self.call.data.split('smens_')
                key = int(key)
                if current_value == 'None':
                    self.status_dict[key] = 1
                elif current_value == '1':
                    self.status_dict[key] = None
                else:
                    # response_text = "Чтобы изменить подработку, перейдите, пожалуйста, в раздел 'подработки'."
                    # bot.answer_callback_query(call.id, response_text, show_alert=True)
                    self.dop_smens()

                self.actualy_smens()  # Обновляем кнопки
            elif self.call.data.startswith("number_"):
                selected_number = int(call.data.split("_")[1])
                self.selected_number = selected_number  # Сохраняем выбранный номер

            elif call.data == 'cancel':
                # Логика для отмены
                self.actualy_smens()
            elif call.data == 'save_smens':
                pass
    def handle_back_state(self, last_state):

        if last_state in ['shifts_jobs', 'employees']:

            self.show_sments_dop_sments()

        elif last_state in ['sments', 'dop_smens']:

            self.show_shifts_jobs_selection()

        elif last_state in ['add_employees', 'dell_employee', 'employees']:
            self.add_del_employees()
        else:
            self.show_month_selection()

    def show_month_selection(self):

        self.markup = InlineKeyboardMarkup()

        buttons = []

        for month in self.get_months():
            item = InlineKeyboardButton(month, callback_data=month)

            buttons.append(item)

        self.markup = InlineKeyboardMarkup([buttons])

        bot.send_message(self.user_id, "Выберите месяц:", reply_markup=self.markup)

    def show_sments_dop_sments(self):
        self.markup = InlineKeyboardMarkup()
        item2 = InlineKeyboardButton("Смены / подработки", callback_data='shifts_jobs')
        item3 = InlineKeyboardButton("Сотрудники", callback_data='employees')
        self.markup.add(item2, item3)

        # Обновляем клавиатуру в том же сообщении
        bot.edit_message_text(
            f"Вы находитесь в разделе: {self.selected_month}.\nИспользуй кнопки для навигации. Чтобы "
            f"вернуться на шаг назад, используй команду /back. В начало /start",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=self.markup)

    def show_shifts_jobs_selection(self):

        self.markup = InlineKeyboardMarkup()

        item2 = InlineKeyboardButton("Смены", callback_data='sments')

        item3 = InlineKeyboardButton("Подработки", callback_data='dop_smens')

        self.markup.add(item2, item3)

        bot.edit_message_text(

            f"Вы находитесь в разделе: {self.selected_month}.\n Используй кнопки для навигации. Чтобы "

            f"вернуться на шаг назад, используй команду /back. В начало /start \n Выберите опцию:",

            chat_id=self.call.message.chat.id,

            message_id=self.call.message.message_id,

            reply_markup=self.markup

        )

    def add_del_employees(self):
        new_markup = types.InlineKeyboardMarkup()
        item4 = types.InlineKeyboardButton("Добавить сотрудника", callback_data='add_employees')
        item5 = types.InlineKeyboardButton("Убрать сотрудника", callback_data='dell_employee')
        new_markup.add(item4, item5)

        bot.edit_message_text(
            f"Вы находитесь в разделе: {self.selected_month}.\n Используй кнопки для навигации. Чтобы "
            f"вернуться на шаг назад, используй команду /back. В начало /start \n Выберите опцию:",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=new_markup)

    def add_employees(self):
        bot.send_message(self.call.message.chat.id,
                         f"Вы находитесь в разделе: {self.selected_month}.\n Используй кнопки для навигации. Чтобы "
                         f"вернуться на шаг назад, используй команду /back. В начало /start \n Напишите сотрудника "
                         f"для добавления")
        # Устанавливаем состояние ожидания ответа от пользователя
        bot.register_next_step_handler(self.call.message, self.process_employee_name)

    def process_employee_name(self, message):
        if message.text not in ['/back', '/start']:
            employee_name = message.text  # Получаем введенное имя сотрудника
            add_users = AddUser()
            add_users.add(employee_name, self.actualy_months)
            # Здесь вы можете обработать имя сотрудника, например, сохранить его в базе данных
            bot.send_message(message.chat.id, f"Сотрудник {employee_name} добавлен.")
        else:
            self.handle_back_state('employees')

    def dell_employee(self):

        employees = self.table_data.get_users()  # Получаем список сотрудников за последний месяц

        new_markup = InlineKeyboardMarkup()

        # Добавляем кнопки для сотрудников по 2 в строке
        for i in range(0, len(employees), 2):
            # Берем два сотрудника за раз
            row_buttons = []
            for j in range(2):
                if i + j < len(employees):  # Проверяем, чтобы не выйти за пределы списка
                    employee = employees[i + j]
                    is_selected = employee in self.selected_employees
                    button_text = f"{employee} {'❌' if is_selected else '✅'}"
                    item = InlineKeyboardButton(button_text, callback_data=f'select_employee_{employee}')
                    row_buttons.append(item)

            # Добавляем кнопки в строку
            new_markup.row(*row_buttons)

        # Добавляем кнопку "Удалить"
        delete_button = InlineKeyboardButton("🗑️ Удалить!", callback_data='confirm_delete')
        new_markup.add(delete_button)

        bot.edit_message_text(
            f"Вы находитесь в разделе: {self.selected_month}. Используй кнопки для навигации. Чтобы "
            f"вернуться на шаг назад, используй команду /back. В начало /start \n Выберите сотрудников для удаления:",
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
            item = types.InlineKeyboardButton(user, callback_data=f'user_{user}')
            buttons.append(item)

        self.markup.add(*buttons)

        bot.edit_message_text(
            "Выберите сотрудника:",
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
            item = types.InlineKeyboardButton(button_text, callback_data=f"{key}smens_{value}")
            buttons.append(item)

        self.markup.add(*buttons)
        # Добавляем кнопку "Удалить"
        save_smens = InlineKeyboardButton("💾 Сохранить!", callback_data='save_smens')
        self.markup.add(save_smens)
        bot.edit_message_text(
            "Выберите статус:",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=self.markup
        )


    def dop_smens(self):
        # Создаем кнопки от 1 до 12
        for i in range(1, 13):
            button_text = f"{i} {'✅' if self.selected_number == i else '❌'}"  # Зеленая галочка для выбранного номера
            item = types.InlineKeyboardButton(button_text, callback_data=f"number_{i}")
            self.markup.add(item)

        # Добавляем кнопки "Отмена" и "Сохранить"
        cancel_button = types.InlineKeyboardButton("❌ Отмена", callback_data='cancel')
        save_button = types.InlineKeyboardButton("💾 Сохранить!", callback_data='save_smens')
        self.markup.add(cancel_button, save_button)

        # Отправляем сообщение с кнопками
        bot.edit_message_text(
            "Выберите номер:",
            chat_id=self.call.message.chat.id,
            message_id=self.call.message.message_id,
            reply_markup=self.markup
        )

# Main(sys.argv)
Main()
bot.infinity_polling(timeout=90, long_polling_timeout=5)
