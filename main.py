import discord
import asyncio
import os
from discord.ext import commands
import random
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intents if required

bot = commands.Bot(command_prefix='!', intents=intents)

# Store if this is the first startup
first_startup = True

@bot.event
async def on_ready():
    global first_startup
    if bot.user:
        print(f'Logged in as {bot.user.name} ({bot.user.id})')
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name="!help | Type me a command!")
        )
        
        # If this isn't the first startup, announce that bot is back up
        if not first_startup:
            for guild in bot.guilds:
                # Find the first text channel the bot can send messages in
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        embed = discord.Embed(
                            title="🟢 Bot is Back Online!",
                            description="I'm back up and running! Sorry for any downtime.",
                            color=0x00ff00
                        )
                        await channel.send(embed=embed)
                        break  # Only send to one channel per server
        
        first_startup = False

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

@bot.command(name='status')
async def status(ctx):
    """Check if the bot is online and responding"""
    uptime = discord.utils.utcnow() - bot.user.created_at if bot.user else None
    embed = discord.Embed(
        title="🟢 Bot Status",
        description="I'm online and running perfectly!",
        color=0x00ff00
    )
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    if uptime:
        embed.add_field(name="Account Age", value=f"{uptime.days} days", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='announce')
async def announce_online(ctx):
    """Manually announce that the bot is online"""
    embed = discord.Embed(
        title="📢 Bot Status Announcement",
        description="I'm online and ready to serve!",
        color=0x00ff00
    )
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Status", value="🟢 Online", inline=True)
    await ctx.send(embed=embed)

# Get token from environment variables
token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
    print("Please add your Discord bot token to the Secrets tab.")
else:
    keep_alive()  # Start the keep-alive server before running the bot

    bot.run(token)