from aiogram.fsm.state import State, StatesGroup

class User_form(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()
    
    def is_valid_weight(value):
        try:
            weight = float(value)
            return 30.0 <= weight <= 300.0
        except ValueError:
            return False

    def is_valid_height(value):
        try:
            height = float(value)
            return 100.0 <= height <= 250.0
        except ValueError:
            return False

    def is_valid_age(value):
        try:
            age = int(value)
            return 12 <= age <= 120
        except ValueError:
            return False

    def is_valid_activity(value):
        try:
            activity = int(value)
            return 1 <= activity <= 1440
        except ValueError:
            return False
    