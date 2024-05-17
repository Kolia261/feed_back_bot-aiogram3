from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_tickets

send_number = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить номер телефона', request_contact=True)]
],                                resize_keyboard=True,
                                  input_field_placeholder='Отправьте телефон по кнопке ниже')


async def all_tickets():
    tickets = await get_tickets()
    keyboard = InlineKeyboardBuilder()
    for ticket in tickets:
        keyboard.add(InlineKeyboardButton(text=f'Тикет № {ticket.id}',
                                          callback_data=f'ticket_{ticket.id}'))
    return keyboard.adjust(2).as_markup()


new_ticket = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Новый запрос')]
],                                resize_keyboard=True)