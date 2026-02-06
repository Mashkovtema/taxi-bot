from aiogram import Bot, types, Router, F
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ChatType
import logging

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests
from filters.admin_filter import IsSuperAdmin

config: Config = load_config()
router = Router()
router.message.filter(IsSuperAdmin())

class FsmModeration(StatesGroup):
    get_cancel_reason = State()
    get_ban_reason = State()


@router.message(F.text == 'Водители 🚕', F.chat.type.in_({ChatType.PRIVATE}))
async def main_drivers(message: types.Message, state: FSMContext):
    """Раздел с водителями"""
    logging.info('main_drivers')
    markup = await admin_keyboard.main_drivers_buttons()
    await state.clear()
    await state.set_state(default_state)
    await message.answer('Выберите действие 👇', reply_markup=markup)


@router.callback_query(F.data == 'back-to-main-drivers')
async def back_to_drivers(callback: types.CallbackQuery):
    """Назад в меню"""
    logging.info('back-to-drivers')
    markup = await admin_keyboard.main_drivers_buttons()
    await callback.message.edit_text('Выберите действие 👇', reply_markup=markup)


# -------------------- Модерация водителей --------------------------------

@router.callback_query(F.data == 'drivers-moderation')
async def moderation_drivers(callback: types.CallbackQuery, state: FSMContext):
    """Модерация водителей"""
    logging.info('moderation_drivers')
    drivers = await admin_requests.get_drivers_to_moderate()
    await state.update_data(page=0)
    if drivers:
        markup = await admin_keyboard.drivers_pagination(
            'select-driver-moder',
            'pagination-driver-moder',
            drivers,
            0
        )
        await callback.message.edit_text('Выберите водителя для модерации 👇', reply_markup=markup)
    else:
        markup = await admin_keyboard.back_buttons('back-to-main-drivers')
        await callback.message.edit_text('Заявок на модерацию еще не поступало ❌', reply_markup=markup)


@router.callback_query(F.data.startswith('pagination-driver-moder_'))
async def pagination_moderation(callback: types.CallbackQuery, state: FSMContext):
    """Пагинация модерации"""
    logging.info('pagination_moderation')
    page = int(str(callback.data).split('_')[1])
    drivers = await admin_requests.get_drivers_to_moderate()
    markup = await admin_keyboard.drivers_pagination(
        'select-driver-moder',
        'pagination-driver-moder',
        drivers,
        page
    )
    await state.update_data(page=page)
    if markup:
        await callback.message.edit_text('Выберите водителя для модерации 👇', reply_markup=markup)
    else:
        await callback.answer()


@router.callback_query(F.data.startswith('select-driver-moder_'))
async def select_driver_to_moderation(callback: types.CallbackQuery, state: FSMContext):
    """Выбор водителя для модерации"""
    logging.info('select_driver_to_moderation')
    driver_id = int(str(callback.data).split('_')[1])
    state_data = await state.get_data()
    driver_data = await admin_requests.get_driver_data_by_id(driver_id)
    markup = await admin_keyboard.confirm_or_no_moderation(driver_data['user_id'], state_data['page'])

    if driver_data['username'] != 'None':
        text = ('Информация о водителе 👤\n\n'
                f'Имя: {driver_data["driver_name"]}\n'
                f'Автомобиль: {driver_data["car_description"]}\n'
                f'<a href="https://t.me/{driver_data['username']}">Ссылка на водителя</a>')
    else:
        text = ('Информация о водителе 👤\n\n'
                f'Имя: {driver_data["driver_name"]}\n'
                f'Автомобиль: {driver_data["car_description"]}\n'
                f'<a href="tg://user?id={driver_data['user_id']}">Ссылка на водителя</a>')

    await state.set_state(default_state)
    await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)


@router.callback_query(F.data.startswith('confirm-moderation_'))
async def confirm_moderation(callback: types.CallbackQuery, bot: Bot):
    """Подтверждение модерации"""
    logging.info('confirm_moderation')
    driver_user_id = int(str(callback.data).split('_')[1])
    text = ('Ваш аккаунт успешно прошел модерацию ⭐️\n\n'
            'Нажмите на кнопку "Выйти на линию ✅" чтобы начать принимать заказы')
    markup = await user_keyboard.main_driver_buttons(False)
    admin_markup = await admin_keyboard.back_buttons('drivers-moderation')

    await admin_requests.confirm_moderation_driver(driver_user_id)
    try:
        await bot.send_message(chat_id=driver_user_id, text=text, reply_markup=markup)
    except:
        pass
    await callback.message.edit_text('Водителю отправлено ответное письмо ✅', reply_markup=admin_markup)


