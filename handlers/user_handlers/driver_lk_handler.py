from aiogram import Bot, types, Router, F
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ChatType
import logging

from config_data.config_data import Config, load_config
from future.standard_library import exclude_local_folder_imports
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests, user_requests

config: Config = load_config()
router = Router()


class FsmLk(StatesGroup):
    get_new_name = State()
    get_new_car = State()


@router.message(F.text == 'Личный кабинет 👤', F.chat.type.in_({ChatType.PRIVATE}))
async def driver_lk(message: types.Message, state: FSMContext):
    """Личный кабинет водителя"""
    logging.info('driver_lk')
    await state.clear()
    await state.set_state(default_state)

    user_id = int(message.from_user.id)
    driver_data = await user_requests.get_driver_data(user_id)
    if driver_data['banned']:
        await message.answer('Вы были заблокированы администратором, вам запрещено пользоваться ботом ❌')
    else:
        text = (f'Ваш личный кабинет\n\n'
                f'👤 Имя: {driver_data["driver_name"]}\n'
                f'🚕 Автомобиль: {driver_data["car_description"]}\n\n'
                f'Выберите что вы хотите изменить 👇')
        markup = await user_keyboard.lk_buttons()
        await message.answer(text=text, reply_markup=markup)


@router.callback_query(F.data == 'back-to-driver-lk')
async def back_to_lk(callback: types.CallbackQuery, state: FSMContext):
    """Назад в лк"""
    logging.info('back-to-driver-lk')
    user_id = int(callback.from_user.id)
    driver_data = await user_requests.get_driver_data(user_id)
    markup = await user_keyboard.lk_buttons()

    text = (f'Ваш личный кабинет\n\n'
            f'👤 Имя: {driver_data["driver_name"]}\n'
            f'🚕 Автомобиль: {driver_data["car_description"]}\n\n'
            f'Выберите что вы хотите изменить 👇')
    await state.set_state(default_state)
    await callback.message.edit_text(text=text, reply_markup=markup)


@router.callback_query(F.data == 'change-driver-name')
async def change_driver_name(callback: types.CallbackQuery, state: FSMContext):
    """Изменение имени водителя"""
    logging.info('change_driver_name')
    markup = await user_keyboard.back_button('back-to-driver-lk')
    await state.set_state(FsmLk.get_new_name)
    await callback.message.edit_text('Введите новое имя 👇', reply_markup=markup)


@router.callback_query(F.data == 'change-driver-car')
async def change_car(callback: types.CallbackQuery, state: FSMContext):
    """Изменение опсиание машины"""
    logging.info('change_car')
    markup = await user_keyboard.back_button('back-to-driver-lk')
    await state.set_state(FsmLk.get_new_car)
    await callback.message.edit_text('Введите новое описание автомобиля 👇', reply_markup=markup)


@router.message(StateFilter(FsmLk.get_new_name))
async def get_new_name(message: types.Message, state: FSMContext):
    """Получение нового имени"""
    logging.info('get_new_name')
    new_name = str(message.text)
    if new_name == 'Личный кабинет 👤':
        await driver_lk(message=message, state=state)
    else:
        markup = await user_keyboard.yes_or_no_buttons('confirm-new-name')
        await state.update_data(new_name=new_name)
        await state.set_state(default_state)
        await message.answer(f'Вы уверены что хотите изменить имя на - {new_name}?', reply_markup=markup)


@router.message(StateFilter(FsmLk.get_new_car))
async def get_new_car(message: types.Message, state: FSMContext):
    """Получение нового описания автомобиля"""
    logging.info('get_new_car')
    new_car = str(message.text)
    if new_car == 'Личный кабинет 👤':
        await driver_lk(message=message, state=state)
    else:
        markup = await user_keyboard.yes_or_no_buttons('confirm-new-car')
        await state.update_data(new_car=new_car)
        await state.set_state(default_state)
        await message.answer(f'Вы уверены что хотите изменить описание автомобиля на - {new_car}?', reply_markup=markup)


@router.callback_query(F.data.startswith('confirm-new-name_'))
async def confirm_new_name_or_no(callback: types.CallbackQuery, state: FSMContext):
    """Подтвержление нового имени"""
    logging.info('confirm_new_name_or_no')
    flag = str(callback.data).split('_')[1]
    user_id = int(callback.from_user.id)
    username = str(callback.from_user.username)
    if flag == 'yes':
        state_data = await state.get_data()
        await user_requests.update_driver_data(user_id, 'name', state_data['new_name'], username)
        driver_data = await user_requests.get_driver_data(user_id)
        markup = await user_keyboard.lk_buttons()

        text = (f'Ваш личный кабинет\n\n'
                f'👤 Имя: {driver_data["driver_name"]}\n'
                f'🚕 Автомобиль: {driver_data["car_description"]}\n\n'
                f'Выберите что вы хотите изменить 👇')

        await state.clear()
        await state.set_state(default_state)
        await callback.message.edit_text(text=text, reply_markup=markup)

    else:
        markup = await user_keyboard.back_button('back-to-driver-lk')
        await state.set_state(FsmLk.get_new_name)
        await callback.message.edit_text('Введите новое имя 👇', reply_markup=markup)


@router.callback_query(F.data.startswith('confirm-new-car_'))
async def confirm_new_car(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение выбора новой машины"""
    logging.info('confirm_new_car')
    flag = str(callback.data).split('_')[1]
    user_id = int(callback.from_user.id)
    username = str(callback.from_user.username)
    if flag == 'yes':
        state_data = await state.get_data()
        await user_requests.update_driver_data(user_id, 'car', state_data['new_car'], username)
        driver_data = await user_requests.get_driver_data(user_id)
        markup = await user_keyboard.lk_buttons()

        text = (f'Ваш личный кабинет\n\n'
                f'👤 Имя: {driver_data["driver_name"]}\n'
                f'🚕 Автомобиль: {driver_data["car_description"]}\n\n'
                f'Выберите что вы хотите изменить 👇')

        await state.clear()
        await state.set_state(default_state)
        await callback.message.edit_text(text=text, reply_markup=markup)

    else:
        markup = await user_keyboard.back_button('back-to-driver-lk')
        await state.set_state(FsmLk.get_new_car)
        await callback.message.edit_text('Введите новое описание автомобиля 👇', reply_markup=markup)

















