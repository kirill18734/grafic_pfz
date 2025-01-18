from config.auto_search_dir import path_to_test1_json
from edit_charts.data_file import DataCharts, get_font_style


# -------------------------------------редактирование смен и подработок --------------------------------

class Editsmens:
    def __init__(self):
        self.file = None
        self.table = DataCharts()

    def smens(self, month, user):
        self.file = self.table.file[month]
        # получаем номер строки где наш пользователь
        find_row = [cell.row for row in self.file.iter_rows(
            max_row=len(self.table.get_users(month)) + 4) for cell in row if
                    user in str(cell.value)]
        result = {}
        count = 1
        for row in self.file.iter_rows(min_col=4, max_row=find_row[0],
                                       min_row=find_row[0]):
            for cell in row:
                if cell.fill.start_color.rgb == 'FF00B0F0':
                    result[f'{count}i'] = cell.value
                else:
                    result[count] = cell.value
                count += 1

        return result

    def get_days(self, month):
        self.file = self.table.file[month]
        result = {}
        count = 1
        for row in self.file.iter_rows(min_col=4, max_row=3, min_row=3):
            for cell in row:
                result[count] = cell.value
                count += 1
        return result

    def edit_smens(self, month, user, new_smens):
        self.file = self.table.file[month]

        # Получаем номер строки, где наш пользователь
        find_row = [cell.row for row in self.file.iter_rows(
            max_row=len(self.table.get_users(month)) + 4) for cell in row if
                    user in str(cell.value)]

        # Проверяем, найден ли пользователь
        if not find_row:
            print("Пользователь не найден.")
            return

        # Предполагаем, что мы работаем только с первой найденной строкой
        target_row = find_row[0]

        # Получаем смены для текущего пользователя
        row_cells = list(self.file.iter_rows(min_col=4, max_row=target_row,
                                             min_row=target_row))[0]

        # Перебираем ячейки в целевой строке
        for count, cell in enumerate(row_cells, start=1):
            key = count if count in new_smens else None
            color = None
            value = None
            if key is not None:
                value = new_smens[key]

                if value is None:
                    color = 'green'
                elif value == 1:
                    color = 'red'
                elif value > 1:
                    color = 'orange'
            else:
                # Проверяем, если ключ строка с 'i'
                str_key = str(count) + 'i'
                if str_key in new_smens:
                    value = new_smens[str_key]
                    if value == 1:
                        color = 'blue'
                    else:
                        continue  # Если значение не 1, пропускаем

            # Обновляем ячейку
            cell.value = value
            cell.border = get_font_style(color)[0]
            cell.font = get_font_style(color)[1]
            cell.fill = get_font_style(color)[2]
            cell.number_format = get_font_style(color)[3]
            cell.protection = get_font_style(color)[4]
            cell.alignment = get_font_style(color)[5]
            if color != 'orange':
                cell.value = get_font_style(color)[6]
        self.table.file.save(path_to_test1_json)
        # получаем уже измененные смены для переданного пользователя
        top_user = list(self.file.iter_rows(min_col=4, max_row=target_row,
                                            min_row=target_row))[0]

        # Сохраняем значения смен текущего пользователя в список
        current_user_smens = [cell.value for cell in top_user]
        # получаем все номера строк других пользователей
        find_row_other_user = set([cell.row for row in self.file.iter_rows(min_row=5,
                                                                           max_row=len(self.table.get_users(month)) + 4)
                                   for cell in row if
                                   user not in str(cell.value) and cell.row != target_row])
        # проходимся по каждой строчки пользователей
        for user_list in find_row_other_user:
            # получем список занчения пользователя
            row_cells_other = list(self.file.iter_rows(min_col=4, max_row=user_list,
                                                       min_row=user_list))[0]
            # проходимся по длине смен нашего главного пользователя
            for i in range(len(current_user_smens)):
                if current_user_smens[i] == 1 and row_cells_other[i].value == 1:
                    color = 'green'
                    row_cells_other[i].value = None  # Устанавливаем None для других пользователей
                    row_cells_other[i].border = get_font_style(color)[0]
                    row_cells_other[i].font = get_font_style(color)[1]
                    row_cells_other[i].fill = get_font_style(color)[2]
                    row_cells_other[i].number_format = get_font_style(color)[3]
                    row_cells_other[i].protection = get_font_style(color)[4]
                    row_cells_other[i].alignment = get_font_style(color)[5]

        self.table.file.save(path_to_test1_json)


# test = Editsmens()
# test.edit_smens('Январь', 'Кирилл', {1: None,
#                                      2: None, 3: 3, 4: None, 5: None, 6: None, 7: 1, 8: 1, 9: None,
#                                      10: None, 11: None, 12: 1, 13: None, 14: None, 15: None, 16: None,
#                                      17: 1, 18: None, 19: 1, 20: None, 21: None, '22i': 1, 23: 7,
#                                      24: 10, 25: 1, 26: None, 27: None, 28: None, 29: None, 30: None,
#                                      31: 1})
