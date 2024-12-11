import random
import json
import os

import numpy as np

class UserPreference():
    def __init__(self, user_id, items, epsilon=0.1):
        self.user_id = user_id
        self.items = items # Список всех товаров
        self.epsilon = epsilon
        self.counts = {item: 0 for item in items}
        self.likes = {item: 0 for item in items}

    def choose_item(self):
        if random.random() < self.epsilon:
            return random.choice(self.items)  # Исследование
        else:
            avg_likes = {item: self.likes[item] / self.counts[item] if self.counts[item] > 0 else 0 for item in self.items}
            if all(value == 0 for value in avg_likes.values()):
                return random.choice(self.items)

            # Используем Softmax для выбора товара
            probs = np.exp(np.array(list(avg_likes.values())))
            probs /= np.sum(probs)  # Нормализация
            best_item = np.random.choice(self.items, p=probs)
            return best_item

    def update(self, item, liked):
        self.counts[item] += 1
        if liked:
            self.likes[item] += 1

    def save(self, filename):
        data = {
            "user_id": self.user_id,
            "counts": self.counts,
            "likes": self.likes,
            "epsilon": self.epsilon
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load(cls, filename):
        if not os.path.exists(filename):
            return None
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls(data['user_id'], list(data['counts'].keys()), epsilon=data['epsilon']), data['counts'], data['likes']


# --- Пример использования ---

items = ["Товар A", "Товар B", "Товар C", "Товар D"]

user_id = 1

filename = f"user_preferences_{user_id}.json"

try:
    user_pref, counts, likes = UserPreference.load(filename)
    if user_pref: #Проверяем, что объект создан
      user_pref.counts = counts
      user_pref.likes = likes
      print("Данные пользователя загружены.")
    else:
      print("Файл с данными пользователя не найден. Создаем новый профиль.")
      user_pref = UserPreference(user_id, items)
except Exception as e:
    print(f"Ошибка при загрузке данных: {e}")
    user_pref = UserPreference(user_id, items)
# Симулируем несколько взаимодействий
while True:
    recommended_item = user_pref.choose_item()
    print(f"Рекомендуемый товар: {recommended_item}")
    liked = input(f"Нравится ли вам товар {recommended_item}? (да/нет): ").lower() == "да"
    user_pref.update(recommended_item, liked)
    # Сохраняем данные пользователя
    user_pref.save(filename)



print("\nСтатистика предпочтений:")
avg_likes = {item: user_pref.likes[item] / user_pref.counts[item] if user_pref.counts[item] > 0 else 0 for item in items}
print(avg_likes)