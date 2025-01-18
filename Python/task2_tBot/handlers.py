from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states_user import UserState, FoodState

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
@router.message(Command("set_profile"))
async def start_form(message: Message, state: FSMContext):
    await message.reply("Введите ваш вес (в кг):")
    await state.set_state(UserState.weight)
    
@router.message(UserState.weight)
async def process_weight(message: Message, state: FSMContext):
    weight=message.text
    if UserState.is_valid_weight(weight):
        await state.update_data(weight=weight)
        await message.reply("Введите ваш рост (в см):")
        await state.set_state(UserState.height)
    else:
        await message.reply("Некорректный ввод веса. Пожалуйста, введите число от 30 до 300.")

@router.message(UserState.height)
async def process_height(message: Message, state: FSMContext):
    height = message.text
    if UserState.is_valid_height(height):
        await state.update_data(height=height)
        await message.reply("Сколько вам лет?")
        await state.set_state(UserState.age)
    else:
        await message.reply("Некорректный ввод роста. Пожалуйста, введите число от 100 до 250.")
        

@router.message(UserState.age)
async def process_age(message: Message, state: FSMContext):
    age = message.text
    if UserState.is_valid_age(age):
        await state.update_data(age=age)
        await message.reply("Сколько минут активности у вас в день?")
        await state.set_state(UserState.activity)
    else:
        await message.reply("Некорректный ввод возраста. Пожалуйста, введите число от 12 до 120.")

@router.message(UserState.activity)
async def process_activity(message: Message, state: FSMContext):
    activity = message.text
    if UserState.is_valid_activity(activity):
        await state.update_data(activity=activity)
        await message.reply("В каком городе вы находитесь?")
        await state.set_state(UserState.city)
    else:
        await message.reply("Некорректный ввод активности. Пожалуйста, введите число от 1 до 1440.")

@router.message(UserState.city)
async def process_city(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    await User.add_or_update_user(
        user_id=user_id,
        weight=user_data.get('weight'),
        height=user_data.get('height'),
        age=user_data.get('age'),
        activity=user_data.get('activity'),
        city=user_data.get('city')
    )
    
    await message.reply(f"Привет! Твои данные успешно сохранены.")
    await state.clear()


@router.message(Command("log_water"))
async def log_water(message: Message):
    # await message.reply("Сколько воды вы сегодня выпили (в мл)?")
    # watter = message.text
    try:
        water = int(message.text.split()[1])
        user = User.get_user_by_id(message.from_user.id)
        user.log_water(water)
        await message.reply(f'Записано {water} мл выпитой воды')
    except ValueError:
        await message.reply("Некорректный ввод выпитой воды. Пожалуйста, введите только число")


@router.message(Command("log_food"))
async def log_food(message: Message, state: FSMContext):
    food = message.text.split()[1]

    if len(food) < 3:
        await message.reply("Пожалуйста, укажите название продукта после команды.")
        return

    food_fact = get_food_info(food)

    if food_fact:
        food_calories = int(food_fact['calories'])
        await state.update_data(food_calories=food_calories)
        await message.reply(f"{food} - {food_calories} ккал на 100 г. Сколько грамм вы съели?")
        await state.set_state(FoodState.food_grams)
    else:
        await message.reply("Некорректный ввод продукта. Пожалуйста, введите название продукта.")


@router.message(FoodState.food_grams)
async def get_food_grams(food_message: Message, state: FSMContext):
    try:
        food_fact = await state.get_data()
        food_calories = food_fact.get('food_calories')
        food_grams = int(food_message.text)
        current_calories = food_grams * food_calories / 100
        user = User.get_user_by_id(food_message.from_user.id)
        user.log_calories(current_calories)
        await food_message.reply(f"Записано {current_calories:.2f} ккал")
    except ValueError:
        await food_message.reply("Пожалуйста, введите корректное количество граммов.")
    finally:
        await state.clear()


@router.message(Command("log_workout"))
async def log_workout(message: Message):
    type_workout = message.text.split()[1]
    activity = int(message.text.split()[2])

    user = User.get_user_by_id(message.from_user.id)
    user.log_activity(activity)

    await message.reply(f"{type_workout} {activity} минут — {200} ккал. Дополнительно: выпейте {500 * activity / 30} мл воды.")
    
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