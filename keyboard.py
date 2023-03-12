from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from main import bot

keyboard = VkKeyboard(one_time=False)
keyboard.add_button('Начать поиск', color=VkKeyboardColor.PRIMARY)
keyboard.add_line()
keyboard.add_button('Далее', color=VkKeyboardColor.SECONDARY)

def sender(user_id, text):
    bot.vk.method('messages.send', {'user_id': user_id,
                                    'message': text,
                                    'random_id': 0,
                                    'keyboard': keyboard.get_keyboard()})
