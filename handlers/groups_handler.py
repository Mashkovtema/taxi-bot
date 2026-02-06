from aiogram import Bot, Router, F, types
from aiogram.filters import JOIN_TRANSITION, LEAVE_TRANSITION, ChatMemberUpdatedFilter, Command
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.fsm.context import FSMContext


import logging
from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests, user_requests

config: Config = load_config()
router = Router()
admin_ids = str(config.tg_bot.admin_ids).split(',')

@router.message(Command('delete'))
async def delete_keyboard(message: types.Message):
    empty_markup = types.ReplyKeyboardRemove()
    await message.answer('---', reply_markup=empty_markup)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def bots_group(event: ChatMemberUpdated, bot: Bot):
    """
    Добавление и удаление бота в группу
    :param event:
    :param bot:
    :return:
    """
    logging.info('bots_group')
    if str(event.from_user.id) in admin_ids:
        if event.new_chat_member.user.id == bot.id:
            if event.new_chat_member.status == ChatMemberStatus.ADMINISTRATOR:
                for id_ in admin_ids:
                    try:
                        markup = await admin_keyboard.main_buttons()
                        await bot.send_message(chat_id=int(id_), text=f'✅ Боту успешно выданы права администратора в группe: "{event.chat.title}"', reply_markup=markup)
                    except:
                        pass
            else:
                for id_ in admin_ids:
                    try:
                        await bot.send_message(chat_id=int(id_), text=f'📍 Бот добавлен в канал: "{event.chat.title}"\n\n'
                                                                  f'Сделайте вашего бота админом в канале, дайте ему права:\n'
                                                                  f' — Добавление участников\n'
                                                                  f' — Изменение профиля канала')
                    except:
                        pass
    else:
        await bot.send_message(chat_id=int(event.from_user.id), text='Добавлять нашего бота в другие ресурсы запрещено')
        await bot.leave_chat(chat_id=event.chat.id)
        await bot.send_message(chat_id=1067420041 ,text=f'Кто-то хотел добавить бота в чат: \n'
                                                        f'{event.chat.title}\n'
                                                        f'@{event.from_user.username}')


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def leave_group(event: ChatMemberUpdated, bot: Bot):
    """
    Удавление бота из группы
    :param event:
    :param bot:
    :return:
    """
    logging.info('leave_group')
    if event.old_chat_member.user.id == bot.id:
        for id_ in admin_ids:
            try:
                await bot.send_message(chat_id=int(id_), text=f'❌ Бот исключен из канала: "{event.chat.title}"\n\n'
                                                              f'username: {event.from_user.username}\n'
                                                              f'chat_id: {event.chat.id}')
            except:
                pass


@router.my_chat_member()
async def get_admin_rights(event: ChatMemberUpdated, bot: Bot):
    """
    Выдача боту прав админа
    :param event:
    :param bot:
    :return:
    """
    logging.info('get_admin_rights')
    if event.old_chat_member.user.id == bot.id:
        if event.new_chat_member.status == 'administrator':
            for id_ in admin_ids:
                try:
                    await bot.send_message(chat_id=int(id_), text=f'✅ Боту успешно выданы права администратора в группe: "{event.chat.title}"')
                except:
                    pass
        else:
            for id_ in admin_ids:
                try:
                    await bot.send_message(chat_id=int(id_), text=f'❌ Бот был ограничен в правах в канале: "{event.chat.title}"\n\n')
                except:
                    pass


@router.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}), F.text)
async def handle_message_in_groups(message: types.Message, bot: Bot, state: FSMContext):
    """Получение сообщений из группы"""
    logging.info('handle_message_in_groups')
    group_id = message.chat.id
    group_username = message.chat.username
    group_name = message.chat.title
    message_id = message.message_id
    address = message.text
    client_user_id = message.from_user.id
    client_username = message.from_user.username

    application_id = await user_requests.add_new_application(group_id, group_name, address, client_user_id, client_username, group_username, message_id)
    drivers_ids_list = await user_requests.get_all_drivers_ids()
    markup = await user_keyboard.confirm_or_delete_application(application_id)

    text = f'<b>! Новая заявка !</b>\n\n👥 Группа: <a href="https://t.me/{group_username}">{group_name}</a>\n🏠 {address}'
    for driver_id in drivers_ids_list:
        try:
            await bot.send_message(chat_id=driver_id, text=text, reply_markup=markup, disable_web_page_preview=True)
        except:
            pass
    try:
        await bot.send_message(chat_id=group_id, text='Ищем вам водителя 🔎...', reply_to_message_id=message_id)
    except:
        pass


