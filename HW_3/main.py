from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
import asyncio, logging
from config import token

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=token)
dp = Dispatcher()


products = {
    "aвтозапчасти": [
        {"name": "фильтр", "price": "1000сом"},
        {"name": "Двери", "price": "5000сом"},
        {"name": "Лобовое окно", "price": "3000сом"},
        {"name": "Боковое зеркало", "price": "500сом"},
        {"name": "Бампер", "price": "8000сом"}
    ],
    "косметика": [
        {"name": "Помада", "price": "500 ₽"},
        {"name": "Тушь", "price": "700 ₽"},
        {"name": "Тональный крем", "price": "1500 ₽"}
    ],
    "мобильные запчасти": [
        {"name": "Экран", "price": "1500 сом"},
        {"name": "Аккумулятор", "price": "800 сом"},
        {"name": "Зарядное устройство", "price": "200 сом"}
    ]
}


@dp.message(Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()

    for category in products:
        builder.button(
            text=category,
            callback_data=f"category_{category.lower().replace(' ', '_')}"
        )
    builder.adjust(1)

    await message.answer("Добро пожаловать в магазин автозапчастей и косметики! Выберите категорию:", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("category_"))
async def category_selected(callback_query: types.CallbackQuery):
    category = callback_query.data.split("_")[1]
    builder = InlineKeyboardBuilder()

    if category not in products:
        await callback_query.answer("Категория не найдена")
        return
    
    for product in products.get(category, []):
        builder.add(InlineKeyboardButton(f"{product['name']} - {product['price']}", 
                                        callback_data=f"product_{category.lower().replace(' ', '_')}_{product['name'].lower().replace(' ', '_')}"))

    markup = builder.as_markup()

    await bot.send_message(callback_query.from_user.id, f"Выберите товар из категории {category}:", reply_markup=markup)
    await callback_query.answer()


@dp.callback_query(F.data.startswith("product_"))
async def product_selected(callback_query: types.CallbackQuery):
    logging.debug(f"callback_data: {callback_query.data}")
    data = callback_query.data.split("_")
    category = ' '.join(data[1:-1]).replace('_', ' ')  
    product_name = data[-1].replace('_', ' ')  

    selected_product = next((p for p in products.get(category.lower(), []) if p['name'].lower() == product_name.lower()), None)

    if selected_product:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton("Подтвердить товар", callback_data=f"confirm_{category.lower().replace(' ', '_')}_{product_name.lower().replace(' ', '_')}"))
        builder.add(InlineKeyboardButton("Отменить товар", callback_data="cancel"))

        markup = builder.as_markup()

        await bot.send_message(
            callback_query.from_user.id,
            f"Вы выбрали товар: {selected_product['name']}\nЦена: {selected_product['price']}",
            reply_markup=markup
        )
    else:
        await bot.send_message(callback_query.from_user.id, "Товар не найден.")
    await callback_query.answer()


@dp.callback_query(F.data.startswith("confirm_"))
async def confirm_product(callback_query: types.CallbackQuery):
    data = callback_query.data.split("_")
    category = ' '.join(data[1:-1]).replace('_', ' ')  
    product_name = data[-1].replace('_', ' ')  

    selected_product = next((p for p in products.get(category.lower(), []) if p['name'].lower() == product_name.lower()), None)

    if selected_product:
        await bot.send_message(callback_query.from_user.id, f"Ваш выбор подтвержден: {selected_product['name']} - {selected_product['price']}")
    else:
        await bot.send_message(callback_query.from_user.id, "Ошибка при подтверждении товара.")
    await callback_query.answer()


@dp.callback_query(F('cancel'))
async def cancel_product(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Вы отменили выбор товара.")
    await callback_query.answer()


async def main():
    await dp.start_polling(bot)

asyncio.run(main())
