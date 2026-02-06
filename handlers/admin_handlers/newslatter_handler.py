from aiogram import Bot, types, Router, F
from aiogram.types import InputMediaPhoto, InputMediaVideo
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, or_f
import logging

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard, user_keyboard
from database.requests import admin_requests
from filters.admin_filter import IsSuperAdmin

config: Config = load_config()
router = Router()
router.message.filter(IsSuperAdmin())


class FsmNewsletter(StatesGroup):
    media = State()
    text = State()


@router.message(F.text == 'Создать рассылку 📄')
async def create_newslatter(message: types.Message, state: FSMContext):
    """Начало создания рассыллки"""
    logging.info('create_newslatter')
    markup = await admin_keyboard.newslater_filter()
    await state.clear()
    await state.set_state(default_state)
    await message.answer('Выберите категорию водителей для рассылки 👇', reply_markup=markup)


@router.callback_query(F.data.startswith('select-filter-drivers_'))
async def select_drivers_type(callback: types.CallbackQuery, state: FSMContext):
    """ПОлучение типа водителей для рассылки"""
    logging.info('select_drivers_type')
    type_ = str(callback.data).split('_')[1]

    markup = await admin_keyboard.back_buttons('back-to-newslstter_type')

    await state.update_data(type=type_)
    await state.set_state(FsmNewsletter.text)
    await callback.message.edit_text('Введите текст для рассылки 📄', reply_markup=markup)


@router.message(StateFilter(FsmNewsletter.text))
async def get_text(message: types.Message, state: FSMContext):
    """
    получение текста для рассылки
    :param message:
    :param state:
    :return:
    """
    logging.info('get_text')
    text = str(message.text)

    markup = await admin_keyboard.scip_media_or_back_text()

    await state.update_data(text=text)
    await state.update_data(media='')
    await state.set_state(FsmNewsletter.media)
    await message.answer('Можете добавить фото/видео 📷', reply_markup=markup)


@router.message(StateFilter(FsmNewsletter.media))
async def get_media(message: types.Message, state: FSMContext):
    """
    Получение медиа файлов
    :param message:
    :param state:
    :return:
    """
    logging.info('get_media')
    state_data = await state.get_data()
    media = state_data['media']

    if message.video:
        file_id = f'video:{message.video.file_id}|'
        media += file_id

        await state.update_data(media=media)
        if len(media.split('|')) == 2:
            markup = await admin_keyboard.next_button()
            await message.answer('✅ Медиафайлы добавлены, нажмите на кнопку чтобы продолжить', reply_markup=markup)

    elif message.photo:
        file_id = f'photo:{message.photo[-1].file_id}|'
        media += file_id

        await state.update_data(media=media)
        if len(media.split('|')) == 2:
            markup = await admin_keyboard.next_button()
            await message.answer('✅ Медиафайлы добавлены, нажмите на кнопку чтобы продолжить', reply_markup=markup)

    else:
        await message.answer('Вы отправили не фото/видео, попробуйте еще раз')


@router.callback_query(or_f(F.data == 'next-to-watch', F.data == 'scip-media'))
async def get_text(callback: types.CallbackQuery, state: FSMContext):
    """
    Получение текста для рассылки и вывод рассылки
    :param callback:
    :param state:
    :return:
    """
    logging.info('get_text')
    state_data = await state.get_data()
    media = state_data['media']
    message_text = state_data['text']

    media_list = []
    media_input = media.split('|')[:-1]

    markup = await admin_keyboard.send_or_delete_buttons()
    if media_input:
        await callback.message.delete()

        if len(message_text) < 1024:
            for elem in media_input:
                if media_input.index(elem) != 0:
                    if elem.split(':')[0] == 'photo':
                        photo = InputMediaPhoto(media=elem.split(':')[1])
                        media_list.append(photo)
                    else:
                        video = InputMediaVideo(media=elem.split(':')[1])
                        media_list.append(video)
                else:
                    if elem.split(':')[0] == 'photo':
                        photo = InputMediaPhoto(media=elem.split(':')[1], caption=message_text)
                        media_list.append(photo)
                    else:
                        video = InputMediaVideo(media=elem.split(':')[1], caption=message_text)
                        media_list.append(video)

            await callback.message.answer_media_group(media=media_list)
            await callback.message.answer('Нажмите на кнопку чтобы отправить рассылку, либо отменить отправку',
                                          reply_markup=markup)

        else:
            for elem in media_input:
                if elem.split(':')[0] == 'photo':
                    photo = InputMediaPhoto(media=elem.split(':')[1])
                    media_list.append(photo)
                else:
                    video = InputMediaVideo(media=elem.split(':')[1])
                    media_list.append(video)

            await callback.message.answer_media_group(media=media_list)
            await callback.message.answer(message_text)
            await callback.message.answer('Нажмите на кнопку чтобы отправить рассылку, либо отменить отправку',
                                          reply_markup=markup)

    else:
        markup = await admin_keyboard.send_or_delete_buttons()
        await callback.message.edit_text(message_text, reply_markup=markup)


