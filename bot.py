import random

import logging

import asyncio

from aiogram import Bot, Dispatcher, types

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.dispatcher import FSMContext

from aiogram.dispatcher.filters import Command

from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

API_TOKEN = '6093068610:AAHTFd6MiSX0CLIeJQ9gQarXsdY8MJRLoMk'

bot = Bot(token=API_TOKEN)

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

class GameStates(StatesGroup):

    playing = State()

async def game(update: types.Update, state: FSMContext):

    num1 = random.randint(1, 100)

    num2 = random.randint(1, 100)

    operator = random.choice(['+', '-', '*'])

    if operator == '+':

        answer = num1 + num2

    elif operator == '-':

        answer = num1 - num2

    elif operator == '*':

        answer = num1 * num2

    await state.update_data(answer=answer)

    answer_options = [answer]

    while len(answer_options) < 4:

        new_answer = random.randint(1, 200)

        if new_answer not in answer_options:

            answer_options.append(new_answer)

    random.shuffle(answer_options)

    keyboard = InlineKeyboardMarkup(row_width=2)

    for option in answer_options:

        callback_data = str(option)

        button = InlineKeyboardButton(str(option), callback_data=callback_data)

        keyboard.add(button)

    await bot.send_message(chat_id=update.from_user.id, text=f"{num1} {operator} {num2} = ?", reply_markup=keyboard)

    await GameStates.playing.set()

async def answer_handler(update: types.Update, state: FSMContext):

    user_answer = int(update.data)

    data = await state.get_data()

    correct_answer = data['answer']

    if user_answer == correct_answer:

        await bot.delete_message(update.message.chat.id, update.message.message_id)

        await bot.answer_callback_query(callback_query_id=update.id, text="Correct")

        await game(update, state)

    else:

        await bot.answer_callback_query(callback_query_id=update.id, text="Incorrect")

        await state.finish()

async def start_command_handler(update: types.Update):

    await bot.send_message(chat_id=update.chat.id, text="Welcome to the math game! Press the /play command to start.")

async def play_command_handler(update: types.Update, state: FSMContext):

    await game(update, state)

dp.register_message_handler(start_command_handler, Command("start"))

dp.register_message_handler(play_command_handler, Command("play"), state="*")

dp.register_callback_query_handler(answer_handler, state=GameStates.playing)

async def main():

    await dp.start_polling()

if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    loop.run_until_complete(main())