@router.callback_query(F.data.startswith('cancel-moderation_'))
async def cancel_moderation(callback: types.CallbackQuery, state: FSMContext):
    """Отклонение модерации"""
    logging.info('cancel_moderation')
    driver_user_id = int(str(callback.data).split('_')[1])

    driver_data = await admin_requests.get_driver_data_by_user_id(driver_user_id)
    markup = await admin_keyboard.back_buttons(f'select-driver-moder_{driver_data["id"]}')

    if driver_data['username'] != 'None':
        text = ('Информация о водителе 👤\n\n'
                f'Имя: {driver_data["driver_name"]}\n'
                f'Автомобиль: {driver_data["car_description"]}\n'
                f'<a href="https://t.me/{driver_data['username']}">Ссылка на водителя</a>\n\n'
                f'Введите причину отказа в модерации 👇')
    else:
        text = ('Информация о водителе 👤\n\n'
                f'Имя: {driver_data["driver_name"]}\n'
                f'Автомобиль: {driver_data["car_description"]}\n'
                f'<a href="tg://user?id={driver_data['user_id']}">Ссылка на водителя</a>\n\n'
                f'Введите причину отказа в модерации 👇')

    await state.set_state(FsmModeration.get_cancel_reason)
    await state.update_data(driver_user_id=driver_user_id)
    await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)


@router.message(StateFilter(FsmModeration.get_cancel_reason))
async def get_cancel_reason(message: types.Message, state: FSMContext):
    """Получение причины отказа в модерации"""
    logging.info('get_cancel_reason')
    cancel_reason = str(message.text)
    await state.update_data(cancel_reason=cancel_reason)
    markup = await admin_keyboard.yes_or_no_buttons('confirm-or-no-moderation')
    await message.answer(f'❌ Вы уверены что хотите отказать в модерации по причине: \n'
                         f'"{cancel_reason}"', reply_markup=markup)


