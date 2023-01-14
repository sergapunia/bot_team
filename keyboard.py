from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, executor, types
from main import opened_position_long
TOKEN = '5886578012:AAHIPhYEMgf_UxqbLDR0v5NJc7XjY-0X5AI'
CHAT = '624736798'
bot = Bot(TOKEN)
dp = Dispatcher(bot)

# kb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
# b1=KeyboardButton('/pars')
# b2=KeyboardButton('balance')
# b3=KeyboardButton('hello')
# b4=KeyboardButton('help')
# b5=KeyboardButton('quit')
# kb.add(b1).insert(b2).add(b3).insert(b4).add(b5)

aa=['1','2','3']
ikb= InlineKeyboardMarkup(row_width=3,
                          inline_keyboard=[[
                              InlineKeyboardButton(text='прив',callback_data='hihi')
                          ]])
for i in opened_position_long:
    i = InlineKeyboardButton(text=i,callback_data='ff')
    ikb.add(i)

@dp.message_handler(commands=["1"])
async def mmmmm(message: types.Message):
    await message.answer(opened_position_long,
                         reply_markup=ikb)

@dp.callback_query_handler(text='hihi')
async def com(callback : types.CallbackQuery):
    await callback.message.answer('нажал')
    await callback.answer()
# @dp.message_handler(commands=['start'])
# async def startcom(message: types.Message):
#     await message.answer(text='hi',
#                          reply_markup=kb)
#
# @dp.message_handler(commands=['pars'])
# async def startcom(message: types.Message):
#     await message.answer(text='hi',
#                          reply_markup=ikb)

if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)