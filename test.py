import pandas as pd
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

# Укажите свои учетные данные и URL OneDrive
username = 'kira.foka99@gmail.com'
password = 'HfW-2iL-2yn-97W'
file_url = 'https://yourtenant-my.sharepoint.com/personal/your_user/Documents/your_file.xlsx'

# Аутентификация
credentials = UserCredential(username, password)
ctx = ClientContext(file_url).with_credentials(credentials)

# Загрузка файла
response = ctx.web.get_file_by_server_relative_url(file_url).download('local_file.xlsx').execute_query()

# Чтение и изменение файла
df = pd.read_excel('local_file.xlsx')
# Здесь вы можете внести изменения в DataFrame df
df['new_column'] = df['existing_column'] * 2  # Пример изменения

# Сохранение изменений
df.to_excel('local_file.xlsx', index=False)

# Загрузка измененного файла обратно в OneDrive
with open('local_file.xlsx', 'rb') as file:
    ctx.web.get_file_by_server_relative_url(file_url).upload(file).execute_query()