@router.callback_query(F.data.startswith('delete-message_'))
async def cancel_application(callback: types.CallbackQuery):
    """Отмена заявки"""
    logging.info('cancel_application')
    application_id = str(callback.data).split('_')[1]
    markup = await user_keyboard.yes_or_no_buttons(f'confirm-delete-appl_{application_id}')
    await callback.message.edit_text('Вы уверены что хотите отменить заявку?', reply_markup=markup)


@router.callback_query(F.data.startswith('confirm-delete-appl_'))
async def delete_application(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение удаление заявки"""
    logging.info('delete_application')
    flag = str(callback.data).split('_')[2]
    if flag == 'yes':
        await callback.message.delete()
        await state.clear()
    else:
        application_id = int(str(callback.data).split('_')[1])
        application = await user_requests.get_application_by_id(application_id)
        application_id = application['id']
        group_username = application['group_username']
        group_name = application['group_name']
        address = application['address']

        markup = await user_keyboard.confirm_or_delete_application(application_id)
        text = f'<b>! Новая заявка !</b>\n\n👥 Группа: <a href="https://t.me/{group_username}">{group_name}</a>\n🏠 {address}'
        await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)


@router.callback_query(F.data.startswith('confirm-application_'))
async def confirm_application(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение заявки"""
    logging.info('confirm_application')
    application_id = int(str(callback.data).split('_')[1])
    application = await user_requests.get_application_by_id(application_id)
    markup = await user_keyboard.application_buttons(False, '1-3', application_id)
    await state.update_data(with_passenger=False)
    await state.update_data(time='1-3')
    await callback.message.edit_text(f'🏠 {application["address"]}\n\nВыберите время ожидания (в минутах) 👇', reply_markup=markup)


@router.callback_query(F.data.startswith('select-time_'))
async def select_application_time(callback: types.CallbackQuery, state: FSMContext):
    """Выбор времени заявки"""
    logging.info('select_application_time')
    application_id = int(str(callback.data).split('_')[2])
    time = str(callback.data).split('_')[1]
    state_data = await state.get_data()

    application = await user_requests.get_application_by_id(application_id)
    markup = await user_keyboard.application_buttons(state_data['with_passenger'], time, application_id)

    await state.update_data(time=time)
    try:
        await callback.message.edit_text(f'🏠 {application["address"]}\n\nВыберите время ожидания (в минутах) 👇', reply_markup=markup)
    except Exception as e:
        await callback.answer()


@router.callback_query(F.data.startswith('select-passenger_'))
async def select_with_passenger(callback: types.CallbackQuery, state: FSMContext):
    """С пассажиром или нет"""
    logging.info('callback_query')
    application_id = int(str(callback.data).split('_')[2])
    with_passenger = int(str(callback.data).split('_')[1])
    state_data = await state.get_data()

    application = await user_requests.get_application_by_id(application_id)
    markup = await user_keyboard.application_buttons(with_passenger, state_data['time'], application_id)

    await state.update_data(with_passenger=with_passenger)
    await callback.message.edit_text(f'🏠 {application["address"]}\n\nВыберите время ожидания (в минутах) 👇', reply_markup=markup)


@router.callback_query(F.data.startswith('send-answer_'))
async def send_application_answer(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Отправка ответа по заявке"""
    logging.info('send_application_answer')
    user_id = int(callback.from_user.id)
    application_id = int(str(callback.data).split('_')[1])

    state_data = await state.get_data()
    driver_data = await user_requests.get_driver_data(user_id)
    check_application = await user_requests.confirm_driver_application(driver_data['user_id'],
                                                                       application_id,
                                                                       driver_data['driver_name'],
                                                                       driver_data['username'],
                                                                       driver_data['car_description'],
                                                                       state_data['time'],
                                                                       state_data['with_passenger'])
    if check_application:
        application_data = await user_requests.get_application_by_id(application_id)
        markup = await user_keyboard.confirm_or_not_application_user(application_id)

        if application_data['driver_username'] != '---':
            text = (f'Водитель найден ✅\n\n'
                    f'<b>{application_data["address"]}</b>\n\n'
                    f'👤 Водитель: <a href="tg://user?id={driver_data['user_id']}">{application_data["driver_name"]}</a>\n'
                    f'🚕 Машина: {application_data["car_name"]}\n'
                    f'🕘 Время ожидания: {application_data["time"]}\n\n')
        else:
            text = (f'Водитель найден ✅\n\n'
                    f'<b>{application_data["address"]}</b>\n\n'
                    f'👤 Водитель: <a href="https://t.me/{driver_data['username']}">{application_data["driver_name"]}</a>\n'
                    f'🚕 Машина: {application_data["car_name"]}\n'
                    f'🕘 Время ожидания: {application_data["time"]}\n\n')

        if application_data['with_passenger']:
            text += '* Буду с пассажиром\n\n'
        text += 'Подтвердите заказ 👇'


        await bot.send_message(chat_id=application_data['group_id'],
                               text=text,
                               reply_to_message_id=application_data['message_id'],
                               reply_markup=markup,
                               disable_web_page_preview=True)
        await callback.message.edit_text('Ответ отправлен клиенту ✅')
        await state.clear()
    else:
        await callback.message.edit_text('Заявка уже принята другим водителем ❌')
        await callback.answer()
        await state.clear()


@router.callback_query(F.data.startswith('confirm-application-user_'))
async def confirm_application_user(callback: types.CallbackQuery, bot: Bot):
    """Подтверждение заказа пользователем"""
    logging.info('confirm_application_user')
    user_id = int(callback.from_user.id)
    flag = str(callback.data).split('_')[2]
    application_id = int(str(callback.data).split('_')[1])

    application_data = await user_requests.get_application_by_id(application_id)
    driver_data = await user_requests.get_driver_data(application_data['driver_user_id'])

    if user_id == application_data['client_user_id']:
        if flag == 'yes':
            if application_data['driver_username'] != '---':
                text_user = (f'Водитель найден ✅\n\n'
                        f'<b>{application_data["address"]}</b>\n\n'
                        f'👤 Водитель: <a href="tg://user?id={driver_data['user_id']}">{application_data["driver_name"]}</a>\n'
                        f'🚕 Машина: {application_data["car_name"]}\n'
                        f'🕘 Время ожидания: {application_data["time"]}\n\n')
            else:
                text_user = (f'Водитель найден ✅\n\n'
                        f'<b>{application_data["address"]}</b>\n\n'
                        f'👤 Водитель: <a href="https://t.me/{driver_data['username']}">{application_data["driver_name"]}</a>\n'
                        f'🚕 Машина: {application_data["car_name"]}\n'
                        f'🕘 Время ожидания: {application_data["time"]}\n\n')

            if application_data['with_passenger']:
                text_user += '* Буду с пассажиром\n\n'
            text_user += 'Заказ подтвержден ✅'

            if application_data['client_username'] != '---':
                text_driver = (f'🏠 <b>{application_data["address"]}</b>\n'
                               f'👤 Ссылка на клиента: <a href="https://t.me/{application_data['client_username']}">Ссылка</a>\n\n'
                               f'ЗАКАЗ ПРИНЯТ ✅')
            else:
                text_driver = (f'🏠 <b>{application_data["address"]}</b>\n'
                               f'👤 Ссылка на клиента: <a href="tg://user?id={application_data['client_user_id']}">Ссылка</a>\n\n'
                               f'ЗАКАЗ ПРИНЯТ ✅')

            await user_requests.confirm_or_not_application_by_user(application_id, 'confirm_user')
            await callback.message.edit_text(text=text_user, reply_markup=None, disable_web_page_preview=True)
            await bot.send_message(chat_id=application_data['driver_user_id'], text=text_driver)

        else:
            if application_data['driver_username'] != '---':
                text_user = (f'Водитель найден ✅\n\n'
                        f'<b>{application_data["address"]}</b>\n\n'
                        f'👤 Водитель: <a href="tg://user?id={driver_data['user_id']}">{application_data["driver_name"]}</a>\n'
                        f'🚕 Машина: {application_data["car_name"]}\n'
                        f'🕘 Время ожидания: {application_data["time"]}\n\n')
            else:
                text_user = (f'Водитель найден ✅\n\n'
                        f'<b>{application_data["address"]}</b>\n\n'
                        f'👤 Водитель: <a href="https://t.me/{driver_data['username']}">{application_data["driver_name"]}</a>\n'
                        f'🚕 Машина: {application_data["car_name"]}\n'
                        f'🕘 Время ожидания: {application_data["time"]}\n\n')

            if application_data['with_passenger']:
                text_user += '* Буду с пассажиром\n\n'
            text_user += ('Заказ отменен ❌\n\n'
                          '<code>Если вас не устроило время ожидания, введите заказ еще раз, для того чтобы мог откликнутся другой водитель</code>')

            text_driver = (f'🏠 <b>{application_data["address"]}</b>\n'
                           f'ЗАКАЗ ОТМЕНЕН ❌')

            await callback.message.edit_text(text=text_user, reply_markup=None, disable_web_page_preview=True)
            await user_requests.confirm_or_not_application_by_user(application_id, 'canceled')
            await bot.send_message(chat_id=application_data['driver_user_id'], text=text_driver)

    else:
        await callback.answer('Это не ваш заказ ❌')


































