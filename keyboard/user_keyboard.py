from aiogram import types


async def main_driver_buttons(on_the_line: bool):
    markup = types.ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
    if on_the_line:
        btn_line = types.KeyboardButton(text='Уйти с линии ❌')
    else:
        btn_line = types.KeyboardButton(text='Выйти на линию ✅')
    btn_lk = types.KeyboardButton(text='Личный кабинет 👤')
    markup.keyboard.append([btn_line])
    markup.keyboard.append([btn_lk])
    return markup


async def back_button(back_callback: str):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_back = types.InlineKeyboardButton(text='Назад ◀️', callback_data=back_callback)
    markup.inline_keyboard.append([btn_back])
    return markup


async def confirm_data_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_confirm = types.InlineKeyboardButton(text='Все верно', callback_data='end-register')
    btn_back = types.InlineKeyboardButton(text='Назад ◀️', callback_data='back-to-reg-driver_car')
    markup.inline_keyboard.append([btn_confirm])
    markup.inline_keyboard.append([btn_back])
    return markup


async def yes_or_no_buttons(callback_prefix: str):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_yes = types.InlineKeyboardButton(text='Да', callback_data=f'{callback_prefix}_yes')
    btn_no= types.InlineKeyboardButton(text='Нет', callback_data=f'{callback_prefix}_no')
    markup.inline_keyboard.append([btn_yes, btn_no])
    return markup


async def lk_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_name = types.InlineKeyboardButton(text='Имя', callback_data='change-driver-name')
    btn_car = types.InlineKeyboardButton(text='Автомобиль', callback_data='change-driver-car')
    markup.inline_keyboard.append([btn_name, btn_car])
    return markup


async def confirm_or_delete_application(appl_id: int):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_confirm = types.InlineKeyboardButton(text='Принять ✅', callback_data=f'confirm-application_{appl_id}')
    btn_delete = types.InlineKeyboardButton(text='Отмена ❌', callback_data=f'delete-message_{appl_id}')
    markup.inline_keyboard.append([btn_confirm, btn_delete])
    return markup


async def confirm_or_not_application_user(application_id: int):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_confirm = types.InlineKeyboardButton(text='Принять ✅', callback_data=f'confirm-application-user_{application_id}_yes')
    btn_delete = types.InlineKeyboardButton(text='Отмена ❌', callback_data=f'confirm-application-user_{application_id}_no')
    markup.inline_keyboard.append([btn_confirm, btn_delete])
    return markup


async def application_buttons(with_passenger: bool, time: str, application_id: int):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    time_dict = {
        '1-3': '1-3',
        '5-7': '5-7',
        '10-15': '10-15',
        '15-30': '15-30',
        '30-60': '30-60',
        'Заберу': 'Заберу'
    }
    time_dict[time] += ' ✅'
    btn_1 = types.InlineKeyboardButton(text=time_dict['1-3'], callback_data=f'select-time_1-3_{application_id}')
    btn_2 = types.InlineKeyboardButton(text=time_dict['5-7'], callback_data=f'select-time_5-7_{application_id}')
    btn_3 = types.InlineKeyboardButton(text=time_dict['10-15'], callback_data=f'select-time_10-15_{application_id}')
    btn_4 = types.InlineKeyboardButton(text=time_dict['15-30'], callback_data=f'select-time_15-30_{application_id}')
    btn_5 = types.InlineKeyboardButton(text=time_dict['30-60'], callback_data=f'select-time_30-60_{application_id}')
    btn_6 = types.InlineKeyboardButton(text=time_dict['Заберу'], callback_data=f'select-time_Заберу_{application_id}')

    if with_passenger:
        btn_passenger = types.InlineKeyboardButton(text='С пассажиром ✅', callback_data=f'select-passenger_0_{application_id}')
    else:
        btn_passenger = types.InlineKeyboardButton(text='С пассажиром ❌', callback_data=f'select-passenger_1_{application_id}')

    btn_send = types.InlineKeyboardButton(text='Отправить ответ', callback_data=f'send-answer_{application_id}')
    btn_back = types.InlineKeyboardButton(text='Назад ◀️', callback_data=f'confirm-delete-appl_{application_id}_no')

    markup.inline_keyboard.append([btn_1, btn_2, btn_3])
    markup.inline_keyboard.append([btn_4, btn_5])
    markup.inline_keyboard.append([btn_6])
    markup.inline_keyboard.append([btn_passenger])
    markup.inline_keyboard.append([btn_send])
    markup.inline_keyboard.append([btn_back])
    return markup




















