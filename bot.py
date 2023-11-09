import asyncio

from aiogram.filters import Command
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "6911628405:AAGsFXSQzBiHXo-ErOkN35EpIjmrD2lUq20"
ADMIN_CHAT_ID = -1002132090045

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
router = Router()

# ---------- BUTTONS ----------


async def generate_application_buttons(user_id: int) -> InlineKeyboardBuilder:

    application_buttons_builder = InlineKeyboardBuilder()

    accept_button = types.InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_application_button_{user_id}")
    reject_button = types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_application_button_{user_id}")

    application_buttons_builder.row(accept_button, reject_button)

    return application_buttons_builder
# -----------------------------


class ApplicationsStates(StatesGroup):
    choosing_age = State()
    choosing_work_time = State()
    choosing_income = State()


@router.message(Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    agree_button = types.InlineKeyboardButton(text="✅ Да, я согласен", callback_data="agree_button")
    builder.row(agree_button)
    await message.answer(text=f"Привет! Внимательно ознакомься с условиями и сутью работы: https://t.me/+wvuJe_Vpb4tiNGMy. Если заинтресован - жми кнопку ниже ⬇️", reply_markup=builder.as_markup())


@router.callback_query(F.data == "agree_button")
async def accept_agreement(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(text="Напиши свой возраст:")
    await state.set_state(ApplicationsStates.choosing_age)


@router.message(ApplicationsStates.choosing_age)
async def age_handler(message: types.Message, state: FSMContext):
    await state.update_data(chosen_age=message.text)
    await message.answer(text="Сколько времени ты готов уделять работе?")
    await state.set_state(ApplicationsStates.choosing_work_time)


@router.message(ApplicationsStates.choosing_work_time)
async def time_handler(message: types.Message, state: FSMContext):
    await state.update_data(chosen_time=message.text)
    await message.answer(text="Сколько планируешь зарабатывать с нами?")
    await state.set_state(ApplicationsStates.choosing_income)


@router.message(ApplicationsStates.choosing_income)
async def income_handler(message: types.Message, state: FSMContext):
    await state.update_data(chosen_income=message.text)
    application_data = await state.get_data()
    await message.answer(text="✅ Твоя заявка успешно отправлена!")
    await bot.send_message(ADMIN_CHAT_ID, text=f"📌 Новая заявка 📌\n\n От: @{message.from_user.username}\n\n 🧬 Возраст: {application_data.get('chosen_age')}\n\n 🕔 Время, которое готов уделять: {application_data.get('chosen_time')}\n\n 💰 В планах заработать: {application_data.get('chosen_income')}", reply_markup=(await generate_application_buttons(message.chat.id)).as_markup())
    await state.clear()


@router.callback_query(F.data.startswith("accept_application_button_"))
async def accept_application(callback_query: types.CallbackQuery):
    application_user_id = callback_query.data.split("_")[-1]
    await bot.send_message(application_user_id, text="✅ Поздравляем! Ваша заявка принята администратором! Вступай в рабочий чат по ссылке: https://t.me/+cyWuTT99H0oyZDAy")


@router.callback_query(F.data.startswith("reject_application_button_"))
async def accept_application(callback_query: types.CallbackQuery):
    application_user_id = callback_query.data.split("_")[-1]
    await bot.send_message(application_user_id, text="❌ К сожалению, ваша заявка была отклонена.")


async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
