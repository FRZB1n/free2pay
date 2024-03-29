from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher, Bot
from functools import partial
from chat.chat import chat_start
from ..diamonds import *
from reviews.reviews import view_reviews

async def diamonds_kb_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await diamonds_kb_pr(call, state, db)

async def diamonds_by_one_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await one_diamond_offer(call, state, db)

async def buy_start_handler(call:types.CallbackQuery, state:FSMContext):
    await call.message.delete()
    await buy_diamonds_start(call, state)

async def count_process_handler(message:types.Message, state:FSMContext, db:Database):
    await diamonds_count_process(message, state, db)

#buy
async def diamond_seller_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await diamond_seller_start(call, state, db, bot)

async def diamond_get_lots_handler(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    await diamond_get_lots(message, state, db, bot)
#buy

async def change_diamond_count_start_handler(call:types.CallbackQuery, state:FSMContext):
    await call.message.delete()
    await change_diamond_count_start(call,state)
    
async def change_diamond_count_process_handler(message:types.Message, state:FSMContext, db:Database):
    await change_diamond_count_process(message, state, db)

async def delete_diamond_offer_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await delete_diamond_offer(call, state, db)


async def buy_porcess_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot):
    await call.message.delete()
    await diamond_buy_process(call, state, db, bot)


async def back_buttons_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await state.update_data(id = None)
    await diamonds_out(call, state, db)

async def chat_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, dp:Dispatcher,bot:Bot):
    await chat_start(call, state, db,dp, bot )

def diamonds_buy_handlers(dp: Dispatcher, dbc:Database, botc):
    new_diamonds_kb_handler = partial(diamonds_kb_handler, db=dbc)
    new_diamonds_buy_handlers = partial(diamonds_by_one_handler, db=dbc)
    new_count_process_handler = partial(count_process_handler, db=dbc)
    new_back_buttons_handler = partial(back_buttons_handler, db=dbc)
    new_change_diamond_count_process_handler = partial(change_diamond_count_process_handler, db=dbc)
    new_delete_diamond_offer_handler = partial(delete_diamond_offer_handler, db=dbc)
    new_buy_porcess_start_handler = partial(buy_porcess_start_handler, db=dbc, bot=botc)
    new_chat_start_handler = partial(chat_start_handler, db=dbc, bot=botc, dp=dp)
    new_view_reviews = partial(view_reviews, db=dbc)
    new_diamond_seller_start_handler = partial(diamond_seller_start_handler, db=dbc, bot=botc )
    new_diamond_get_lots_handler = partial(diamond_get_lots_handler, db=dbc, bot=botc )

    dp.register_callback_query_handler(new_diamond_seller_start_handler, lambda c: "_buy_diamonds_start_" in c.data, state="*")
    dp.register_message_handler(new_diamond_get_lots_handler, state=buy_list.seller_ready)

    dp.register_callback_query_handler(new_view_reviews, lambda c:c.data=="buyer_reviews", state=diamonds_list.id)
    
    dp.register_callback_query_handler(new_diamonds_kb_handler, lambda c: c.data.endswith("_offers"), state=diamonds_list.cur_list )
    dp.register_callback_query_handler(new_diamonds_buy_handlers, lambda c: c.data.startswith("dia_offer_id:"), state=diamonds_list.cur_list )
    dp.register_callback_query_handler(buy_start_handler, lambda c: c.data == "buyer_buy"  or c.data == "d_button_change_dia",state =[diamonds_list.id,diamonds_list.sum])
    dp.register_callback_query_handler(new_back_buttons_handler, lambda c: c.data == "back_from_one" or c.data == "d_button_cancel_buy",state=[diamonds_list.id,diamonds_list.sum] )
    
    dp.register_callback_query_handler(change_diamond_count_start_handler, lambda c:c.data=="seller_count", state=diamonds_list.id)
    dp.register_message_handler(new_change_diamond_count_process_handler, state=diamonds_list.id)
    dp.register_callback_query_handler(new_delete_diamond_offer_handler, lambda c:c.data=="seller_delete", state=diamonds_list.id)
    
    
    dp.register_callback_query_handler(new_chat_start_handler, lambda c: c.data == "buyer_chat", state=diamonds_list.id)

    dp.register_callback_query_handler(new_buy_porcess_start_handler, lambda c: c.data == "d_button_buy", state=diamonds_list.sum)

    dp.register_message_handler(new_count_process_handler,state=diamonds_list.buy_count )
    
    