import configparser

CONFIG_NAME = "config.ini"
TELEGRAM = 'Telegram'
TELEGRAM_MESSAGES = 'TelegramMessages'
TELEGRAM_USERS = 'TelegramUsers'
CONFIG_DEFAULT = """
[Telegram]
api_id = your_telegram_api
api_hash = your_telegram_hash
username = your_telegram_username
channel_name = your_parser_channel

[TelegramMessages]
#the number of the record to start reading from
offset_msg = 0
# maximum number of records transferred at one time
limit_msg = 1000
# change this value if you don't need all messages
total_count_limit = 0

[TelegramUsers]
#the number of the record to start reading from
offset_user = 0
# maximum number of records transferred at one time
limit_user = 100
""" 

class ConfigInfo():
    def __init__(self) -> None:
        # Считываем учетные данные
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_NAME)
        if not self.config.sections():
            self.config.read_string(CONFIG_DEFAULT)
            self.save_config()
        # Присваиваем значения внутренним переменным
        self.telegram = ConfigTelegram(self.config)
        self.telegramMessages = ConfigTelegramMessages(self.config)
        self.telegramUsers = ConfigTelegramUsers(self.config)

    def save_config(self):
        with open(CONFIG_NAME, 'w') as configfile:
            self.config.write(configfile)

    def set_offset_msg(self, offset_msg):
        self.config.set(section=TELEGRAM_MESSAGES,option='offset_msg',value=str(offset_msg))
        self.save_config()
    
    def set_offset_user(self, offset_user):
        self.config.set(section=TELEGRAM_USERS,option='offset_user',value=str(offset_user))
        self.save_config()   


class ConfigTelegram():
    def __init__(self, config):
        self.api_id   = config[TELEGRAM]['api_id']
        self.api_hash = config[TELEGRAM]['api_hash']
        self.username = config[TELEGRAM]['username']
        self.channel_name = config[TELEGRAM]['channel_name']


class ConfigTelegramMessages():
    def __init__(self, config):
        self.offset_msg        = config.getint(TELEGRAM_MESSAGES,'offset_msg')# номер записи, с которой начинается считывание
        self.limit_msg         = config.getint(TELEGRAM_MESSAGES,'limit_msg')  # максимальное число записей, передаваемых за один раз
        self.total_count_limit = config.getint(TELEGRAM_MESSAGES,'total_count_limit')# поменяйте это значение, если вам нужны не все сообщения


class ConfigTelegramUsers():
    def __init__(self, config):
        self.offset_user = config.getint(TELEGRAM_USERS,'offset_user')# номер участника, с которого начинается считывание
        self.limit_user  = config.getint(TELEGRAM_USERS,'limit_user')# максимальное число записей, передаваемых за один раз
 

if  __name__ == "__main__":
    config = ConfigInfo()
