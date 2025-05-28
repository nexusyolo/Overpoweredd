import discord
from discord.ext import commands
import random
import os
from keep_alive import keep_alive  # Import the keep_alive function

# Setup intents and bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    if bot.user:
        print(f'Logged in as {bot.user.name} ({bot.user.id})')
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name="!help | Type me a command!")
        )

# Command definitions here...

# Run the bot
token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
    print("Please add your Discord bot token to the Secrets tab.")
else:
    keep_alive()  # Start the keep-alive server before running the bot
    bot.run(token)
