import json
import os
import logging
import sys
from datetime import datetime

from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from config import ConfigInfo

LOG_NAME = 'read_history.log'

config = ConfigInfo()
logging.basicConfig(filename=LOG_NAME, encoding='utf-8', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
client = TelegramClient(config.telegram.username, config.telegram.api_id, config.telegram.api_hash)

def get_path(suffix):
    dir = os.path.join(os.getcwd(), 'history', config.telegram.channel_name )
    if not os.path.exists(dir):
        os.mkdir(dir)
    return os.path.join(dir, f'{config.telegram.channel_name}_{suffix}.json') 

async def dump_all_users(channel):
    """Writes a json file with information about channel/chat users"""    
    offset_user = config.telegramUsers.offset_user
    limit_user = config.telegramUsers.limit_user
    filter_user = ChannelParticipantsSearch('')

    while True:
        try:
            participants = await client(GetParticipantsRequest(channel,
                filter_user, offset_user, limit_user, hash=0))
        except:
            logging.warning(f'Error reading users: {sys.exc_info()}')
            return
        if not participants.users:
            break
        all_users_details = []
        for participant in participants.users:
            all_users_details.append({  "id": participant.id,
                                        "first_name": participant.first_name,
                                        "last_name": participant.last_name,
                                        "user": participant.username,
                                        "phone": participant.phone,
                                        "is_bot": participant.bot})    
        if all_users_details:
            save_file('users', all_users_details)

        offset_user += len(participants.users)
    config.set_offset_user(offset_user)
    

async def dump_all_messages(channel):
    """Writes a json file with information about channel/chat messages"""    
    offset_msg = config.telegramMessages.offset_msg
    limit_msg = config.telegramMessages.limit_msg
    total_count_limit = config.telegramMessages.offset_msg
    total_messages = 0
    all_messages = []

    while True:
        all_messages = []
        try:
            messages = await client.get_messages(
                entity=channel,
                offset_id=offset_msg,
                offset_date=None, add_offset=0, #offset_date=date(2021, 7, 6)
                limit=limit_msg, max_id=0, min_id=0,
                reverse = True)
        except:
            logging.warning(f'Error reading messages: {sys.exc_info()}')
            return
        if not messages:
            break
        for message in messages:
            mes = message.to_dict()
            if mes['_'] == "Message":
                all_messages.append(mes)
        if all_messages:
            save_file('messages', all_messages)
        offset_msg = messages[-1].id
        total_messages = len(messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
    
    config.set_offset_msg(offset_msg)

def save_file(suffix, _list):
    class DateTimeEncoder(json.JSONEncoder):
        """Class for serializing date records to JSON"""
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    fname = get_path(suffix)
    if os.path.isfile(fname):
    # File exists
        with open(fname, 'ab+') as outfile:
            outfile.seek(-1, os.SEEK_END)
            outfile.truncate()
            outfile.write(','.encode())
            outfile.write(json.dumps(_list, ensure_ascii=False, cls=DateTimeEncoder)[1:-1].encode())
            outfile.write(']'.encode())
    else:
        # Create file
        with open(fname, 'wb') as outfile:
            outfile.write(json.dumps(_list, ensure_ascii=False, cls=DateTimeEncoder).encode())

async def read_channel_history():
    try:
        channel = await client.get_entity(config.telegram.channel_name)
    except:
        logging.warning(f'Error getting channel: {sys.exc_info()}')
        return
    await dump_all_users(channel)
    await dump_all_messages(channel)


def main():
    logging.info('Started')
    client.start()
    with client:
        client.loop.run_until_complete(read_channel_history())
    logging.info('Finished')

if  __name__ == "__main__":
    main()
