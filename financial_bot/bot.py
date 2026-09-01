import database as db
import ocr_handler as ocr
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv('TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ ثبت هزینه", callback_data='add_expense')],
        [InlineKeyboardButton("📈 ثبت درآمد", callback_data='add_income')],
        [InlineKeyboardButton("📊 گزارش ماهانه", callback_data='report')],
        [InlineKeyboardButton("📸 اسکن فاکتور", callback_data='scan_bill')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! به دستیار مالی خوش اومدی. یکی از گزینه‌ها رو انتخاب کن:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'add_expense':
        await query.edit_message_text("مبلغ هزینه رو به تومان وارد کن (مثلاً ۲۵۰۰۰۰):")
        context.user_data['state'] = 'waiting_expense_amount'
    
    elif query.data == 'add_income':
        await query.edit_message_text("مبلغ درآمد رو به تومان وارد کن:")
        context.user_data['state'] = 'waiting_income_amount'
    
    elif query.data == 'report':
        user_id = update.effective_user.id
        total_income, total_expense = db.get_monthly_summary(user_id)
        balance = total_income - total_expense
        await query.edit_message_text(
            f"📊 گزارش ماهانه:\n"
            f"💰 درآمد: {total_income:,} تومان\n"
            f"💸 هزینه: {total_expense:,} تومان\n"
            f"📌 مانده: {balance:,} تومان"
        )
    
    elif query.data == 'scan_bill':
        await query.edit_message_text("لطفاً از فاکتور یا قبض خود عکس بفرست:")
        context.user_data['state'] = 'waiting_photo'

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    state = context.user_data.get('state')
    
    if state == 'waiting_expense_amount':
        try:
            amount = int(text.replace(',', ''))
            db.add_transaction(user_id, amount, "عمومی", "ثبت دستی", "expense")
            await update.message.reply_text(f"✅ هزینه {amount:,} تومانی ثبت شد.")
            context.user_data['state'] = None
        except ValueError:
            await update.message.reply_text("❌ عدد رو درست وارد کن!")
    
    elif state == 'waiting_income_amount':
        try:
            amount = int(text.replace(',', ''))
            db.add_transaction(user_id, amount, "عمومی", "ثبت دستی", "income")
            await update.message.reply_text(f"✅ درآمد {amount:,} تومانی ثبت شد.")
            context.user_data['state'] = None
        except ValueError:
            await update.message.reply_text("❌ عدد رو درست وارد کن!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') == 'waiting_photo':
        photo_file = await update.message.photo[-1].get_file()
        file_bytes = await photo_file.download_as_bytearray()
        
        amount = ocr.extract_amount_from_image(file_bytes)
        if amount:
            db.add_transaction(update.effective_user.id, amount, "فاکتور", "تشخیص خودکار", "expense")
            await update.message.reply_text(f"✅ مبلغ {amount:,} تومان از روی فاکتور خونده شد و ثبت شد.")
        else:
            await update.message.reply_text("❌ نتونستم مبلغ رو تشخیص بدم. لطفاً دستی وارد کن.")
        context.user_data['state'] = None

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("ربات روشن شد...")
    import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_server():
    port = int(os.getenv('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

# توی تابع main، قبل از app.run_polling():
threading.Thread(target=run_health_server, daemon=True).start()
    app.run_polling()

if __name__ == '__main__':
    main()
