import telebot
from telebot import types
import re
import os

# Берем токен из настроек Render (Environment Variables)
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
# Если запускаешь локально (на компе), раскомментируй строку ниже и вставь токен:
# BOT_TOKEN = "ТВОЙ_ТОКЕН"

bot = telebot.TeleBot(BOT_TOKEN)

# ID твоей группы
GROUP_ID = -5562252323

# Список ID админов (с большой буквы S в конце!)
ADMIN_IDS = [5389430769]

# ==========================================
# 1. КОМАНДА /start (InLine кнопки)
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1) 
    
    btn1 = types.InlineKeyboardButton('🆘 Поддержка', callback_data='support')
    btn2 = types.InlineKeyboardButton('💬 Общение', callback_data='chat')
    btn3 = types.InlineKeyboardButton('⚖️ Универсал', callback_data='universal')
    
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(
        message.chat.id, 
        "Привет. Выбери, с кем хочешь поговорить:", 
        reply_markup=markup
    )

# ==========================================
# 2. ОБРАБОТКА НАЖАТИЙ НА INLINE-КНОПКИ
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    bot.answer_callback_query(call.id)
    
    chosen_category = ""
    
    if call.data == 'support':
        chosen_category = "🆘 Поддержка"
    elif call.data == 'chat':
        chosen_category = "💬 Общение"
    elif call.data == 'universal':
        chosen_category = "⚖️ Универсал"
    
    if chosen_category:
        bot.send_message(
            call.message.chat.id, 
            f"Ты выбрал: {chosen_category}. Напиши свой вопрос, и админ ответит."
        )
        
        bot.send_message(
            GROUP_ID, 
            f"Юзер @{call.from_user.username} (ID: {call.from_user.id}) выбрал категорию: {chosen_category}"
        )

# ==========================================
# 3. ПЕРЕСЫЛКА СООБЩЕНИЙ В ГРУППУ
# ==========================================
# ДОБАВЛЕНА ПРОВЕРКА: бот игнорирует сообщения от админов
@bot.message_handler(func=lambda message: message.chat.id != GROUP_ID and message.from_user.id not in ADMIN_IDS)
def forward_to_admin(message):
    text_to_send = message.text if message.text else "[Вложение]"
    
    bot.send_message(
        GROUP_ID, 
        f"💬 Сообщение от @{message.from_user.username}:\n\n{text_to_send}\n\n[ID:{message.from_user.id}]"
    )

# ==========================================
# 4. ОТВЕТ АДМИНА ИЗ ГРУППЫ
# ==========================================
@bot.message_handler(func=lambda message: message.chat.id == GROUP_ID and message.reply_to_message is not None)
def reply_from_admin(message):
    if message.from_user.is_bot:
        return

    try:
        current_msg = message.reply_to_message
        target_user_id = None
        
        for _ in range(10):
            if not current_msg:
                break
                
            if current_msg.text:
                match = re.search(r'\[ID:(\d+)\]', current_msg.text)
                if match:
                    target_user_id = int(match.group(1))
                    break
            
            current_msg = current_msg.reply_to_message
            
        if target_user_id:
            # Защита: не отвечаем, если ID принадлежит админу
            if target_user_id in ADMIN_IDS:
                bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji('👀')])
                return
            
            bot.send_message(target_user_id, f"Админ: {message.text}")
            bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji('✅')])
            
        else:
            bot.reply_to(message, "❌ Ошибка: не могу найти ID пользователя в этой цепочке.")
            
    except Exception as e:
        print(f"Ошибка: {e}")

print("Бот запущен и работает на сервере...")
bot.polling(none_stop=True)
