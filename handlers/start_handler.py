from aiogram import Bot, types, Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType
from aiogram.filters import StateFilter
    
import logging
from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests, user_requests


config: Config = load_config()
router = Router()
admin_ids = str(config.tg_bot.admin_ids).split(',')


def extract_arg(arg):
    return arg.split()[1:]


class FsmStart(StatesGroup):
    get_name = State()
    get_car_description = State()


@router.message(Command('start'), F.chat.type.in_({ChatType.PRIVATE}))
async def start(message: types.Message, state: FSMContext):
    """
    Старт
    :param message:
    :param state:
    :return:
    """
    logging.info('start')
    await state.clear()
    user_id = str(message.from_user.id)
    command = extract_arg(message.text)
    if command:
        command = command[0]
        flag = command.split('_')[0]
        arg = command.split('_')[1]
        if flag == 'adm':
            new_admin_check = await user_requests.add_new_admin(int(user_id), int(arg))
            if new_admin_check:
                markup = await admin_keyboard.main_admin_buttons()
                await message.answer('Вы были добавлены администратором, выберите действие 👇', reply_markup=markup)
            else:
                await message.answer('По этой ссылке уже зарегистрирован администратор ❌')
    else:
        db_admins = await user_requests.get_db_admins()
        if user_id in admin_ids or int(user_id) in db_admins:
            markup = await admin_keyboard.main_admin_buttons()
            await message.answer('Вы являетесь администратором, выберите действие 👇', reply_markup=markup)
        else:
            driver_status = await user_requests.check_driver_in_db(int(user_id))
            if driver_status == 'dont_moderation':
                await message.answer('Ваша заявка на рассмотрении, в скором времени вы сможете начать работу 🚕')
            if driver_status == 'banned':
                await message.answer('Вы были заблокированы администратором ❌')
            if driver_status == 'good_driver':
                driver_data = await user_requests.get_driver_data(int(user_id))
                markup = await user_keyboard.main_driver_buttons(driver_data['on_the_line'])
                await message.answer('Приветствуем вас в боте ...', reply_markup=markup)
            if driver_status == 'not_in_db':
                await state.set_state(FsmStart.get_name)
                await message.answer('Добро пожаловать в бота ...\n\n'
                                     'Введите ваше имя 👇')


@router.message(StateFilter(FsmStart.get_name))
async def get_driver_name(message: types.Message, state: FSMContext):
    """Получение имени водителя"""
    logging.info('get_driver_name')
    driver_name = str(message.text)
    markup = await user_keyboard.back_button('back-to-reg-driver_name')
    await state.update_data(driver_name=driver_name)
    await state.set_state(FsmStart.get_car_description)
    await message.answer('Введите описание вашего автомобиля 🚕\n\n'
                         'Например: Синяя веста 122', reply_markup=markup)


@router.message(StateFilter(FsmStart.get_car_description))
async def get_car_description(message: types.Message, state: FSMContext):
    """Получение описания автомобиля"""
    logging.info('get_car_description')
    car_description = str(message.text)
    user_id = int(message.from_user.id)
    username = str(message.from_user.username)

    markup = await user_keyboard.confirm_data_buttons()
    state_data = await state.get_data()

    await state.update_data(car_description=car_description)
    await state.update_data(username=username)
    await state.update_data(user_id=user_id)

    await message.answer(f'Проверьте правильность введенных данных 👇\n\n'
                         f'👤 Имя: {state_data["driver_name"]}\n'
                         f'🚕 Описание машины: {car_description}', reply_markup=markup)


@router.callback_query(F.data.startswith('back-to-reg-driver_'))
async def back_register(callback: types.CallbackQuery, state: FSMContext):
    """Обработка кнопок назад"""
    logging.info('back_register')
    flag = str(callback.data).split('_')[1]
    if flag == 'name':
        await state.set_state(FsmStart.get_name)
        await callback.message.edit_text('Добро пожаловать в бота ...\n\n'
                                         'Введите ваше имя 👇')
    else:
        markup = await user_keyboard.back_button('back-to-reg-driver_name')
        await state.set_state(FsmStart.get_car_description)
        await callback.message.edit_text('Введите описание вашего автомобиля 🚕\n\n'
                         'Например: Синяя веста 122', reply_markup=markup)


@router.callback_query(F.data == 'end-register')
async def end_of_register(callback: types.CallbackQuery, state: FSMContext):
    """Окончание регистрации"""
    logging.info('end_of_register')
    state_data = await state.get_data()
    await user_requests.insert_driver_data(state_data)
    await state.set_state(default_state)
    await callback.message.edit_text('Благодарим вас за регистрацию ✅\n\n'
                                     'После одобрения заявки модератором, вам придет сообщение')

















