from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from config.auto_search_dir import data_config, path_to_img
from edit_charts.data_file import DataCharts


class Image:
    def __init__(self):
        self.table = None
        self.sheet = None

    def get_image(self, month):
        self.table = DataCharts()
        self.sheet = self.table.file.worksheets
        self.open_site(month)

    def open_site(self, month):
        # Настройка опций для Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Запуск в headless режиме
        # Инициализация драйвера с опциями
        self.driver = webdriver.Chrome(options=chrome_options)

        # Устанавливаем размер окна (ширина, высота)
        self.driver.set_window_size(1600, 1000)
        # Открытие сайта
        self.driver.get(data_config["URL"])

        # Получение HTML-кода страницы
        try:
            # Явное ожидание, пока элемент не станет видимым
            element = WebDriverWait(self.driver, 10).until(
                lambda d: d.find_element(By.XPATH, f"//span[@class='docs-sheet-tab-name' and text()='{month}']")
            )
            element.click()  # Клик на элемент
            sleep(5)
            # Сделать скриншот и сохранить его в файл
            self.driver.save_screenshot(path_to_img)
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            # Закрытие драйвера
            self.driver.quit()