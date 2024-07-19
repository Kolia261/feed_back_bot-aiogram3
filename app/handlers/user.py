from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove

from app.database import requests as rq
from app import keyboards as kb
from random import randint as rnd

user = Router()


class Process(StatesGroup):
    name = State()
    number = State()
    question = State()
    question2 = State()


@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await rq.add_user(message.from_user.id)
    if not user:
        await message.answer('Добро пожаловать в SigmaGacha_bot!\n\nВведите ваше имя')
        await state.set_state(Process.name)
    else:
        await message.answer('Нажми на кнопку Новый запрос, и следуй инструкциям', reply_markup=kb.new_ticket)


@user.message(Process.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Process.number)
    await message.answer('Отправьте по кнопке ваш номер телефона',
                         reply_markup=kb.send_number)


@user.message(Process.number, F.contact)
async def get_number(message: Message, state: FSMContext):
    await state.update_data(number=message.contact.phone_number)
    await state.set_state(Process.question)
    await message.answer(
        'Напиши код для отправки сигмакоинов \n Как это сделать? \n Вот подробная инструкция: \n 1.Открой сигма бот(https://t.me/sigma_mail_bot) \n 2.Нажми на кнопку Menu \n 3. Выбери в меню команду /transfer или просто напиши ее боту. \n Выбери количество сигмакоинов \n Отправь код в нашего бота',
        reply_markup=ReplyKeyboardRemove())


@user.message(Process.question)
async def get_question(message: Message, state: FSMContext):
    user = await state.get_data()
    await rq.edit_user(message.from_user.id,
                       user['name'],
                       user['number'],
                       message.from_user.username)
    await rq.add_ticket(message.text, message.from_user.id)
    await message.answer(
        'Спасибо, ваше обращение добавлено. Ожидайте подтверждения, может занять от 2 минут (в зависимости от нагрузки сервера)',
        reply_markup=kb.new_ticket)
    await state.clear()


@user.message(F.text == 'Новый запрос')
async def new_question(message: Message, state: FSMContext):
    await state.set_state(Process.question2)
    await message.answer(
        'Напиши код для отправки сигмакоинов \n Как это сделать? \n Вот подробная инструкция: \n 1.Открой сигма бот(https://t.me/sigma_mail_bot) \n 2.Нажми на кнопку Menu \n 3. Выбери в меню команду /transfer или просто напиши ее боту. \n Выбери количество сигмакоинов \n Отправь код в нашего бота',
        reply_markup=ReplyKeyboardRemove())


@user.message(Process.question2)
async def get_question(message: Message, state: FSMContext):
    await rq.add_ticket(message.text, message.from_user.id)
    await message.answer(
        'Спасибо, ваше обращение добавлено. Ожидайте подтверждения, может занять от 2 минут (в зависимости от нагрузки сервера)',
        reply_markup=kb.new_ticket)
    await state.clear()


def playing(pulls, last_garant5, last_garant20):
    pull5 = pulls - last_garant5
    ans = (0, pulls, last_garant5, last_garant20)
    if pull5 >= 3:
        if rnd(1, 2) == 1:
            ans = (1, pulls, pulls, last_garant20)
    if pull5 == 5:
        ans = (1, pulls, pulls, last_garant20)
    pull20 = pulls - last_garant20
    if pull20 >= 17:
        if rnd(1, 5) == 1:
            ans = (2, pulls, pulls, pulls)
    if pull20 == 20:
        ans = (2, pulls, pulls, pulls)
    if pulls == 150:
        ans = (3, pulls, pulls, pulls)
    elif rnd(1, 10000000) == 5000:
        ans = (3, pulls, pulls, pulls)
    return ans


@user.message(Command("play"))
async def cmd_play(message: Message, state: FSMContext):
    user = await rq.get_user_by_tg_id(message.from_user.id)
    if not user:
        await message.answer('Данная команда доступна лишь авторизованным пользователям!\n\nВоспользуйся /start')
    else:
        if user.money < 15:
            await message.answer(
                "У вас слишком мало сигмакоинов на балансе (меньше 15). Чтобы пополнить, напишите /start и следуйте инструкциям.")
            return
        await message.answer('Запускаем магию!')
        ans = playing(user.pulls + 1, user.last_garant5, user.last_garant20)
        user.pulls = ans[1]
        user.last_garant5 = ans[2]
        user.last_garant20 = ans[3]
        user.money = user.money - 15
        await rq.set_user_data(user.tg_id, user)
        if ans[0] == 0:
            await message.answer('К сожалению, вы ничего не выиграли в этот раз :(')
        elif ans[0] == 1:
            await message.answer(
                'Вау, ты выиграл приз №1!\n\nПодойди к нам на ярмарке и покажи это сообщение, чтобы получить приз!')
        elif ans[0] == 2:
            await message.answer(
                'ОГО! Ты выиграл приз №2!\n\nПодойди к нам на ярмарке и покажи это сообщение, чтобы получить приз!')
        elif ans[0] == 3:
            await message.answer(
                'Ёк макарек, кажется ты претендуешь на приз №3!\n\nСкорее беги к нам на ярмарке и покажи это сообщение, чтобы получить приз (он всего один на всех!)')


@user.message(Command("stats"))
async def cmd_stats(message: Message, state: FSMContext):
    user = await rq.get_user_by_tg_id(message.from_user.id)
    if not user:
        await message.answer('Данная команда доступна лишь авторизованным пользователям!\n\nВоспользуйся /start')
    else:
        msg = f"Статистика по пользователю {user.name} ({user.username}):\n\n1. Сигмакоинов осталось: {user.money}\n2. Всего было попыток: {user.pulls}\n3. Гаранты: {user.pulls - user.last_garant5}/5 | {user.pulls - user.last_garant20}/20"
        await message.answer(msg)