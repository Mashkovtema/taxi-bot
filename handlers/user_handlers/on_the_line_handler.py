from aiogram import Bot, types, Router, F
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType
import logging

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests, user_requests

config: Config = load_config()
router = Router()


@router.message(F.text == 'Выйти на линию ✅', F.chat.type.in_({ChatType.PRIVATE}))
async def go_to_the_line(message: types.Message, state: FSMContext):
    """Выход на линию"""
    logging.info('go_to_the_line')
    user_id = int(message.from_user.id)
    driver_data = await user_requests.get_driver_data(user_id)
    await state.clear()
    await state.set_state(default_state)
    if driver_data['banned']:
        await message.answer('Вы заблокированы администратором, вы не можете выйти на линию ❌')
    else:
        markup = await user_keyboard.main_driver_buttons(True)
        await user_requests.go_or_out_of_line(user_id, True)
        await message.answer('Вы на линии, теперь вам будут поступать заявки ✅', reply_markup=markup)


@router.message(F.text == 'Уйти с линии ❌', F.chat.type.in_({ChatType.PRIVATE}))
async def go_out_of_line(message: types.Message, state: FSMContext):
    """Уход с линии"""
    logging.info('go_out_of_line')
    user_id = int(message.from_user.id)
    driver_data = await user_requests.get_driver_data(user_id)
    await state.clear()
    await state.set_state(default_state)
    if driver_data['banned']:
        await message.answer('Вы заблокированы администратором, вы не можете выйти на линию ❌')
    else:
        markup = await user_keyboard.main_driver_buttons(False)
        await user_requests.go_or_out_of_line(user_id, False)
        await message.answer('Вы ушли с линии, заявки больше не будут поступать ❌', reply_markup=markup)