import discord
from discord.ext import commands

# Set up the bot intents (this is required for reading messages)
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance with command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Event that runs when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# A simple ping command
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# A simple hello command
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}!")

# Run the bot with your token
bot.run('YOUR_BOT_TOKEN')
