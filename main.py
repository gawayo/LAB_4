import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

bot_token=os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=bot_token)
dp=Dispatcher(bot, storage=MemoryStorage())

#состояния
class Form(StatesGroup):
    name = State()
    course = State()
    check = State()
    num = State()

dictionary = {}

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! Я бот для подсчёта валюты. Введи /save_currency, чтобы сохранить валюту")

#после ввода команды /save_currency бот предлагает ввести название валюты;
@dp.message_handler(commands=['save_currency'])
async def save_command(message: types.Message):
    # Устанавливаем состояние name
    await Form.name.set()
    await message.reply("Введите название валюты")

#после ввода названия валюты бот предлагает ввести курс валюты к рублю;

# Обрабатываем состояние name
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    # Обновляем данные в состоянии name
    await state.update_data(name=message.text)
    await message.reply('Курс "'+ message.text +'" по отношению к рублю: ')
    await message.reply('Чтобы начать конвенртацию - введите /convert, чтобы добавить еще валюту введите /save_currency')
    # Устанавливаем состояние course
    await Form.course.set()

@dp.message_handler(state=Form.course)
async def process_course(message: types.Message, state: FSMContext):
    course = message.text
    # Получаем данные из состояния name
    name = await state.get_data()
    # Получаем название валюты из словаря
    name_dictionary = name['name']
    # В словарь добавляем имя валюты
    dictionary[name_dictionary] = course
    await state.finish()
    print(dictionary)


@dp.message_handler(commands=['convert'])
async def convert_comand(message: types.Message):
    await Form.check.set()
    await message.reply("Введите название валюты, которую вы сохраняли ранее")

@dp.message_handler(state=Form.check)
async def process_check(message: types.Message, state: FSMContext):
    #обновляем данные в текущем состоянии формы, добавляя данные сохраненной валюты.
    await state.update_data(check_course=message.text)
    await message.answer("Введите сумму для перевода в рубли")
    await Form.num.set()

@dp.message_handler(state=Form.num)
async def process_convert(message: types.Message, state: FSMContext):
    #получаем введенную пользователем сумму для перевода в рубли.
    num = message.text
    #извлекаем данные о названии сохраненной валюты.
    check_course = await state.get_data()
    #получаем название сохраненной валюты.
    name_dictionary = check_course['check_course']
    result = int(dictionary[name_dictionary]) * int(num)
    await message.reply(result)
    await state.finish()


if __name__ =='__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
