import telegrambot
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer

# Initialize the Solana client and Telegram bot
SOLANA_RPC_URL = “https://api.testnet.solana.com"
solana_client = Client(https://api.testnet.solana.com)
bot = telebot.TeleBot("8042143084:AAGh5wnIYob_YgeIxOozqEgZ6EEJCRUM8eA")

# Dictionary to hold user wallets
user_wallets = {}

# Function to create a wallet for a user
def create_wallet():
    new_wallet = Keypair()
    return new_wallet.public_key, new_wallet.secret_key

# Command to create a new wallet for the user
@bot.message_handler(commands=['create_wallet'])
def create_user_wallet(message):
    user_id = message.from_user.id
    public_key, secret_key = create_wallet()
    
    user_wallets[user_id] = {
        'public_key': str(public_key),
        'secret_key': secret_key,
        'balance': 0
    }
    
    bot.reply_to(message, f"New wallet created!\nPublic Key: {public_key}\nKeep your secret key safe!")

# Function to get balance of user's wallet
def get_balance(public_key):
    balance = solana_client.get_balance(public_key)
    return balance['result']['value'] / 10**9  # Convert from lamports to SOL

# Command to check balance
@bot.message_handler(commands=['balance'])
def check_balance(message):
    user_id = message.from_user.id
    if user_id in user_wallets:
        public_key = user_wallets[user_id]['public_key']
        balance = get_balance(public_key)
        bot.reply_to(message, f"Your wallet balance: {balance:.4f} SOL")
    else:
        bot.reply_to(message, "No wallet found for you. Use /create_wallet to generate one.")

# Function to send SOL
def send_sol(sender_secret_key, recipient_pub_key, amount):
    sender_wallet = Keypair.from_secret_key(sender_secret_key)
    txn = Transaction().add(
        transfer(TransferParams(
            from_pubkey=sender_wallet.public_key,
            to_pubkey=recipient_pub_key,
            lamports=int(amount * 10**9)  # Convert SOL to lamports
        ))
    )
    response = solana_client.send_transaction(txn, sender_wallet)
    return response

# Command to send SOL to another wallet
@bot.message_handler(commands=['send_sol'])
def send_sol_command(message):
    user_id = message.from_user.id
    if user_id in user_wallets:
        try:
            params = message.text.split()
            recipient = params[1]
            amount = float(params[2])
            sender_secret_key = user_wallets[user_id]['secret_key']

            result = send_sol(sender_secret_key, recipient, amount)
            bot.reply_to(message, f"Transaction sent! Txn ID: {result['result']}")
        except Exception as e:
            bot.reply_to(message, f"Error: {str(e)}")
    else:
        bot.reply_to(message, "You need to create a wallet first using /create_wallet.")

# Start the bot
bot.polling()
