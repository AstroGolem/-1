import telebot
from telebot import types
import re

# ВСТАВЬ СВОЙ АКТУАЛЬНЫЙ ТОКЕН
bot = telebot.TeleBot("8683246282:AAHtP0nCHy4Uq7TYkJq6xyRRMXw0EOHvr48")

# ID твоей группы
GROUP_ID = -5562252323

# Список ID админов (чтобы бот не пересылал им сообщения)
ADMIN_ID = [5389430769]

# ==========================================
# 1. КОМАНДА /start (InLine кнопки)
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):
    # Создаем INLINE клавиатуру (внутри сообщения)
    markup = types.InlineKeyboardMarkup(row_width=1) 
    
    # Создаем кнопки
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
    # Убираем "часики" с кнопки у пользователя
    bot.answer_callback_query(call.id)
    
    chosen_category = ""
    
    # Определяем, какую кнопку нажали
    if call.data == 'support':
        chosen_category = "🆘 Поддержка"
    elif call.data == 'chat':
        chosen_category = "💬 Общение"
    elif call.data == 'universal':
        chosen_category = "⚖️ Универсал"
    
    if chosen_category:
        # Отвечаем пользователю
        bot.send_message(
            call.message.chat.id, 
            f"Ты выбрал: {chosen_category}. Напиши свой вопрос, и админ ответит."
        )
        
        # Уведомляем группу
        bot.send_message(
            GROUP_ID, 
            f"Юзер @{call.from_user.username} (ID: {call.from_user.id}) выбрал категорию: {chosen_category}"
        )

# ==========================================
# 3. ПЕРЕСЫЛКА СООБЩЕНИЙ В ГРУППУ
# ==========================================
@bot.message_handler(func=lambda message: message.chat.id != GROUP_ID)
def forward_to_admin(message):
    text_to_send = message.text if message.text else "[Вложение]"
    
    # Отправляем в группу со скрытой меткой [ID:число]
    bot.send_message(
        GROUP_ID, 
        f"💬 Сообщение от @{message.from_user.username}:\n\n{text_to_send}\n\n[ID:{message.from_user.id}]"
    )

# ==========================================
# 4. ОТВЕТ АДМИНА ИЗ ГРУППЫ
# ==========================================
@bot.message_handler(func=lambda message: message.chat.id == GROUP_ID and message.reply_to_message is not None)
def reply_from_admin(message):
    # Если сообщение отправил сам бот - игнорируем
    if message.from_user.is_bot:
        return

    try:
        # Идем по цепочке сообщений наверх
        current_msg = message.reply_to_message
        target_user_id = None
        
        # Проверяем до 10 сообщений вверх по цепочке
        for _ in range(10):
            if not current_msg:
                break
                
            # Ищем скрытую метку [ID:12345678]
            if current_msg.text:
                match = re.search(r'\[ID:(\d+)\]', current_msg.text)
                if match:
                    target_user_id = int(match.group(1))
                    break
            
            # Если не нашли, идем к сообщению выше
            current_msg = current_msg.reply_to_message
            
        if target_user_id:
            # ЗАЩИТА: Если найденный ID принадлежит админу, ничего не отправляем
            if target_user_id in ADMIN_IDS:
                # Ставим реакцию, чтобы админ понял, что бот его услышал
                bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji('👀')])
                return
            
            # Отправляем ответ пользователю (если это не админ)
            bot.send_message(target_user_id, f"Админ: {message.text}")
            
            # Ставим галочку в группе, что отправлено
            bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji('✅')])
            
        else:
            bot.reply_to(message, "❌ Ошибка: не могу найти ID пользователя в этой цепочке.")
            
    except Exception as e:
        print(f"Ошибка: {e}")

print("Бот запущен...")
bot.polling(none_stop=True)
