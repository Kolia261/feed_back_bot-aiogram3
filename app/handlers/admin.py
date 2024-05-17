from aiogram import Router, F, Bot
from aiogram.filters.command import Command
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.keyboards import all_tickets
from app.database.requests import get_ticket, get_user, delete_ticket

admin = Router()


class Answer(StatesGroup):
    answer = State()


class Admin(Filter):
    def __init__(self):
        self.admins = [5077093829]

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
    await callback.message.answer(f'Вопрос: {ticket.text}\n\n{user.name} | {user.number} | {user.username}\n\nНапишите ответ')


@admin.message(Admin(), Answer.answer)
async def send_answer(message: Message, state: FSMContext, bot: Bot):
    info = await state.get_data()
    await bot.send_message(chat_id=info['tg_id'], text=message.text)
    await delete_ticket(info['ticket_id'])
    await message.answer('Сообщение отправлено!')
    await state.clear()