from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId
from ..keyboards.offers.things_offers import offers_kb
from ..keyboards.seller_kb import seller_kb
from ..keyboards.buyer_kb import buyer_kb
from usefull.converters import things_to_text
from keyboards.menu import menu_kb
from ..keyboards.l2m_things import l2m_things_cat

class things_list(StatesGroup):
    cur_list = State()
    id = State()

async def things_out(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    offers = []
    for offer in db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").limit(11):
        offers.append(offer)
    await things_list.cur_list.set()
    await state.update_data(cur_list = 10)
   

    if len(offers) > 0:
        await call.message.answer("Вот все наши предложения: ",reply_markup=offers_kb(offers, 10, db))
    else:
        await state.finish()
        await call.message.answer("В данном разделе отсутсвуют товары", reply_markup=menu_kb)




async def things_kb_pr(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    if call.data.startswith("things_"):
        _cur_list = 10
        _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False, "type":call.data}).sort("cost").limit(11)
        await call.message.edit_text("Вот все предложения в классе "+things_to_text(call.data)+":")


    match call.data.replace("_offers", ""):
        case "forward":
            _cur_list = data.get("cur_list") + 10
            _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").skip(data.get("cur_list")).limit(11)
        case "back":
            _cur_list = data.get("cur_list") - 10
            if _cur_list == 10:
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").limit(11)
            else:
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").skip(_cur_list-10).limit(11)

        case "type":
            await call.message.delete()
            _cur_list = 10
            await call.message.answer("Выбери тип", reply_markup=l2m_things_cat)
            await state.update_data(cur_list = _cur_list)
            return

        case "cancel":
            await state.finish()
            await call.message.delete()
            return
        
    
    offers = []
    for offer in _offers:
        offers.append(offer)
    
    if len(offers) <= 0:
        await call.message.edit_text("В данной категории нет предложений")
        
    await state.update_data(cur_list = _cur_list)
    await call.message.edit_reply_markup(offers_kb(offers, _cur_list, db))


async def one_thing_offer(call:types.CallbackQuery, state:FSMContext, db:Database, rev = False):
    if not rev:
        cur_id = ObjectId(call.data.replace("th_offer_id:", ""))
    else:
        data = await state.get_data()
        cur_id = data.get("id")


    await things_list.id.set()
    await state.update_data(id = cur_id)
    product = db["l2m"].find_one({"_id":cur_id})
    seller = db["users"].find_one({"telegram_id":product["seller"]})
    if call.message.chat.id == product["seller"]:
        reply_kb = seller_kb
    else:
        reply_kb = buyer_kb

    if seller["statistics"]["total"] >0:
        rat = seller["statistics"]["successful"] / (seller["statistics"]["total"]/100)
    else:
        rat = 0
        
    await call.message.answer(
        "Продавец: " + str(seller["local_name"]) + "\n" +
        "Тип: " + str(things_to_text(product["type"])) + "\n" +
        "Описание: " + str(product["description"]) + "\n" +
        "Цена: " + str(product["cost"]) + "\n" +
        "Рейтинг: "+str(rat)+"%",
        reply_markup= reply_kb
        
    )

async def delete_things_offer(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    db["l2m"].delete_one({"_id":data.get("id")})
    await call.message.answer("Предложение успешно удалено")
    await things_out(call,state, db)