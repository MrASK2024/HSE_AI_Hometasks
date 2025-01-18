from weatherAPI import WeatherAPI
users = {}

class User:
    def __init__(self, user_id, weight, height, age, activity, city):
        self.user_id = user_id
        self.weight = weight
        self.height = height
        self.age = age
        self.activity = activity
        self.city = city
        self.water_goal = self.calculate_water_goal()
        self.calorie_goal = self.calculate_calorie_goal()
        self.logged_water = 0
        self.logged_calories = 0
        self.burned_calories = 0



    def add_or_update_user(self,user_id, weight, height, age, activity, city):
        user = User(user_id, weight, height, age, activity, city)
        users[user_id] = user

    def get_user_by_id(self, user_id):
        return users.get(user_id, None)

    def calculate_water_goal(self):
        self.water_goal = self.weight * 30 + 500 * (self.activity)
        temperature = WeatherAPI.get_weather(self.city)

        if temperature > 25:
            self.water_goal -= 1000

        return self.water_goal

    def calculate_calorie_goal(self):
        self.calorie_goal = 10 * self.weight + 6.25 * self.height - 5 * self.age
        # учеть пол или придумать прикол в зависимости от времени и типа тренировки
        return self.calorie_goal

    def calculate_rest_water(self):
        return self.water_goal - self.logged_water

    def log_water(self, amount):
        """Добавляет зарегистрированное количество воды."""
        self.logged_water += amount
        return self.water_goal - self.logged_water

    def log_calories(self, amount):
        """Добавляет зарегистрированное количество калорий."""
        self.logged_calories += amount

    def log_burned_calories(self, amount):
        """Добавляет зарегистрированное количество сожжённых калорий."""
        self.burned_calories += amount

    def log_activity(self, amount):
        self.activity += amount


    def user_to_dict(self, user):
        return {
            "weight": user.weight,
            "height": user.height,
            "age": user.age,
            "activity": user.activity,
            "city": user.city,
            "water_goal": user.water_goal,
            "calorie_goal": user.calorie_goal,
            "logged_water": user.logged_water,
            "logged_calories": user.logged_calories,
            "burned_calories": user.burned_calories,
        }
