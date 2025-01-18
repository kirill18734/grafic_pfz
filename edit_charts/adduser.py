import logging
import re
from config.auto_search_dir import path_to_test1_json
from edit_charts.data_file import DataCharts, get_font_style
from copy import copy


# -------------------------------------добавление пользователя --------------------------------
class AddUser:
    def __init__(self):
        self.month = None
        self.file = None
        self.merged_ranges = None
        self.name = None
        self.table = DataCharts()

    # проставляем каждому пользователя акутальные подсчет через =SUMIF
    def edit_summ(self):
        count = 5
        rows_to_update = []

        # Проходим по каждой строке в файле
        for row in self.file.iter_rows():
            # Извлекаем значения ячеек в строке и сохраняем их в список
            row_values = [cell.value for cell in row]

            # Проверяем, содержится ли хотя бы один пользователь и формула '=SUMIF' в значениях строки
            if (user for user in self.table.get_users(self.month) if user in str(row_values)) and '=SUMIF' in str(
                    row_values):
                # Если условие выполнено, выполняем нужные действия (например, печатаем что-то)
                rows_to_update.append(row)

            # Заменяем значения в определенных ячейках
        for row in rows_to_update:
            for cell in row:
                if isinstance(cell.value,
                              str):  # Проверяем, является ли значение строкой
                    cell.value = re.sub(
                        r'([A-Z]+)(\d+):([A-Z]+)(\d+)',
                        lambda m: f"{m.group(1)}{count}:{m.group(3)}{count}",
                        cell.value
                    )
            count += 1

    # объединение тех ячеек, которые были разъеденены
    def merge(self, last_index):
        # проставляем имя (дополнительная)

        self.file.cell(row=last_index, column=13, value=self.name)
        # проставляем имя (основная)
        self.file.cell(row=len(self.table.get_users(self.month)) + 4, column=2,
                       value=self.name)

        # Обработка объединенных диапазонов
        for merged in self.merged_ranges:
            # Получаем границы диапазона
            min_col, min_row, max_col, max_row = merged.bounds

            # Уменьшаем min_row и max_row на 1, чтобы учесть сдвиг
            self.file.merge_cells(start_row=min_row + 1, start_column=min_col,
                                  end_row=max_row + 1,
                                  end_column=max_col)
        # также отдельно объединяем новые ячейки (основная таблица)
        row_merge = len(self.table.get_users(self.month)) + 3
        self.file.merge_cells(start_row=row_merge, start_column=2,
                              end_row=row_merge,
                              end_column=3)
        # также отдельно объединяем новые ячейки (дополнительная таблица)
        row_merge = last_index
        self.file.merge_cells(start_row=row_merge, start_column=13,
                              end_row=row_merge,
                              end_column=14)
        self.file.merge_cells(start_row=row_merge, start_column=15,
                              end_row=row_merge,
                              end_column=17)
        self.file.merge_cells(start_row=row_merge, start_column=18,
                              end_row=row_merge,
                              end_column=20)

    # разъединение необходимых ячеек
    def unmerge(self, start_row):
        merged_cells = self.file.merged_cells.ranges
        self.merged_ranges = []  # Список для хранения диапазонов объединенных ячеек

        for merged in list(sorted(merged_cells)):
            # Получаем диапазон объединенных ячеек
            min_col, min_row, max_col, max_row = merged.bounds
            # Если объединенные ячейки начинаются на строке больше или равной start_row, разъединяем их
            if min_row >= start_row:
                self.merged_ranges.append(
                    merged)  # Сохраняем диапазон для последующего объединения
                self.file.unmerge_cells(str(merged))

    # копирование 2 последних ячеек в последних строчках 2 таблиц, где пользовати и добавление в следующие
    def add_colls(self, row):
        for row in self.file.iter_rows(min_row=row, max_row=row):
            for cell in row:  # получаем каждую ячейку
                new_value = cell.value

                # стилизация для основной таблицы
                if cell.row <= len(
                        self.table.get_users(self.month)) + 5 and cell.column > 3:

                    # присваиваем скопированному последнему столбцу переменную, где будет все храниться
                    new_cell = self.file.cell(row=cell.row + 1,
                                              column=cell.column)
                    # делаем новую стилизацию для основного столбца для новой ячейки (убираем все смены, которые были у предыдущего пользователя, с которого скопировали строчку  )
                    new_cell.border = get_font_style('green')[0]
                    new_cell.font = get_font_style('green')[1]
                    new_cell.fill = get_font_style('green')[2]
                    new_cell.number_format = get_font_style('green')[3]
                    new_cell.protection = get_font_style('green')[4]
                    new_cell.alignment = get_font_style('green')[5]
                    new_cell.value = get_font_style('green')[6]

                # дополнительная
                else:
                    # присваиваем скопированному последнему столбцу переменную, где будет все храниться
                    new_cell = self.file.cell(row=cell.row + 1,
                                              column=cell.column,
                                              value=new_value)
                    # если у этой ячейки есть стили, то также копируем их
                    if cell.has_style:
                        new_cell.font = copy(cell.font)
                        new_cell.border = copy(cell.border)
                        new_cell.fill = copy(cell.fill)
                        new_cell.number_format = copy(
                            cell.number_format)
                        new_cell.protection = copy(cell.protection)
                        new_cell.alignment = copy(cell.alignment)
                    # копируем ширину ячейки
                    original_width = \
                        self.file.column_dimensions[
                            cell.column_letter].width
                    new_column_letter = self.file.cell(
                        row=cell.row,
                        column=cell.column + 1).column_letter
                    self.file.column_dimensions[
                        new_column_letter].width = original_width

                    # Копируем высоту ячейки
                    original_height = self.file.row_dimensions[cell.row].height
                    self.file.row_dimensions[new_cell.row].height = original_height

    # основная фукнция по добавлению,которая объединяет другие
    def add(self, name, months):
        for month in months:
            self.month = month
            self.name = name
            self.file = self.table.file[month]
            # определяем крайнию строчку, где последний пользователь
            last_user_undex = [cell.row for row in
                               self.file.iter_rows(max_col=13, min_col=13,
                                                   min_row=len(
                                                       self.table.get_users(
                                                           self.month)) + 10)
                               for cell
                               in
                               row if
                               cell.value is not None and cell.value != '' and cell.value != ' '][
                -1]
            # перед каким либо изменением необходимо обязтельно разъеденить все ячейки которые объеденены
            self.unmerge(len(self.table.get_users(self.month)) + 4)
            # вставляем новую строчку в основной стобцец
            self.file.insert_rows(len(self.table.get_users(self.month)) + 5)
            # вставляем новую строчку в дополнительный столбец
            self.file.insert_rows(last_user_undex + 2)
            # вызываем фукнцию для копирования последней строчки и вставке в новую (основной)
            self.add_colls(len(self.table.get_users(self.month)) + 4)
            # вызываем фукнцию для копирования последней строчки и вставке в новую (дополнительный)
            self.add_colls(last_user_undex + 1)
            # обратно все склеиваем
            self.merge(last_user_undex + 2)
            # вызываем функцию для обновления формул автоподсчета
            self.edit_summ()
            self.table.file.save(path_to_test1_json)
            self.table.file.close()

# test = AddUser()
# test.add('Домой', ['Январь', 'Февраль', 'Декабрь'])