@router.callback_query(F.data.startswith('confirm-or-no-moderation_'))
async def confirm_or_no(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Отправить отказ или нет"""
    logging.info('confirm_or_no')
    flag = str(callback.data).split('_')[1]
    if flag == 'yes':
        state_data = await state.get_data()
        admin_markup = await admin_keyboard.back_buttons('drivers-moderation')

        text = (f'Ваш аккаунт не  прошел модерацию ❌\n\n'
                f'Причина: "{state_data['cancel_reason']}"')

        await admin_requests.delete_driver(state_data['driver_user_id'])
        try:
            await bot.send_message(chat_id=state_data['driver_user_id'], text=text)
        except:
            pass

        await state.set_state(default_state)
        await callback.message.edit_text('Водителю отправлено ответное письмо ✅', reply_markup=admin_markup)

    else:
        state_data = await state.get_data()
        driver_data = await admin_requests.get_driver_data_by_user_id(state_data['driver_user_id'])
        markup = await admin_keyboard.back_buttons(f'select-driver-moder_{driver_data["id"]}')

        if driver_data['username'] != 'None':
            text = ('Информация о водителе 👤\n\n'
                    f'Имя: {driver_data["driver_name"]}\n'
                    f'Автомобиль: {driver_data["car_description"]}\n'
                    f'<a href="https://t.me/{driver_data['username']}">Ссылка на водителя</a>\n\n'
                    f'Введите причину отказа в модерации 👇')
        else:
            text = ('Информация о водителе 👤\n\n'
                    f'Имя: {driver_data["driver_name"]}\n'
                    f'Автомобиль: {driver_data["car_description"]}\n'
                    f'<a href="tg://user?id={driver_data['user_id']}">Ссылка на водителя</a>\n\n'
                    f'Введите причину отказа в модерации 👇')

        await state.set_state(FsmModeration.get_cancel_reason)
        await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)


# ---------------- Бан водителей -------------------------------


@router.callback_query(F.data == 'ban-drivers')
async def ban_drivers(callback: types.CallbackQuery, state: FSMContext):
    """Бан водителей"""
    logging.info('ban_drivers')
    drivers = await admin_requests.get_drivers_to_ban()
    await state.update_data(page=0)
    if drivers:
        markup = await admin_keyboard.drivers_pagination(
            'select-driver-ban',
            'pagination-driver-ban',
            drivers,
            0
        )
        await callback.message.edit_text('Выберите водителя, которого хотите забанить 👇', reply_markup=markup)
    else:
        markup = await admin_keyboard.back_buttons('back-to-main-drivers')
        await callback.message.edit_text('Водителей, которых можно заблокировать нет ❌', reply_markup=markup)


@router.callback_query(F.data.startswith('pagination-driver-ban_'))
async def pagination_ban_drivers(callback: types.CallbackQuery, state: FSMContext):
    """Пагинация водителей для блокировки"""
    logging.info('pagination_ban_drivers')
    page = int(str(callback.data).split('_')[1])
    drivers = await admin_requests.get_drivers_to_ban()
    markup = await admin_keyboard.drivers_pagination(
        'select-driver-ban',
        'pagination-driver-ban',
        drivers,
        page
    )
    await state.update_data(page=page)
    if markup:
        await callback.message.edit_text('Выберите водителя, которого хотите забанить 👇', reply_markup=markup)
    else:
        await callback.answer()


@router.callback_query(F.data.startswith('select-driver-ban_'))
async def select_driver_to_ban(callback: types.CallbackQuery, state: FSMContext):
    """Выбор водителя для блокировки"""
    logging.info('select_driver_to_ban')
    driver_id = int(str(callback.data).split('_')[1])
    state_data = await state.get_data()
    driver_data = await admin_requests.get_driver_data_by_id(driver_id)
    markup = await admin_keyboard.back_buttons(f'pagination-driver-ban_{state_data["page"]}')

    if driver_data['username'] != 'None':
        text = ('Информация о водителе 👤\n\n'
                f'Имя: {driver_data["driver_name"]}\n'
                f'Автомобиль: {driver_data["car_description"]}\n'
                f'<a href="https://t.me/{driver_data['username']}">Ссылка на водителя</a>\n\n'
                f'Введите причину блокировки водителя 👇')
    else:
        text = ('Информация о водителе 👤\n\n'
                f'Имя: {driver_data["driver_name"]}\n'
                f'Автомобиль: {driver_data["car_description"]}\n'
                f'<a href="tg://user?id={driver_data['user_id']}">Ссылка на водителя</a>\n\n'
                f'Введите причину блокировки водителя 👇')

    await state.set_state(FsmModeration.get_ban_reason)
    await state.update_data(driver_id=driver_id)
    await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)


@router.message(StateFilter(FsmModeration.get_ban_reason))
async def get_ban_reason(message: types.Message, state: FSMContext):
    """Получение причины блокировки водителя"""
    logging.info('get_ban_reason')
    ban_reason = str(message.text)
    state_data = await state.get_data()

    driver_id = state_data['driver_id']
    driver_data = await admin_requests.get_driver_data_by_id(driver_id)
    markup = await admin_keyboard.yes_or_no_buttons(f'confirm-ban-driver')

    if driver_data['username'] != 'None':
        text = ('Информация о водителе 👤\n\n'
                f'Имя: {driver_data["driver_name"]}\n'
                f'Автомобиль: {driver_data["car_description"]}\n'
                f'<a href="https://t.me/{driver_data['username']}">Ссылка на водителя</a>\n\n'
                f'Вы уверены что хотите заблокировать водителя по причине:\n'
                f'"{ban_reason}" ?')
    else:
        text = ('Информация о водителе 👤\n\n'
                f'Имя: {driver_data["driver_name"]}\n'
                f'Автомобиль: {driver_data["car_description"]}\n'
                f'<a href="tg://user?id={driver_data['user_id']}">Ссылка на водителя</a>\n\n'
                f'Вы уверены что хотите заблокировать водителя по причине:\n'
                f'"{ban_reason}" ?')

    await state.update_data(ban_reason=ban_reason)
    await state.set_state(default_state)
    await message.answer(text=text, reply_markup=markup, disable_web_page_preview=True)


@router.callback_query(F.data.startswith('confirm-ban-driver_'))
async def confirm_or_no_ban_driver(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Банить водителя или нет"""
    logging.info('confirm_or_no_ban_driver')
    flag = str(callback.data).split('_')[1]
    state_data = await state.get_data()

    if flag == 'yes':
        text = (f'Ваш аккаунт был заблокирован ❌\n\n'
                f'Причина: "{state_data['ban_reason']}"')
        markup = await admin_keyboard.back_buttons('ban-drivers')
        driver_data = await admin_requests.get_driver_data_by_id(state_data['driver_id'])

        await admin_requests.ban_driver(driver_data['user_id'])
        try:
            await bot.send_message(chat_id=driver_data['user_id'], text=text)
        except:
            pass
        await callback.message.edit_text('Водителю отправлено ответное письмо ✅', reply_markup=markup)
    else:
        driver_id = state_data['driver_id']
        page = state_data['page']
        driver_data = await admin_requests.get_driver_data_by_id(driver_id)
        markup = await admin_keyboard.back_buttons(f'pagination-driver-ban_{page}')

        if driver_data['username'] != 'None':
            text = ('Информация о водителе 👤\n\n'
                    f'Имя: {driver_data["driver_name"]}\n'
                    f'Автомобиль: {driver_data["car_description"]}\n'
                    f'<a href="https://t.me/{driver_data['username']}">Ссылка на водителя</a>\n\n'
                    f'Введите причину блокировки водителя 👇')
        else:
            text = ('Информация о водителе 👤\n\n'
                    f'Имя: {driver_data["driver_name"]}\n'
                    f'Автомобиль: {driver_data["car_description"]}\n'
                    f'<a href="tg://user?id={driver_data['user_id']}">Ссылка на водителя</a>\n\n'
                    f'Введите причину блокировки водителя 👇')

        await state.set_state(FsmModeration.get_ban_reason)
        await state.update_data(driver_id=driver_id)
        await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)


