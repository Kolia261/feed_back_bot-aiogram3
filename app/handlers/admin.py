from aiogram import Router, F, Bot
from aiogram.filters.command import Command
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.keyboards import all_tickets
from app.database.requests import get_ticket, get_user, delete_ticket, get_user_by_tg_id, set_user_data

admin = Router()


class Answer(StatesGroup):
    answer = State()


class Admin(Filter):
    def __init__(self):
        self.admins = [1080165612, 1291733510]

    async def __call__(self, message: Message):
        return message.from_user.id in self.admins


@admin.message(Admin(), Command('tickets'))
async def tickets(message: Message):
    await message.answer('Список всех тикетов',
                         reply_markup=await all_tickets())


@admin.callback_query(F.data.startswith('ticket_'))
async def answer_ticket(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Answer.answer)
    await callback.answer('Вы выбрали тикет')
    ticket = await get_ticket(callback.data.split('_')[1])
    user = await get_user(ticket.user)
    await state.update_data(tg_id=user.tg_id)
    await state.update_data(ticket_id=ticket.id)
    await callback.message.answer(f'Вопрос: {ticket.text}\n\n{user.name} | {user.number} | {user.username}\n\nНапишите кол-во сигмакоинов, которое перечислил пользователь')



@admin.message(Admin(), Answer.answer)
async def send_answer(message: Message, state: FSMContext, bot: Bot):
    info = await state.get_data()
    if not message.text.isdigit():
        await message.answer('Неправильный формат ввода. Заново: /tickets')
        await state.clear()
        return
    if int(message.text) == 0:
        await bot.send_message(chat_id=info['tg_id'], text="Введенный вами код был не валидным.")
        await delete_ticket(info['ticket_id'])
        await message.answer('Тикет отклонен! Список тикетов: /tickets')
        await state.clear()
        return
    await bot.send_message(chat_id=info['tg_id'], text=f"Вам начислено {message.text} сигмакоинов на счет SigmaGacha.")
    user = await get_user_by_tg_id(info['tg_id'])
    user.money += int(message.text)
    await set_user_data(user.tg_id, user)
    await delete_ticket(info['ticket_id'])
    await message.answer('Коины начислены! Список тикетов: /tickets')
    await state.clear()