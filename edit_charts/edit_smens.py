from edit_charts.data_file import DataCharts
from send_to_telegram_email.send_to_TG_email import test_mode


class Editsmens:
    def __init__(self):
        self.file = None
        self.table = DataCharts()

    def smens(self, month, user):
        self.file = self.table.file[month]
        # получаем номер строки где наш пользователь
        find_row= [cell.row for row in self.file.iter_rows(max_row=len(self.table.get_users()) + 4) for cell in row if user in str(cell.value)]
        result= {}
        count = 1
        for row in self.file.iter_rows(min_col=4, max_row=find_row[0], min_row=find_row[0]):
            for cell in row:
                result[count] = cell.value
                count += 1
        return result
    def dop_smens(self):
       pass


# test  =  Editsmens()
# test.smens('Январь','Кирилл')