# ------------------ Разблокировка ------------------------------

@router.callback_query(F.data == 'unban-drivers')
async def unban_drivers(callback: types.CallbackQuery, state: FSMContext):
    """Разблокировка водителей"""
    logging.info('unban_drivers')
    drivers = await admin_requests.get_drivers_to_unban()
    await state.update_data(page=0)
    if drivers:
        markup = await admin_keyboard.drivers_pagination(
            'select-driver-unban',
            'pagination-driver-unban',
            drivers,
            0
        )
        await callback.message.edit_text('Выберите водителя, которого хотите разблокировать 👇', reply_markup=markup)
    else:
        markup = await admin_keyboard.back_buttons('back-to-main-drivers')
        await callback.message.edit_text('Водителей, которых можно разблокировать нет ❌', reply_markup=markup)


@router.callback_query(F.data.startswith('pagination-driver-unban_'))
async def pagination_unban_drivers(callback: types.CallbackQuery, state: FSMContext):
    """пагинация водителей для разблокировки"""
    logging.info('pagination_unban_drivers')
    page = int(str(callback.data).split('_')[1])
    drivers = await admin_requests.get_drivers_to_unban()
    markup = await admin_keyboard.drivers_pagination(
        'select-driver-unban',
        'pagination-driver-unban',
        drivers,
        page
    )
    await state.update_data(page=page)
    if markup:
        await callback.message.edit_text('Выберите водителя, которого хотите разблокировать 👇', reply_markup=markup)
        await callback.answer()
    else:
        await callback.answer()


@router.callback_query(F.data.startswith('select-driver-unban_'))
async def select_driver_to_unban(callback: types.CallbackQuery, state: FSMContext):
    """Выбор водителя для разблокировки"""
    logging.info('select_driver_to_unban')
    driver_id = int(str(callback.data).split('_')[1])
    driver_data = await admin_requests.get_driver_data_by_id(driver_id)
    markup = await admin_keyboard.yes_or_no_buttons('confirm-unban-driver')

    if driver_data['username'] != 'None':
        text = ('Информация о водителе 👤\n\n'
                f'Имя: {driver_data["driver_name"]}\n'
                f'Автомобиль: {driver_data["car_description"]}\n'
                f'<a href="https://t.me/{driver_data['username']}">Ссылка на водителя</a>\n\n'
                f'Вы уверены что хотите разблокировать водителя ?')
    else:
        text = ('Информация о водителе 👤\n\n'
                f'Имя: {driver_data["driver_name"]}\n'
                f'Автомобиль: {driver_data["car_description"]}\n'
                f'<a href="tg://user?id={driver_data['user_id']}">Ссылка на водителя</a>\n\n'
                f'Вы уверены что хотите разблокировать водителя ?')

    await state.update_data(driver_id=driver_id)
    await callback.message.edit_text(text=text, reply_markup=markup, disable_web_page_preview=True)


@router.callback_query(F.data.startswith('confirm-unban-driver_'))
async def confirm_unban_driver(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Уточнение разблокировки водителя"""
    logging.info('confirm_unban_driver')
    flag = str(callback.data).split('_')[1]
    state_data = await state.get_data()
    if flag == 'yes':
        driver_id = state_data['driver_id']
        driver_data = await admin_requests.get_driver_data_by_id(driver_id)
        markup_driver = await user_keyboard.main_driver_buttons(False)
        markup_admin = await admin_keyboard.back_buttons(f'pagination-driver-unban_{state_data["page"]}')

        text = ('Ваш аккаунт был разблокирован администратором ⭐️\n\n'
                'Нажмите на кнопку "Выйти на линию ✅" чтобы начать принимать заказы')

        await admin_requests.unban_driver(driver_id)
        try:
            await bot.send_message(chat_id=driver_data['user_id'], text=text, reply_markup=markup_driver)
        except:
            pass
        await callback.message.edit_text('Водителю отправлено ответное письмо ✅', reply_markup=markup_admin)
    else:
        drivers = await admin_requests.get_drivers_to_unban()
        markup = await admin_keyboard.drivers_pagination(
            'select-driver-unban',
            'pagination-driver-unban',
            drivers,
            state_data['page']
        )
        if markup:
            await callback.message.edit_text('Выберите водителя, которого хотите разблокировать 👇', reply_markup=markup)
            await callback.answer()
        else:
            await callback.answer()

















