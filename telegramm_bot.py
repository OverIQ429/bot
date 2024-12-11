import random
import json
import os

import numpy as np
from telebot import types
import telebot

class UserPreference():
    def __init__(self, user_id, items, epsilon=0.8):
        self.user_id = user_id
        self.items = items # Список всех товаров
        self.epsilon = epsilon
        self.counts = {item_id: 0 for item_id in items}
        self.likes = {item_id: 0 for item_id in items}

    def choose_item(self):
        if random.random() < self.epsilon:
            item_id = np.random.choice(list(self.items))
            return item_id, self.items[int(item_id) - 1]  # Возвращаем ID и название товара

        else:
            avg_likes = {item_id: self.likes[item_id] / self.counts[item_id] if self.counts[item_id] > 0 else 0 for item_id in self.items}
            if all(value == 0 for value in avg_likes.values()):
                item_id = np.random.choice(list(self.items))
                return item_id, self.items[int(item_id) -1 ]

            # Используем Softmax для выбора товара
            probs = np.exp(np.array(list(avg_likes.values())))
            probs /= np.sum(probs)
            item_id = np.random.choice(list(self.items), p=probs)
            return item_id, self.items[int(item_id) -1]

    def update(self, item_id, liked):
        self.counts[item_id[0]] += 1
        if liked == "yes":
            self.likes[item_id[0]] += 1

    def save(self, filename):
        data = {
            "user_id": self.user_id,
            "items": self.items,
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

bot = telebot.TeleBot('8117985808:AAEPmdm94_aAXIkQ7EY3A96HtDX1JD6cuyc')
global user_id
global filename
initial_products = {
    1: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 1", "description": "Описание товара 1"},
    2: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 2", "description": "Описание товара 2"},
    3: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 3", "description": "Описание товара 3"},
    4: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 4", "description": "Описание товара 4"},
    5: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 5", "description": "Описание товара 5"},
    6: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 6", "description": "Описание товара 6"},
    7: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 7", "description": "Описание товара 7"},
    8: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 8", "description": "Описание товара 8"},
    9: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 9", "description": "Описание товара 9"},
    10: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 10", "description": "Описание товара 10"},
    11: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 11", "description": "Описание товара 11"},
    12: {"image": "-1wUz1LibUNJjsKBZnAbcIblw1OZO3_130HSybEvqqaHV8TNJS-EYPYO4PQNhacHnFwTG6Csi2ZqWxcXqPD1rqKk.jpg", "name": "Товар 12", "description": "Описание товара 12"},
}

current_product_index = 0

@bot.message_handler(commands=['start'])
def handle_start(message):
    global current_product_index
    global user_pref
    user_id = message.from_user.id
    filename = f"user_preferences_{user_id}.json"
    global current_product_index
    product_id, product_data = list(initial_products.items())[current_product_index]
    if UserPreference.load(filename):
        user_pref, counts, likes = UserPreference.load(filename)
        user_pref.counts = counts
        user_pref.likes = likes
        print(product_data)
        print("Данные пользователя загружены.")
    else:
        print(user_id)
        print("Файл с данными пользователя не найден. Создаем новый профиль.")
        user_pref = UserPreference(user_id, initial_products)
    show_product(message, product_data)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    recommended_item = user_pref.choose_item()
    user_pref.update(recommended_item, call.data)
    global current_product_index
    current_product_index = int(recommended_item[0])
    user_id = call.from_user.id
    filename = f"user_preferences_{user_id}.json"
    user_pref.save(filename)
    product_id, product_data = list(initial_products.items())[current_product_index-1]
    show_product(call.message, product_data)

def show_product(message, product_data):

    image_path = product_data['image']
    with open(image_path, 'rb') as image_file:
        bot.send_photo(message.chat.id, image_file)

    text_message = f"<b>Name:</b> {product_data['name']}\n"
    text_message += f"<b>Description:</b> {product_data['description']}\n"
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Нравится', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Не нравится', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.chat.id, text_message, parse_mode="HTML", reply_markup=keyboard)
if __name__ == '__main__':
    bot.polling()