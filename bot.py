from multiprocessing import Process
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.webhook import *
from aiogram import types
from pymongo import MongoClient
from flask import Flask
from flask_sslify import SSLify
import cherrypy
from aiohttp import web
from middleware.ban import ban_user
from config import BOT_TOKEN, MONGO_API

from start.preview import preview
from start.registration import *
from exchange.exchange import *
from personal_area.reviews import reviews_process
from personal_area.deals import deals_process
from exchange.sell import sell_states, diamonds_cost, diamonds_set, diamonds_under_server, diamonds_count, commission, diamonds_db_set, redact_diamonds
from exchange.buy import buy_states, offers_kb


client = MongoClient(MONGO_API)
db = client["test_db"]

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

ban_middleware = ban_user(db['users'])
dp.middleware.setup(ban_middleware)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await preview(message, db)

@dp.callback_query_handler(lambda c: c.data == "registration")
async def registration_handler(call: types.CallbackQuery):
    await call.message.delete()
    await license_agreement(call.message)

@dp.callback_query_handler(lambda c: c.data.startswith('license_'))
async def license_agreement_handler(call: types.CallbackQuery):
    await license_agreement_process(call, db)
    await call.message.delete()

@dp.message_handler(state= registration_states.nickname)
async def nickname_handler(message:types.Message, state:FSMContext):
    await password(message, state)

@dp.message_handler(state= registration_states.password)
async def password_handler(message:types.Message, state:FSMContext):
    await password_process(message, state, db)

@dp.message_handler()
async def menu_handler(message:types.Message, state:FSMContext):
    match message.text:
        case "Профиль":
            await personal_area(message, db)
        case "Отзывы":
            await reviews_process(message, db)
        case "Сделки":
            await deals_process(message, db)
        case "Купить" | "Продать":
            await message.delete()
            await exchange_process(message, state)
    
        





@dp.callback_query_handler(lambda c: c.data.startswith("game_"), state=exchange_states.game)
async def category_handler(call:types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await category_process(call, state)

@dp.callback_query_handler(lambda c: c.data.startswith("cat_"), state=exchange_states.game_type)
async def init_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await init_process(call, state, db)



@dp.callback_query_handler(lambda c: c.data.startswith("l2m_server_"), state=sell_states.server)
async def l2m_server_handler(call: types.CallbackQuery, state:FSMContext):
    await call.message.delete()
    await diamonds_under_server(call, state)


@dp.callback_query_handler(lambda c: c.data.startswith("l2m_under_"), state=sell_states.under_server)
async def l2m_server_handler(call: types.CallbackQuery, state:FSMContext):
    await call.message.delete()
    await diamonds_count(call, state)



@dp.message_handler(state=sell_states.diamonds)
async def diamonds_handler(message:types.Message, state:FSMContext):
    await diamonds_cost(message, state)

@dp.message_handler(state=sell_states.diamonds_cost)
async def commission_handler(message:types.Message, state:FSMContext):
    await commission(message, state)


@dp.callback_query_handler(lambda c: c.data.startswith("comission_"), state=sell_states.comission)
async def diamonds_cost_handler(call:types.CallbackQuery, state:FSMContext):
    await call.message.delete()
    await diamonds_set(call, state, db)


@dp.callback_query_handler(lambda c: c.data.startswith("sell_"), state=sell_states.comission)
async def diamonds_cost_handler(call:types.CallbackQuery, state:FSMContext):
    await call.message.delete()
    match call.data.replace("sell_", ""):
        case "post":
            await diamonds_db_set(call, state, db)
        case "redact":
            await redact_diamonds(call, state)


@dp.callback_query_handler(lambda c: c.data.endswith("_offers"), state=buy_states.cur_list)
async def offers_process(call:types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    match call.data.replace("_offers", ""):
        case "forward":
            _cur_list = data.get("cur_list") + 10
            _offers = db[data.get("game_type").replace("cat_", "")].find({"game":data.get("game")}).sort("cost_per_one").skip(data.get("cur_list")).limit(11)
        case "back":
            _cur_list = data.get("cur_list") - 10
            if _cur_list == 10:
                _offers = db[data.get("game_type").replace("cat_", "")].find({"game":data.get("game")}).sort("cost_per_one").limit(11)
            else:
                _offers = db[data.get("game_type").replace("cat_", "")].find({"game":data.get("game")}).sort("cost_per_one").skip(_cur_list-10).limit(11)
        case "cancel":
            await state.finish()
            await call.message.delete()
            return
    
    offers = []
    for offer in _offers:
        offers.append(offer)
    
    await state.update_data(cur_list = _cur_list)
    await call.message.edit_reply_markup(offers_kb(offers, _cur_list))


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
