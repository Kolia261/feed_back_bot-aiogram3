from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from app.database import requests as rq
from app import keyboards as kb

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
        await message.answer('Добро пожаловать!\n\nВведите ваше имя')
        await state.set_state(Process.name)
    else:
        await message.answer('Отправить новый запрос можно по кнопке ниже', reply_markup=kb.new_ticket)


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
    await message.answer('Напишите свой запрос.',
                         reply_markup=ReplyKeyboardRemove())


@user.message(Process.question)
async def get_question(message: Message, state: FSMContext):
    user = await state.get_data()
    await rq.edit_user(message.from_user.id,
                       user['name'],
                       user['number'],
                       message.from_user.username)
    await rq.add_ticket(message.text, message.from_user.id)
    await message.answer('Спасибо, ваше обращение добавлено.', reply_markup=kb.new_ticket)
    await state.clear()


@user.message(F.text == 'Новый запрос')
async def new_question(message: Message, state: FSMContext):
    await state.set_state(Process.question2)
    await message.answer('Напишите свой запрос.',
                         reply_markup=ReplyKeyboardRemove())


@user.message(Process.question2)
async def get_question(message: Message, state: FSMContext):
    await rq.add_ticket(message.text, message.from_user.id)
    await message.answer('Спасибо, ваше обращение добавлено.', reply_markup=kb.new_ticket)
    await state.clear()