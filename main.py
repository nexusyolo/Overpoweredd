import discord
from discord.ext import commands
import random
import os

token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
    print("Please add your Discord bot token to the Secrets tab.")
else:
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='!', intents=intents)
    bot.run(token)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Logged in as {bot.user.name} ({bot.user.id})')
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="!help | Type me a command!")
    )

# !ping command
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# !say command (repeat a message)
@bot.command()
async def say(ctx, *, message: str):
    await ctx.send(message)

# !announce command (admin only)
@bot.command()
async def announce(ctx, channel: discord.TextChannel, *, message: str):
    if ctx.author.guild_permissions.manage_channels:
        await channel.send(message)
    else:
        await ctx.send('You do not have permission to announce.')

# !question command (answer random question from choices)
@bot.command()
async def question(ctx, *, question: str):
    answers = ['Yes', 'No', 'Maybe', 'Ask again later', 'Definitely']
    random_answer = random.choice(answers)
    await ctx.send(f'Question: {question}\nAnswer: {random_answer}')

# !info command (Bot info)
@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="Bot Info",
        description="This bot was created by Overpowered Productions.",
        color=discord.Color.random()
    )
    await ctx.send(embed=embed)

# !verify command (example: this could link to a real Roblox verification system)
@bot.command()
async def verify(ctx, username: str):
    # Simulate verification logic
    await ctx.send(f"{username} has been verified!")

# Error handling for command not found
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, I don't recognize that command. Use !help to see available commands.")
    else:
        await ctx.send("An error occurred while executing the command.")