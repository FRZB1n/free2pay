from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton

from usefull.converters import things_to_text
        
def offers_kb(posts, n, db):
    offers_kb = InlineKeyboardMarkup()
    for i in range(len(posts)):
        if(i>=10):
            break
        seller = db["users"].find_one({"telegram_id":posts[i]["seller"]})
        if seller["statistics"]["total"] >0:
            rat = seller["statistics"]["successful"] / (seller["statistics"]["total"]/100)
        else:
            rat = 0
        seller_name = seller["local_name"]
        cur = InlineKeyboardButton("Продавец: "+seller_name +"|Тип: "+ things_to_text(posts[i]["type"]) + "|Описание: "+str(posts[i]["description"][:10])+"|Цена: "+str(posts[i]["cost"]) +"|Рейтинг: "+str(round(rat))+"%", callback_data="th_offer_id:"+str(posts[i]["_id"]))
        offers_kb.add(cur)

    offers_kb.add(InlineKeyboardButton("По типу", callback_data="type_offers"))


    if n == 10 and len(posts) < 11:
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(cancel)
    elif n == 10 and len(posts) == 11:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_offers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(forward)
        offers_kb.row(cancel)
    elif n > 10 and len(posts) < 11:
        back= InlineKeyboardButton("Назад", callback_data="back_offers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(back)
        offers_kb.row(cancel)
    else:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_offers" )
        back= InlineKeyboardButton("Назад", callback_data="back_offers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(back, forward)
        offers_kb.row(cancel)
    

   

    return offers_kb