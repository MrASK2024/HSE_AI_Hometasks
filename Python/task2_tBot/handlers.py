from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import User_form
import aiohttp

from users import User
from foodFactsAPI import get_food_info

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать! Я ваш бот. \nВведите /help для списка команд.")
    

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Досутпные команды:\n"
        "/start - Начало работы\n"
        "/set_profile - Заполнить форму о себе\n"
        "/log_water <количество> - Логирование воды\n"
        "/log_food <название продукта> - Логирование еды\n"
        "/log_workout <тип тренировки> <время (мин)> - Логирование тренировки\n"
        "/check_progress - Показывает, сколько воды и калорий потреблено, сожжено и сколько осталось до выполнения цели\n"
        )


@router.message(Command("keyboard"))
async def show_keyboard(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Кнопка 1", callback_data="bt1")],
            [InlineKeyboardButton(text="Кнопка 2", callback_data="bt2")],
        ]
    )
    await message.reply("Выберите опцию:", reply_markup=keyboard)

@router.callback_query()
async def handle_callback(callback_query):
    if callback_query.data == "btn1":
        await callback_query.message.reply("Вы нажали Кнопка 1")
    elif callback_query.data == "btn2":
        await callback_query.message.reply("Вы нажали Кнопка 2")

# FSM: диалог с пользователем
@router.message(Command("form"))
async def start_form(message: Message, state: FSMContext):
    await message.reply("Введите ваш вес (в кг):")
    await state.set_state(User_form.weight)
    
@router.message(User_form.weight)
async def process_weight(message: Message, state: FSMContext):
    weight=message.text
    if User_form.is_valid_weight(weight):
        await state.update_data(weight=weight)
        await message.reply("Введите ваш рост (в см):")
        await state.set_state(User_form.height)
    else:
        await message.reply("Некорректный ввод веса. Пожалуйста, введите число от 30 до 300.")

@router.message(User_form.height)
async def process_height(message: Message, state: FSMContext):
    height = message.text
    if User_form.is_valid_height(height):
        await state.update_data(height=height)
        await message.reply("Сколько вам лет?")
        await state.set_state(User_form.age)
    else:
        await message.reply("Некорректный ввод роста. Пожалуйста, введите число от 100 до 250.")
        

@router.message(User_form.age)
async def process_age(message: Message, state: FSMContext):
    age = message.text
    if User_form.is_valid_age(age):
        await state.update_data(age=age)
        await message.reply("Сколько минут активности у вас в день?")
        await state.set_state(User_form.activity)
    else:
        await message.reply("Некорректный ввод возраста. Пожалуйста, введите число от 12 до 120.")

@router.message(User_form.activity)
async def process_activity(message: Message, state: FSMContext):
    activity = message.text
    if User_form.is_valid_activity(activity):
        await state.update_data(activity=activity)
        await message.reply("В каком городе вы находитесь?")
        await state.set_state(User_form.city)
    else:
        await message.reply("Некорректный ввод активности. Пожалуйста, введите число от 1 до 1440.")

@router.message(User_form.city)
async def process_city(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    User.add_or_update_user(
        user_id=user_id,
        weight=user_data.get['weight'],
        height=user_data.get['height'],
        age=user_data.get['age'],
        activity=user_data.get['activity'],
        city=user_data.get['city']
    )
    
    await message.reply(f"Привет! Твои данные успешно сохранены.")
    await state.clear()


@router.message(Command("log_water"))
async def log_water(message: Message):
    # await message.reply("Сколько воды вы сегодня выпили (в мл)?")
    # watter = message.text
    watter = message.get_args()
    if isinstance(watter, int):
        user = User.get_user_by_id(message.from_user.id)
        user.log_water(watter)
    else:
        await message.reply("Некорректный ввод выпитой воды. Пожалуйста, введите только число")


@router.message(Command("log_food"))
async def log_food(message: Message):
    # await message.reply("Сколько воды вы сегодня выпили (в мл)?")
    # watter = message.text
    food = message.get_args()
    if isinstance(food, str):
        food_fact = get_food_info(food)
        await message.reply(f"{food} - {food_fact['calories']} ккал на 100 г. Сколько грамм вы съели?")
        food_gram =  message.text
        if isinstance(food_gram, int):
            current_calories = food_gram * food_fact['calories'] / 100
            user = User.get_user_by_id(message.from_user.id)
            user.log_calories(current_calories)
            await message.reply(f"Записано {current_calories} ккал")
    #     ДОБАВИТЬ ПРОВЕРКИ
    else:
        await message.reply("Некорректный ввод продукта. Пожалуйста, введите название продукта")

@router.message(Command("log_workout"))
async def log_workout(message: Message):
    type_workout = message.get_args()[0]
    activity = message.get_args()[1]

    user = User.get_user_by_id(message.from_user.id)
    user.log_activity(activity)
    # water_goal = user.calculate_water_goal()
    # calorie_goal = user.calculate_calorie_goal()
    rest_water = user.calculate_rest_water()
    await message.reply(f"{type_workout} {activity} минут — {200} ккал. Дополнительно: выпейте {rest_water} мл воды.")
    
@router.message(Command("check_progress"))
async def check_progress(message: Message):
    user = User.get_user_by_id(message.from_user.id)
    logged_water = user.logged_water
    water_goal = user.water_goal
    rest_water = user.calculate_rest_water()

    logged_calories = user.logged_calories
    calorie_goal = user.calorie_goal
    calories_burned = 200 * (user.activity / 30)
    calorie_balance = calorie_goal - calories_burned

    await message.reply(f'''
    Прогресс:
    Вода:
        - Выпито: {logged_water} мл из {water_goal} мл.
        - Осталось: {rest_water} мл.
    Калории:
        - Потреблено: {logged_calories} ккал из {calorie_goal} ккал.
        - Сожжено: {calories_burned} ккал.
        - Баланс: {calorie_balance} ккал.
    ''')

# Функция для подключения обработчиков
def setup_handlers(dp):
    dp.include_router(router)