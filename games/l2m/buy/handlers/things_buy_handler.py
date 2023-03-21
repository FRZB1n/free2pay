from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial


from ..things import *
from ..buy import buy_process

async def things_kb_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await things_kb_pr(call, state, db)

async def things_by_one_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await one_thing_offer(call, state, db)

async def buy_porcess_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await buy_process(call, state, db)


async def back_buttons_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await state.update_data(id = None)
    await things_out(call, state, db)

def things_buy_handler(dp:Dispatcher, dbc:Database):
    new_things_kb_handler = partial(things_kb_handler, db=dbc)
    new_things_by_one_handler = partial(things_by_one_handler, db=dbc)
    new_back_buttons_handler = partial(back_buttons_handler, db=dbc)
    new_buy_porcess_start_handler = partial(buy_porcess_start_handler, db = dbc)
    dp.register_callback_query_handler(new_things_kb_handler, lambda c: c.data.endswith("_offers"), state=things_list.cur_list)
    dp.register_callback_query_handler(new_things_by_one_handler, lambda c: c.data.startswith("th_offer_id:"), state=things_list.cur_list)
    dp.register_callback_query_handler(new_buy_porcess_start_handler, lambda c: c.data == "buyer_buy", state=things_list.id)
    dp.register_callback_query_handler(new_back_buttons_handler, lambda c: c.data=="back_from_one", state=things_list.id)