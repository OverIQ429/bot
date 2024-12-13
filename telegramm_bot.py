import random
import json
import os
from random import randint
import requests
import numpy as np
from telebot import types
import telebot
from collections import defaultdict
class UserPreference():
    def __init__(self, user_id, items, epsilon=1):
        self.user_id = user_id
        self.items = items # Список всех категорий
        self.epsilon = epsilon
        self.forspocen = items["categories"]
        self.counts = self._initialize_counts_and_likes()
        self.likes = self._initialize_counts_and_likes()
        self.liked_catecorian = []
        self.cock = None
        self.new_id = None
    def _initialize_counts_and_likes(self):
        """Инициализирует словари self.counts и self.likes с нулевыми значениями."""

        counts_and_likes = defaultdict(int)  # Используем defaultdict
        # Важно: теперь items["categories"] - это список, поэтому итерируемся по элементам списка.
        for category in self.items.get("categories", []):
            # Проверка, чтобы избежать ошибок, если "items" не существует или не список
            item_id = category["id"]
            counts_and_likes[item_id] = 0
        return counts_and_likes

    def choose_item(self):
        choise_category = self.items["categories"]
        self.cock = choise_category
        if random.random() < self.epsilon:
            item_id = np.random.choice(list(choise_category))
            for el in range(len(choise_category)):
                if item_id["id"] == choise_category[el]["id"]:
                    value = el
            return item_id["id"], choise_category[value]["id"]  # Возвращаем ID и название товара

        else:
            print(self.items)
            avg_likes = {item_id: self.likes[item_id] / self.counts[item_id] if self.counts[item_id] > 0 else 0 for item_id in self.items}
            if all(value == 0 for value in avg_likes.values()):
                item_id = np.random.choice(list(choise_category))
                print(item_id)
                return item_id["id"], choise_category[int(item_id["id"])-1]

            # Используем Softmax для выбора товара
            probs = np.exp(np.array(list(avg_likes.values())))
            probs /= np.sum(probs)
            item_id = np.random.choice(list(choise_category), p=probs)
            print(item_id)
            return item_id["id"], choise_category[int(item_id["id"])-1]

    def update(self, item_id, liked):
        for el in range(len(self.cock)):
            if item_id[0] == self.cock[el]["id"]:
                value = el
                print(value, item_id[0])
        self.counts[value] += 1
        if liked == "yes":
            self.likes[value] += 1
            name = self.cock[value]["name"]
            self.liked_catecorian.append(name)
            if len(self.liked_catecorian) == 2:
                new_url = "http://176.108.253.3:8080/suggest?category1='{}'&category2='{}'".format(self.liked_catecorian[0], self.liked_catecorian[1])
                Govno = requests.get(new_url)
                if Govno.status_code == 200:
                    ids = Govno.json()
                    self.new_id =ids["id"]
                    print(self.new_id)
        if liked == "no":
            self.new_id = None
            self.liked_catecorian = []





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
        return cls(data['user_id'], dict(data['items']), epsilon=data['epsilon']), data['counts'], data['likes']

bot = telebot.TeleBot('8117985808:AAEPmdm94_aAXIkQ7EY3A96HtDX1JD6cuyc')
global user_id
global filename

url = f'http://176.108.253.3:8080/categories'
r = requests.get(url)

if r.status_code == 200:
    categoory = r.json()
current_product_index = 0

@bot.message_handler(commands=['start'])
def handle_start(message):
    global current_product_index
    global user_pref
    print(len(categoory))
    user_id = message.from_user.id
    filename = f"user_preferences_{user_id}.json"
    rand_int = randint(1, 3)
    global current_product_index
    product_id, product_data = list(categoory.items())[0]
    if UserPreference.load(filename):
        user_pref, counts, likes = UserPreference.load(filename)
        user_pref.counts = counts
        user_pref.likes = likes
        print("Данные пользователя загружены.")
    else:
        print(user_id)
        print("Файл с данными пользователя не найден. Создаем новый профиль.")
        user_pref = UserPreference(user_id, categoory)
    print(user_pref)
    print(product_data)
    show_product(message, product_data[rand_int])

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    global user_pref
    recommended_category = user_pref.choose_item()
    #recommended_item = recommended_category[1][rand_int]
    user_pref.update(recommended_category, call.data)
    if user_pref.new_id is not None:
        recommended_category = (user_pref.new_id, user_pref.new_id)
    #global current_product_index
    #current_product_index = randint()
    user_id = call.from_user.id
    filename = f"user_preferences_{user_id}.json"
    user_pref.save(filename)
    categoory_without_c = categoory["categories"]
    for el in range(len(categoory_without_c)):
        if recommended_category[0] == categoory_without_c[el]["id"]:
            value = el
    print(recommended_category[0])
    result = categoory_without_c[value]
    show_product(call.message, result)

def show_product(message, product_data):
    new_items = product_data["id"]
    item_url = "http://176.108.253.3:8080/product?category_id={}".format(new_items)
    I = requests.get(item_url)
    if I.status_code == 200:
        Item_dict = I.json()
    len_value = Item_dict["products"]
    value = len(len_value)
    if value ==0:
        print("Чё за хуйня, категория без вещей")
    choisen_item = randint(0, value-1)
    product = len_value[choisen_item]
    image_path = product["image_link"]
    bot.send_photo(message.chat.id, image_path)

    text_message = f"<b>Name:</b> {product['name']}\n"
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Нравится', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Не нравится', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(message.chat.id, text_message, parse_mode="HTML", reply_markup=keyboard)
if __name__ == '__main__':
    bot.polling()