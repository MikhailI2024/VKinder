from vk_api.longpoll import VkEventType

from database import creating_database
from keyboard import sender
from main import bot
from settings import LINE

creating_database()

for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        msg = event.text.lower()
        sender(user_id, msg.lower())
        if request == 'начать поиск':
            bot.write_msg(user_id, f'Привет, {bot.get_name(user_id)}, найдём тебе пару?')
            bot.find_pair(user_id)
            shift = 0
            message = 'Нажмите кнопку "Далее", для начала поиска.'
            bot.write_msg(user_id, message)
        elif request == 'далее':
            shift += 1
            if shift >= len(LINE):
                bot.write_msg(user_id, 'Список кандидатов исчерпан.')
            else:
                bot.find_persons(user_id, shift)
        else:
            bot.write_msg(user_id, 'Я не понимаю, напишите другую команду.')
