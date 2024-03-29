from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def buy_start_kb(offer_id, type):
    yes = InlineKeyboardButton('Начать', callback_data= str(offer_id) + '_buy_'+type+'_start_yes')
    later = InlineKeyboardButton("Отложить", callback_data=str(offer_id) + '_buy_'+type+'_start_later')
    no = InlineKeyboardButton('Отмена', callback_data=str(offer_id) + '_buy_'+type+'_start_no')

    buy_start_kb = InlineKeyboardMarkup().row(yes, later).add(no)
    return buy_start_kb

buyer_disagree_kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Отмена", callback_data="buyer_cancel"))

