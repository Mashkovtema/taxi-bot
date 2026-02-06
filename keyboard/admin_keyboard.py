from aiogram import types


async def main_admin_buttons():
    markup = types.ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
    btn_drivers = types.KeyboardButton(text='Водители 🚕')
    btn_admins = types.KeyboardButton(text='Администраторы 👤')
    btn_mail = types.KeyboardButton(text='Создать рассылку 📄')
    markup.keyboard.append([btn_drivers, btn_admins])
    markup.keyboard.append([btn_mail])
    return markup


async def main_drivers_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_moderation = types.InlineKeyboardButton(text='Модерация 📄', callback_data='drivers-moderation')
    btn_ban = types.InlineKeyboardButton(text='Блокировка ❌', callback_data='ban-drivers')
    btn_unban = types.InlineKeyboardButton(text='Разблокировка ✅', callback_data='unban-drivers')
    markup.inline_keyboard.append([btn_moderation])
    markup.inline_keyboard.append([btn_ban])
    markup.inline_keyboard.append([btn_unban])
    return markup


async def main_admins_menu_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_add = types.InlineKeyboardButton(text='Добавить ➕', callback_data='add-new-admin')
    btn_delete = types.InlineKeyboardButton(text='Удалить ❌', callback_data='delete-admin')
    markup.inline_keyboard.append([btn_add, btn_delete])
    return markup


async def back_buttons(back_callback: str):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_back = types.InlineKeyboardButton(text='Назад ◀️', callback_data=back_callback)
    markup.inline_keyboard.append([btn_back])
    return markup


async def drivers_pagination(select_prefix: str, pagination_prefix: str, data: list, page: int):
    item_cnt = 8  # Кол-во объектов в одном блоке

    if (page < len(data) / item_cnt) and page >= 0:  # Проверка, что страница не последняя

        if len(data) % item_cnt > 0:  # Кол-во страниц
            all_pages = int(len(data) / item_cnt) + 1
        else:
            all_pages = int(len(data) / item_cnt)

        markup = types.InlineKeyboardMarkup(inline_keyboard=[])
        if len(data) <= item_cnt:
            for obj in data:
                obj = obj.__dict__
                btn = types.InlineKeyboardButton(text=obj["driver_name"], callback_data=f'{select_prefix}_{obj["id"]}')
                markup.inline_keyboard.append([btn])
        else:
            for obj in data[item_cnt * page: (item_cnt * page) + item_cnt]:
                obj = obj.__dict__
                btn = types.InlineKeyboardButton(text=obj["driver_name"], callback_data=f'{select_prefix}_{obj["id"]}')
                markup.inline_keyboard.append([btn])

            btn_back = types.InlineKeyboardButton(text='<<<', callback_data=f'{pagination_prefix}_{page - 1}')
            btn_page = types.InlineKeyboardButton(text=f'Стр. {page + 1}/{all_pages}', callback_data=f'---')
            btn_forward = types.InlineKeyboardButton(text='>>>', callback_data=f'{pagination_prefix}_{page + 1}')
            markup.inline_keyboard.append([btn_back, btn_page, btn_forward])

        btn_back = types.InlineKeyboardButton(text='Назад ◀️', callback_data='back-to-main-drivers')
        markup.inline_keyboard.append([btn_back])

        return markup

    else:
        return None


async def admins_pagination(select_prefix: str, pagination_prefix: str, data: list, page: int):
    item_cnt = 8  # Кол-во объектов в одном блоке

    if (page < len(data) / item_cnt) and page >= 0:  # Проверка, что страница не последняя

        if len(data) % item_cnt > 0:  # Кол-во страниц
            all_pages = int(len(data) / item_cnt) + 1
        else:
            all_pages = int(len(data) / item_cnt)

        markup = types.InlineKeyboardMarkup(inline_keyboard=[])
        if len(data) <= item_cnt:
            for obj in data:
                obj = obj.__dict__
                btn = types.InlineKeyboardButton(text=obj["admin_name"], callback_data=f'{select_prefix}_{obj["id"]}')
                markup.inline_keyboard.append([btn])
        else:
            for obj in data[item_cnt * page: (item_cnt * page) + item_cnt]:
                obj = obj.__dict__
                btn = types.InlineKeyboardButton(text=obj["admin_name"], callback_data=f'{select_prefix}_{obj["id"]}')
                markup.inline_keyboard.append([btn])

            btn_back = types.InlineKeyboardButton(text='<<<', callback_data=f'{pagination_prefix}_{page - 1}')
            btn_page = types.InlineKeyboardButton(text=f'Стр. {page + 1}/{all_pages}', callback_data=f'---')
            btn_forward = types.InlineKeyboardButton(text='>>>', callback_data=f'{pagination_prefix}_{page + 1}')
            markup.inline_keyboard.append([btn_back, btn_page, btn_forward])

        btn_back = types.InlineKeyboardButton(text='Назад ◀️', callback_data='back-to-main-admins')
        markup.inline_keyboard.append([btn_back])

        return markup

    else:
        return None


async def confirm_or_no_moderation(user_id: int, page: int):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_confirm = types.InlineKeyboardButton(text='Подтвердить ✅', callback_data=f'confirm-moderation_{user_id}')
    btn_cancel = types.InlineKeyboardButton(text='Отклонить ❌', callback_data=f'cancel-moderation_{user_id}')
    btn_back = types.InlineKeyboardButton(text='Назад ◀️', callback_data=f'pagination-driver-moder_{page}')
    markup.inline_keyboard.append([btn_confirm, btn_cancel])
    markup.inline_keyboard.append([btn_back])
    return markup


async def yes_or_no_buttons(callback_prefix: str):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_yes = types.InlineKeyboardButton(text='Да', callback_data=f'{callback_prefix}_yes')
    btn_no = types.InlineKeyboardButton(text='Нет', callback_data=f'{callback_prefix}_no')
    markup.inline_keyboard.append([btn_yes, btn_no])
    return markup


async def scip_media_or_back_text():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_scip = types.InlineKeyboardButton(text='Пропустить', callback_data='scip-media')
    btn_back = types.InlineKeyboardButton(text='Назад ◀️', callback_data='back-to-newslstter_text')
    markup.inline_keyboard.append([btn_scip])
    markup.inline_keyboard.append([btn_back])
    return markup


async def next_button():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_next = types.InlineKeyboardButton(text='Далее', callback_data='next-to-watch')
    btn_back = types.InlineKeyboardButton(text='Назад ◀️', callback_data='back-to-newslstter_media')
    markup.inline_keyboard.append([btn_next])
    markup.inline_keyboard.append([btn_back])
    return markup


async def send_or_delete_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_send = types.InlineKeyboardButton(text='Отправить', callback_data='send-news-end')
    btn_back = types.InlineKeyboardButton(text='Назад ◀️', callback_data='back-to-newslstter_media')
    btn_cancel = types.InlineKeyboardButton(text='Отмена ❌', callback_data='send-news-not')
    markup.inline_keyboard.append([btn_send])
    markup.inline_keyboard.append([btn_back])
    markup.inline_keyboard.append([btn_cancel])
    return markup


async def newslater_filter():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_line = types.InlineKeyboardButton(text='На линии', callback_data='select-filter-drivers_on-line')
    btn_not_line = types.InlineKeyboardButton(text='Не на линии', callback_data='select-filter-drivers_not-on-line')
    btn_all = types.InlineKeyboardButton(text='Всем', callback_data='select-filter-drivers_all')
    markup.inline_keyboard.append([btn_line])
    markup.inline_keyboard.append([btn_not_line])
    markup.inline_keyboard.append([btn_all])
    return markup













