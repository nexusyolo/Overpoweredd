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

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.mention}!')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='roll')
async def roll(ctx, sides: int = 6):
    result = random.randint(1, sides)
    await ctx.send(f'🎲 You rolled a {result}!')

@bot.command(name='8ball')
async def eightball(ctx, *, question):
    responses = [
        "It is certain", "Without a doubt", "Yes definitely",
        "You may rely on it", "As I see it, yes", "Most likely",
        "Outlook good", "Yes", "Signs point to yes", "Reply hazy, try again",
        "Ask again later", "Better not tell you now", "Cannot predict now",
        "Concentrate and ask again", "Don't count on it", "My reply is no",
        "My sources say no", "Outlook not so good", "Very doubtful"
    ]
    await ctx.send(f'🎱 {random.choice(responses)}')

# Run the bot
token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
    print("Please add your Discord bot token to the Secrets tab.")
else:
    keep_alive()  # Start the keep-alive server before running the bot
    bot.run(token)
