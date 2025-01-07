from edit_charts.data_file import DataCharts
import re


class DeleteUsers:
    def __init__(self):
        self.table = DataCharts()
        self.file = self.table.file

    # изменяем координаты для суммирования строк
    def edit_summ(self):
        # первый сотрудник начинается с 5 строчки
        count = 5
        rows_to_update = []
        # Проходим по каждой строке в файле
        for row in self.file.iter_rows():
            # Извлекаем значения ячеек в строке и сохраняем их в список
            row_values = [cell.value for cell in row]

            # Проверяем, содержится ли хотя бы один пользователь и формула '=SUMIF' в значениях строки
            if any(user in str(row_values) for user in self.table.get_users()) and '=SUMIF' in str(row_values):
                # Если условие выполнено, выполняем нужные действия (например, печатаем что-то)
                rows_to_update.append(row)
            # Заменяем значения в определенных ячейках
        for row in rows_to_update:
            for cell in row:
                if isinstance(cell.value, str):  # Проверяем, является ли значение строкой
                    cell.value = re.sub(
                        r'([A-Z]+)(\d+):([A-Z]+)(\d+)',
                        lambda m: f"{m.group(1)}{count}:{m.group(3)}{count}",
                        cell.value
                    )

            count += 1

    def unmerge(self, start_row, rows=None):
        merged_ranges = []  # Список для хранения диапазонов объединенных ячеек
        # перебираем все ячейки, где есть объединение
        for merged in list(self.file.merged_cells.ranges):
            # Получаем диапазон объединенных ячеек
            min_col, min_row, max_col, max_row = merged.bounds
            # Если объединенные ячейки начинаются на строке больше или равной start_row, разъединяем их
            if min_row >= start_row:
                merged_ranges.append(merged)  # Сохраняем диапазон для последующего объединения
                self.file.unmerge_cells(str(merged))

        # Удаляем строки
        for row in reversed(rows):
            self.file.delete_rows(row)

        # Объединяем ячейки обратно с учетом сдвига
        for merged in merged_ranges:
            # Получаем диапазон объединенных ячеек
            min_col, min_row, max_col, max_row = merged.bounds
            # Уменьшаем min_row и max_row на 1, чтобы учесть сдвиг
            self.file.merge_cells(start_row=min_row - 1, start_column=min_col, end_row=max_row - 1,
                                  end_column=max_col)
        self.edit_summ()
        self.table.file.save('test1.xlsx')

    def delete(self, users, months):
        for month in months:
            self.file = self.file[month]
            for user in users:
                # получаем все строки, которые нужно удалить
                row_del_users = [cell.row for row in self.file.iter_rows() for cell in row if user in str(cell.value)]
                # проверяем есть ли пользователь

                if row_del_users:
                    # вызываем функцию для удаления , где указываем
                    self.unmerge(len(self.table.get_users()) + 5, row_del_users)
        self.table.file.save('test1.xlsx')
