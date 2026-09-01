from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import database as db
import ocr_handler as ocr
import logging

TOKEN = "8677054038:AAEQVHc6fwxcL5X1xZHRgDW-SAHc_GzEb88"

# دستور استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ ثبت هزینه", callback_data='add_expense')],
        [InlineKeyboardButton("📈 ثبت درآمد", callback_data='add_income')],
        [InlineKeyboardButton("📊 گزارش ماهانه", callback_data='report')],
        [InlineKeyboardButton("📸 اسکن فاکتور", callback_data='scan_bill')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! به دستیار مالی خوش اومدی. یکی از گزینه‌ها رو انتخاب کن:", reply_markup=reply_markup)

# پردازش دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'add_expense':
        await query.edit_message_text("مبلغ هزینه رو به تومان وارد کن (مثلاً ۲۵۰۰۰۰):")
        context.user_data['state'] = 'waiting_expense_amount'
    elif query.data == 'scan_bill':
        await query.edit_message_text("لطفاً از فاکتور یا قبض خود عکس بگیر و بفرست:")
        context.user_data['state'] = 'waiting_photo'

# دریافت عکس و OCR
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') == 'waiting_photo':
        photo_file = await update.message.photo[-1].get_file()
        file_bytes = await photo_file.download_as_bytearray()
        
        amount = ocr.extract_amount_from_image(file_bytes)
        if amount:
            db.add_transaction(update.effective_user.id, amount, "متفرقه", "تشخیص خودکار از فاکتور", "expense")
            await update.message.reply_text(f"✅ مبلغ {amount:,} تومان از روی فاکتور خونده شد و به هزینه‌ها اضافه شد.")
        else:
            await update.message.reply_text("❌ نتونستم مبلغ رو تشخیص بدم. لطفاً دستی وارد کن.")
        context.user_data['state'] = None

# گوش دادن به پیام‌های متنی برای ثبت دستی
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') == 'waiting_expense_amount':
        try:
            amount = int(update.message.text.replace(',', ''))
            db.add_transaction(update.effective_user.id, amount, "عمومی", "ثبت دستی", "expense")
            await update.message.reply_text(f"💰 هزینه‌ی {amount:,} تومانی ثبت شد.")
            context.user_data['state'] = None
        except:
            await update.message.reply_text("عدد رو درست وارد کن!")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("ربات روشن شد...")
    app.run_polling()

if __name__ == '__main__':
    main()
