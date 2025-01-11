import os
from time import sleep
from selenium import webdriver
from config.auto_search_dir import data_config, path_to_test1_json
from edit_charts.data_file import DataCharts

user_data_dir = os.path.join(os.getenv('APPDATA'), 'Local', 'Google', 'Chrome', 'User Data')
remote_debugging_port = 3294

# Указываем путь к исполняемому файлу Chrome
chrome_driver_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'


# # пример испоьзования с динапический изминением компонента и ответственных
class Image:
    def __init__(self):
        self.table = None
        self.sheet = None

    def get_image(self, month):
        self.table = DataCharts()
        self.sheet = self.table.file.worksheets
        # если переданный месяц не совпадает с последним, то скрывает последний, чтобы отправить предпоследний
        if month not in str(self.sheet[-1]):
            self.table = DataCharts()
            self.sheet = self.table.file.worksheets
            # Скрыть лист "Январь"
            sheet = self.table.file[str(self.sheet[-1].title)]
            sheet.sheet_state = 'hidden'
            # Установить активным последний лист
            last_sheet_index = len(self.table.file.worksheets) - 2  # Индекс последнего листа

            self.table.file.active = last_sheet_index  # Установка активного листа
            sleep(10)
            self.table.file.save(path_to_test1_json)
            self.table.file.close()
            # Сохранить изменения

        else:
            self.table = DataCharts()
            self.sheet = self.table.file.worksheets
            # Скрыть лист "Январь"
            sheet = self.table.file[str(self.sheet[-1].title)]
            sheet.sheet_state = 'visible'
            # Установить активным последний лист
            last_sheet_index = len(self.table.file.worksheets) -1   # Индекс последнего листа
            self.table.file.active = last_sheet_index  # Установка активного листа
            self.table.file.save(path_to_test1_json)
            self.table.file.close()

            # Сохранить изменения
            # self.table.file.save(path_to_test1_json)
            # self.table.file.close()

        # Создаем объект ActionChains
        # Закрыть драйвер

    def open_site(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--allow-profiles-outside-user-dir')
        self.options.add_argument('--enable-profile-shortcut-manager')
        self.options.add_argument('--profile-directory=Profile 1')
        self.options.add_argument(f'--user-data-dir={user_data_dir}')
        # self.options.add_argument("profile-directory=Default")
        # self.options.add_experimental_option('detach', True)
        # self. options.add_argument("profile-directory=Default")
        # self.options.add_argument(f'--remote-debugging-port={remote_debugging_port}')
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()
        self.driver.get(r"https://1drv.ms/x/c/2a8d7b22fa9923e0/EeAjmfoie40ggCrdBgAAAAABK-qPQ1HNSCZeBBvyAFPJeg?e=Fdqxvy")
        # self.driver.get(data_config["URL"])
        # Получение HTML-кода страницыs
        # Сделать скриншот и сохранить его в файл
        self.driver.save_screenshot('screenshot.png')

        self.driver.quit()
        self.driver.close()


test = Image()
test.get_image('Январь')