@router.callback_query(F.data == 'send-news-not')
async def cancel_send_newsletter(callback: types.CallbackQuery, state: FSMContext):
    """
    Отьмена отправки рассылки
    :param callback:
    :param state:
    :return:
    """
    logging.info('cancel_send_newsletter')
    await state.clear()
    await callback.message.edit_text('❌ Рассылка отменена')


@router.callback_query(F.data == 'send-news-end')
async def send_newsletter(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """
    Отправка рассылки
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('send_newsletter')
    state_data = await state.get_data()
    media = state_data['media']
    text = state_data['text']
    type = state_data['type']

    user_ids = await admin_requests.get_drivers_ids_for_newsletter(type)
    cnt_users = len(user_ids)

    media_list = []
    media_input = media.split('|')[:-1]
    if media_input:
        if len(text) < 1024:
            for elem in media_input:
                if media_input.index(elem) != 0:
                    if elem.split(':')[0] == 'photo':
                        photo = InputMediaPhoto(media=elem.split(':')[1])
                        media_list.append(photo)
                    else:
                        video = InputMediaVideo(media=elem.split(':')[1])
                        media_list.append(video)
                else:
                    if elem.split(':')[0] == 'photo':
                        photo = InputMediaPhoto(media=elem.split(':')[1], caption=text)
                        media_list.append(photo)
                    else:
                        video = InputMediaVideo(media=elem.split(':')[1], caption=text)
                        media_list.append(video)
        else:
            for elem in media_input:
                if elem.split(':')[0] == 'photo':
                    photo = InputMediaPhoto(media=elem.split(':')[1])
                    media_list.append(photo)
                else:
                    video = InputMediaVideo(media=elem.split(':')[1])
                    media_list.append(video)

        if len(text) < 1024:
            cnt_false = 0
            for id in user_ids:
                try:
                    await bot.send_media_group(chat_id=id, media=media_list)
                except:
                    cnt_false += 1
                    pass
        else:
            cnt_false = 0
            for id in user_ids:
                try:
                    await bot.send_media_group(chat_id=id, media=media_list)
                    await bot.send_message(chat_id=id, text=text)
                except:
                    cnt_false += 1
                    pass

    else:
        cnt_false = 0
        for id in user_ids:
            try:
                await bot.send_message(chat_id=id, text=text)
            except:
                cnt_false += 1
                pass

    await callback.message.edit_text(f'✅ Рассылка отправлена на {cnt_users} пользователей\n\n'
                                     f'Получили: {cnt_users - cnt_false}/{cnt_users} пользователей')
    await state.clear()


@router.callback_query(F.data.startswith('back-to-newslstter_'))
async def back_buttons(callback: types.CallbackQuery, state: FSMContext):
    """Обработка кнопок назад"""
    logging.info('back_buttons')
    flag = str(callback.data).split('_')[1]
    if flag == 'text':
        markup = await admin_keyboard.back_buttons('back-to-newslstter_type')
        await state.set_state(FsmNewsletter.text)
        await callback.message.edit_text('Введите текст для рассылки 📄', reply_markup=markup)

    if flag == 'media':
        markup = await admin_keyboard.scip_media_or_back_text()

        await state.update_data(media='')
        await state.set_state(FsmNewsletter.media)
        await callback.message.edit_text('Можете добавить фото/видео 📷', reply_markup=markup)

    if flag == 'type':
        markup = await admin_keyboard.newslater_filter()
        await callback.message.edit_text('Выберите категорию водителей для рассылки 👇', reply_markup=markup)






















