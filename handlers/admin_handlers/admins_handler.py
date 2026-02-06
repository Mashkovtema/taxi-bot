from aiogram import Bot, types, Router, F
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ChatMemberStatus, ChatType

import logging

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests
from filters.admin_filter import IsSuperAdmin

config: Config = load_config()
router = Router()
router.message.filter(IsSuperAdmin())

class FsmAdmins(StatesGroup):
    get_name = State()


@router.message(F.text == 'Администраторы 👤', F.chat.type.in_({ChatType.PRIVATE}))
async def main_admins(message: types.Message, state: FSMContext):
    """Назначение удаление админов"""
    logging.info('main_admins')
    markup = await admin_keyboard.main_admins_menu_buttons()
    await state.clear()
    await state.set_state(default_state)
    await message.answer('Выберите действие 👇', reply_markup=markup)


@router.callback_query(F.data == 'back-to-main-admins')
async def back_to_main_admins(callback: types.CallbackQuery, state: FSMContext):
    """Назад в меню"""
    logging.info('back-to-main-admins')
    markup = await admin_keyboard.main_admins_menu_buttons()
    await state.set_state(default_state)
    await callback.message.edit_text('Выберите действие 👇', reply_markup=markup)


@router.callback_query(F.data == 'add-new-admin')
async def add_new_admin(callback: types.CallbackQuery, state: FSMContext):
    """Добавление нового админа"""
    logging.info('add_new_admin')
    markup = await admin_keyboard.back_buttons('back-to-main-admins')
    await state.set_state(FsmAdmins.get_name)
    await callback.message.edit_text('Введите имя администратора 👇', reply_markup=markup)


@router.message(StateFilter(FsmAdmins.get_name))
async def get_admin_name(message: types.Message, state: FSMContext):
    """Получение имени нового админа"""
    logging.info('get_admin_name')
    name = str(message.text)
    markup = await admin_keyboard.yes_or_no_buttons('confirm-new-admin')

    await state.update_data(admin_name=name)
    await state.set_state(default_state)
    await message.answer(f'Вы уверены что хотите добавить нового админа - {name}?', reply_markup=markup)


@router.callback_query(F.data.startswith('confirm-new-admin_'))
async def add_new_admin_or_no(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение добавления нового админа"""
    logging.info('add_new_admin_or_no')
    flag = str(callback.data).split('_')[1]
    if flag == 'yes':
        state_data = await state.get_data()
        admin_index = await admin_requests.add_new_admin(state_data['admin_name'])
        link = f'https://t.me/{config.tg_bot.bot_username}?start=adm_{admin_index}'
        await callback.message.edit_text(f'Новый админ добавлен ✅\n\n'
                                         f'Отправьте ему эту ссылку для того чтобы он присоединился к боту 👇\n'
                                         f'<code>{link}</code>')
        await state.set_state(default_state)
        await state.clear()
    else:
        markup = await admin_keyboard.back_buttons('back-to-main-admins')
        await state.set_state(FsmAdmins.get_name)
        await callback.message.edit_text('Введите имя администратора 👇', reply_markup=markup)


@router.callback_query(F.data == 'delete-admin')
async def delete_admins(callback: types.CallbackQuery, state: FSMContext):
    """Удаление администраторов"""
    logging.info('delete_admins')
    admins_list = await admin_requests.get_all_admins()
    if admins_list:
        markup = await admin_keyboard.admins_pagination(
            'select-admin-to-delete',
            'pagination-delete-admin',
            admins_list,
            0
        )
        await callback.message.edit_text('Выберите админа для разжалования 👇', reply_markup=markup)
    else:
        markup = await admin_keyboard.back_buttons('back-to-main-admins')
        await callback.message.edit_text('Вы еще не назначили ни одного админа ❌', reply_markup=markup)


@router.callback_query(F.data.startswith('pagination-delete-admin_'))
async def pagination_delete_admins(callback: types.CallbackQuery):
    """Пагинация админов для удаления"""
    logging.info('pagination_delete_admins')
    page = int(str(callback.data).split('_')[1])
    admins_list = await admin_requests.get_all_admins()
    markup = await admin_keyboard.admins_pagination(
        'select-admin-to-delete',
        'pagination-delete-admin',
        admins_list,
        page
    )
    if markup:
        await callback.message.edit_text('Выберите админа для разжалования 👇', reply_markup=markup)
        await callback.answer()
    else:
        await callback.answer()


@router.callback_query(F.data.startswith('select-admin-to-delete_'))
async def select_admin_to_delete(callback: types.CallbackQuery, state: FSMContext):
    """Выбор админа для удаления"""
    logging.info('select_admin_to_delete')
    admin_id = int(str(callback.data).split('_')[1])
    admin_data = await admin_requests.get_admin_data_by_id(admin_id)
    markup = await admin_keyboard.yes_or_no_buttons('confirm-delete-admin')

    text = (f'Информация об администраторе 👇\n\n'
            f'👤 Имя: {admin_data["admin_name"]}\n'
            f'📄 User_id: {admin_data["user_id"]}\n'
            f'<code>Если в графа user_id = 0, то администратор еще не перешел по ссылке</code>\n\n'
            f'Вы уверены что хотите разжаловать администратора?')

    await state.update_data(admin_id=admin_id)
    await callback.message.edit_text(text=text, reply_markup=markup)


@router.callback_query(F.data.startswith('confirm-delete-admin_'))
async def delete_admin_or_no(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение удаления админа"""
    logging.info('delete_admin_or_no')
    flag = str(callback.data).split('_')[1]
    if flag == 'yes':
        state_data = await state.get_data()
        markup = await admin_keyboard.back_buttons('delete-admin')
        await admin_requests.delete_admin(state_data['admin_id'])
        await callback.message.edit_text('Админ успешно удален ✅', reply_markup=markup)
    else:
        admins_list = await admin_requests.get_all_admins()
        if admins_list:
            markup = await admin_keyboard.admins_pagination(
                'select-admin-to-delete',
                'pagination-delete-admin',
                admins_list,
                0
            )
            await callback.message.edit_text('Выберите админа для разжалования 👇', reply_markup=markup)
        else:
            markup = await admin_keyboard.back_buttons('back-to-main-admins')
            await callback.message.edit_text('Вы еще не назначили ни одного админа ❌', reply_markup=markup)




















