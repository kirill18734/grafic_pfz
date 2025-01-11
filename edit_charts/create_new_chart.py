from copy import copy

from config.auto_search_dir import path_to_test1_json
from edit_charts.data_file import DataCharts, get_font_style


class CreateChart:

    def __init__(self):
        # список всех месяцев
        self.find_start_B_result = None
        self.find_end_B_result = None
        self.new_index = None
        self.source = None
        self.new_list = None
        self.result = None
        self.start_row = None
        self.start_col = None
        self.file = None
        self.table_data = DataCharts()
        self.weekdays = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
        self.list_days_2 = {28: "AE", 29: "AF", 30: "AG", 31: "AH",
                            32: "AI", 33: "AJ", 34: "AK"}
        self.new_chart()  # запускаем основную функцию по созданию нового месяца

    def add_colls(self, cell, i, new_value):
        # присваиваем скопированному последнему столбцу переменную, где будет все храниться
        new_cell = self.file.cell(row=cell.row,
                                  column=cell.column + i,
                                  value=new_value)

        # если у этой ячейки есть стили , то также копируем их
        if cell.has_style:
            new_cell.font = copy(cell.font)
            new_cell.border = copy(cell.border)
            new_cell.fill = copy(cell.fill)
            new_cell.number_format = copy(
                cell.number_format)
            new_cell.protection = copy(cell.protection)
            new_cell.alignment = copy(cell.alignment)
            original_width = \
                self.file.column_dimensions[
                    cell.column_letter].width
            new_column_letter = self.file.cell(
                row=cell.row,
                column=cell.column + i).column_letter
            self.file.column_dimensions[
                new_column_letter].width = original_width

            original_height = self.file.row_dimensions[cell.row].height
            self.file.row_dimensions[new_cell.row].height = original_height

    # удаляем лишние звездочки до крайнего последнего столбца, лишние
    def remove(self, coll, count_remove):
        # удалеяем столбцы по коодинатам
        self.file.delete_cols(coll, count_remove)
        # в последнем столбце указываем звездочку
        self.file.cell(row=1, column=coll - 1).value = '*'
        self.table_data.file.save(
            path_to_test1_json)
        # проставляем актуальные дни недели
        self.days_week(-count_remove)
        # очищаем таблицу
        self.clear_table()
        # изменяем сумированые ячейки
        self.edit_summ(-count_remove)

    def edit_summ(self, count_add):
        # также изменяем ячейки для суммирования резульата
        for row in self.file.iter_rows(min_row=len(self.table_data.get_users()) + 10,
                                       min_col=18):
            for cell in row:
                if self.list_days_2[self.table_data.data_months()[0]] in str(
                        cell.value):  # Получаем значения в текущей строке
                    text = str(cell.value).replace(
                        self.list_days_2[self.table_data.data_months()[0]],
                        self.list_days_2[self.table_data.data_months()[0] + count_add])
                    cell.value = text

    def clear_table(self):
        # очищаем таблицу
        for row in range(5, len(self.table_data.get_users()) + 5):
            for col in range(4, self.file.max_column + 1):
                cell = self.file.cell(row=row, column=col)
                cell.value = None  # Устанавливаем значение на None
                cell.font = get_font_style('green')[0]  # Применяем стиль шрифта
                cell.fill = get_font_style('green')[
                    1]  # Применяем стиль заливки # Устанавливаем значение на None

    # простовляем актуальные дни недели для нового месяца
    def days_week(self, count_add):
        for col in range(4, self.file.max_column):
            start_index = self.table_data.data_months()[4]  # индекс первого для неделя для нового месяца
            for i in range(self.table_data.data_months()[0] + count_add):  # проходил полные дни для нового месяца
                # Вычисляем текущий индекс с помощью остатка от деления
                current_index = (start_index + i) % len(
                    self.weekdays)  # определяем новый день день недели для каждой итерации
                # изменяем значение дня недели на актуальный день
                self.file.cell(row=3, column=i + 4).value = self.weekdays[
                    current_index]

    def copy_range(self, coll, count_add):
        # получаем старый лист
        for i in range(1, count_add + 1):
            for row in self.file.iter_rows(min_col=coll, max_col=coll):
                for cell in row:  # получаем каждую ячейку
                    # добавляем дни для каждой новой ячейки
                    if cell.row == 4:
                        new_value = cell.value + i if isinstance(
                            cell.value, (int, float)) else cell.value
                    else:
                        new_value = cell.value

                    self.add_colls(cell, i, new_value)
        # вызываем фукнцию для проставления актуальных дней недели
        self.days_week(count_add)

        # убираем лишние звездочки
        for col in range(coll - 1,
                         self.file.max_column):
            if coll != self.file.max_column - 1:
                self.file.cell(row=1,
                               column=col).value = None

        # очищаем таблицу
        self.clear_table()
        # изменяем сумированые ячейки
        self.edit_summ(count_add)

    # новый график
    def new_chart(self):
        # Перед созданием нового листа, сначала удаляем старый с таким же названием
        for sheet in self.table_data.file.worksheets:
            if self.table_data.list_months[self.table_data.data_months()[3]] in sheet.title:
                self.table_data.file.remove(sheet)  # Удаляем лист c
        self.table_data.file.save(
            path_to_test1_json)
        # Создаем копию крайнего месяца
        self.file = self.table_data.file.copy_worksheet(self.table_data.last_list)
        # изменяем название страницы (следующий месяц)
        self.file.title = f'{self.table_data.list_months[self.table_data.data_months()[3]]}'
        # изменяем  заголовки на новый месяц
        for row in self.file.iter_rows():
            for cell in row:
                if self.table_data.list_months[self.table_data.data_months()[2]] in str(cell.value):
                    cell.value = str(cell.value).replace(self.table_data.list_months[self.table_data.data_months()[2]],
                                                         self.table_data.list_months[self.table_data.data_months()[3]])
        last_coll = len(self.table_data.ineration_all_last_table(min_row=2, max_row=2))
        # перед добавление или удалением новых ячеек , сначала нужно разъеденить все ячейки, которые взаимодиествуют
        # при добавлении новых
        self.file.unmerge_cells(start_row=2, start_column=2, end_row=2, end_column=last_coll)
        # дальше определяем что нужно сделать с ячейки, добавить или удалить по нашему выводу:
        # если будет вычитание , то преобразовываем в положительно число
        count_edit_coll = abs(self.table_data.data_months()[1])
        if self.table_data.data_months()[1] > 0:
            # передаем столбец, который будем копировать  и количество копий
            self.copy_range(self.file.max_column, count_edit_coll)
        elif self.table_data.data_months()[1] < 0:
            # вызываем функцию для удаления , принимает параметры, с какого столбца удалить, сколько строк
            self.remove((last_coll + 1) - count_edit_coll, count_edit_coll)
        else:
            self.clear_table()
            self.days_week(self.table_data.data_months()[1])

        # после всех обработок объединяем обратно
        self.file.merge_cells(start_row=2, start_column=2, end_row=2,
                              end_column=last_coll + self.table_data.data_months()[1])

        self.table_data.file.save(
            path_to_test1_json)
