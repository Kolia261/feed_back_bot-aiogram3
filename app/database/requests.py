from app.database.models import async_session
from app.database.models import User, Ticket
from sqlalchemy import select, update, delete, desc
from datetime import datetime



async def add_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()
            return False
        elif user.name:
            return True
        return False


async def edit_user(tg_id, name, number, username=None):
    async with async_session() as session:
        user = await session.execute(update(User).where(User.tg_id == tg_id).values(name=name,
                                                                                   number=number,
                                                                                   username=username))
        await session.commit()

async def set_user_data(tg_id, new_user):
    async with async_session() as session:
        user = await session.execute(update(User).where(User.tg_id == tg_id).values(name=new_user.name,
                                                                                    pulls=new_user.pulls,
                                                                                    last_garant5=new_user.last_garant5,
                                                                                    last_garant20=new_user.last_garant20,
                                                                                    money=new_user.money))
        await session.commit()

async def add_ticket(text, tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        session.add(Ticket(text=text, user=user.id))
        await session.commit()


async def get_tickets():
    async with async_session() as session:
        tickets = await session.scalars(select(Ticket))
        return tickets


async def get_ticket(ticket_id):
    async with async_session() as session:
        ticket = await session.scalar(select(Ticket).where(Ticket.id == ticket_id))
        return ticket


async def get_user(u_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == u_id))
        return user

async def get_user_by_tg_id(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user

async def delete_ticket(ticket_id):
    async with async_session() as session:
        await session.execute(delete(Ticket).where(Ticket.id == ticket_id))
        await session.commit()