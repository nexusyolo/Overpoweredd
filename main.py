import discord
import asyncio
import os
import random
import aiohttp
import datetime
import json
import logging
from discord.ext import commands
from keep_alive import keep_alive

# Set up logging
logging.basicConfig(level=logging.ERROR, filename="bot_errors.log")

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intents if required

bot = commands.Bot(command_prefix='!', intents=intents)

# Persistent storage for first startup
FIRST_STARTUP_FILE = 'first_startup.json'


def is_first_startup():
    """Check if it's the bot's first startup and update persistent file."""
    try:
        with open(FIRST_STARTUP_FILE, 'r') as f:
            data = json.load(f)
            return data.get('first_startup', True)
    except FileNotFoundError:
        return True


def set_first_startup():
    """Set the bot's first startup flag to False after the first launch."""
    with open(FIRST_STARTUP_FILE, 'w') as f:
        json.dump({"first_startup": False}, f)


@bot.event
async def on_ready():
    if bot.user:
        print(f'Logged in as {bot.user.name} ({bot.user.id})')
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name="!help | Type me a command!")
        )

        if is_first_startup():
            # Announce that the bot is back online in each server
            for guild in bot.guilds:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        embed = discord.Embed(
                            title="🟢 Bot is Back Online!",
                            description="I'm back up and running! Sorry for any downtime.",
                            color=0x00ff00
                        )
                        await channel.send(embed=embed)
                        break  # Only send to one channel per server

            # Mark the bot as no longer first startup
            set_first_startup()


@commands.is_owner()  # Only the bot owner can use this
@bot.command()
async def shutdown(ctx):
    embed = discord.Embed(
        title="🔴 Bot is Going Down!",
        description="I'm shutting down for maintenance or due to an update/error. See you soon!",
        color=0xff0000
    )

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    await channel.send(embed=embed)
                    break  # Only send to one channel per server
                except Exception as e:
                    print(f"Failed to send in {channel.name}: {e}")

    await ctx.send("Shutting down now...")
    await bot.close()  # Properly closes the bot


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
        "My sources say no", "My sources say no", "Outlook not so good", "Very doubtful"
    ]
    await ctx.send(f'🎱 {random.choice(responses)}')


@bot.command(name='status')
async def status(ctx):
    """Check if the bot is online and responding"""
    uptime = datetime.datetime.now(datetime.timezone.utc) - bot.user.created_at if bot.user else None
    if not bot.user:
        await ctx.send("❌ Bot is not fully initialized yet.")
        return
    embed = discord.Embed(
        title="🟢 Bot Status",
        description="I'm online and running perfectly!",
        color=0x00ff00
    )
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
    if uptime:
        embed.add_field(name="Account Age", value=f"{uptime.days} days", inline=True)
    await ctx.send(embed=embed)


@bot.command(name='announce')
async def announce_online(ctx):
    """Manually announce that the bot is online (private message)"""
    embed = discord.Embed(
        title="📢 Bot Status Announcement",
        description="I'm online and ready to serve!",
        color=0x00ff00
    )
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Status", value="🟢 Online", inline=True)

    try:
        await ctx.author.send(embed=embed)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
    except discord.Forbidden:
        msg = await ctx.send("❌ I couldn't send you a DM! Please check your privacy settings.")
        await asyncio.sleep(5)
        await msg.delete()

@bot.command(name='version')
async def version(ctx):
    """Displays detailed bot version and information."""
    embed = discord.Embed(
        title="🤖 Bot Version Info",
        description="Overpowered Productions Discord Bot",
        color=0x9932cc
    )

    embed.add_field(name="📋 Version", value="1.3.0", inline=True)
    embed.add_field(name="🐍 Python", value="3.11+", inline=True)
    embed.add_field(name="📚 Discord.py", value="2.5.2+", inline=True)

    embed.add_field(name="👨‍💻 Developer", value="n3x_us", inline=True)
    embed.add_field(name="🏢 Organization", value="Overpowered Productions", inline=True)
    embed.add_field(name="📅 Last Updated", value="29th May 2025", inline=True)

    embed.add_field(
        name="🚀 Features",
        value="• Discord Commands\n• Roblox Integration\n• 24/7 Uptime\n• Auto-announcements",
        inline=False
    )

    embed.set_footer(text="Type !updates to see the full changelog!")
    await ctx.send(embed=embed)

@bot.command(name='updates')
async def bot_updates(ctx):
    """Shows the latest bot updates and changelog"""
    embed = discord.Embed(
        title="🔄 Bot Updates & Changelog",
        description="Here are the latest updates to Overpowered Productions Bot!",
        color=0x7289da
    )

    embed.add_field(
        name="📅 Version 1.4.0 - Upcoming Update",
        value="🔧 **Fixed Issues:**\n"
              "• Removed the syntax error on line 218.\n"
              "• Improved error handling and user input validation.\n\n"
              "✨ **Bloxlink-style Enhancements:**\n"
              "• Added loading message while searching for users.\n"
              "• Included detailed user information including friends count and badges.\n"
              "• Formatted creation date calculation with a 'days ago' display.\n"
              "• Cleaner embed design with proper formatting.\n"
              "• High-resolution avatar thumbnails and links to profile and avatar pages.\n"
              "• Professional footer with verifier information.\n"
              "• Enhanced error messages with helpful suggestions.\n\n"
              "🎮 **New Features:**\n"
              "• Shows account age in days.\n"
              "• Displays friends and badges count.\n"
              "• Better bio formatting with code blocks.\n"
              "• Visual design improvements that match Bloxlink's style.\n"
              "• Timeout handling for slow API responses.",
        inline=False
    )

    embed.add_field(
        name="📅 Version 1.3.0 - Latest Update",
        value="🆕 **New Features:**\n"
              "• Added `!robloxverify` command with full user verification\n"
              "• Bot now shows user avatars and profile links\n"
              "• Enhanced error handling for Roblox API\n"
              "• Added user creation date and bio display",
        inline=False
    )

    embed.add_field(
        name="📅 Version 1.2.0",
        value="🔧 **Improvements:**\n"
              "• Custom embedded help command\n"
              "• Private `!announce` command (DM only)\n"
              "• Auto-announcement when bot comes back online\n"
              "• Better command organization in help menu",
        inline=False
    )

    embed.add_field(
        name="📅 Version 1.1.0",
        value="🎮 **Features Added:**\n"
              "• `!8ball` magic 8-ball command\n"
              "• `!roll` dice rolling with custom sides\n"
              "• `!status` bot health checker\n"
              "• Enhanced bot presence with activity status",
        inline=False
    )

    embed.add_field(
        name="📅 Version 1.0.0 - Initial Release",
        value="🚀 **Core Features:**\n"
              "• Basic `!hello` and `!ping` commands\n"
              "• Keep-alive system for 24/7 uptime\n"
              "• Discord bot foundation established\n"
              "• Custom command prefix (!)",
        inline=False
    )

    embed.add_field(
        name="🔮 Coming Soon",
        value="• More Roblox integration features\n• Fun mini-games\n• Server moderation tools\n• Custom user profiles",
        inline=False
    )

    embed.set_footer(text="Made by Overpowered Productions! | Stay tuned for more updates!")
    await ctx.send(embed=embed)

# Custom Help Command
bot.remove_command('help')
@bot.command(name='help')
async def help_command(ctx):
    """Shows all available commands"""
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="Here are all the commands you can use:",
        color=0x3498db
    )

    embed.add_field(
        name="👋 Basic Commands",
        value="`!hello` - Say hello\n`!ping` - Check bot latency",
        inline=False
    )

    embed.add_field(
        name="🎮 Fun Commands", 
        value="`!roll [sides]` - Roll a dice (default 6 sides)\n**Example:** `!roll 20`\n`!8ball <question>` - Ask the magic 8-ball\n**Example:** `!8ball Will I win the lottery?`",
        inline=False
    )

    embed.add_field(
        name="⚙️ Utility Commands",
        value="`!status` - Check bot status\n`!announce` - Announce bot is online\n`!robloxverify <username>` - Verify a Roblox user\n`!updates` - View bot updates\n`!version` - Show bot version\n`!help` - Show this help menu",
        inline=False
    )

    embed.set_footer(text="Made by Overpowered Productions! | Use ! before each command")
    await ctx.send(embed=embed)


# General Error Handler
@bot.event
async def on_command_error(ctx, error):
    """Global error handler to prevent bot crashes"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Invalid argument provided: {error}")
    else:
        await ctx.send("❌ An unexpected error occurred. Please try again later.")
        logging.error(f"Unhandled error in command {ctx.command}: {error}")


# Roblox Verification Command
@bot.command(name='robloxverify')
async def roblox_verify(ctx, username: str):
    """Verifies a Roblox user and fetches their profile data."""
    await ctx.trigger_typing()

    base_url = f"https://users.roblox.com/v1/users/search?keyword={username}"

    try:
        # Fetch user data from the Roblox API
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as response:
                if response.status == 200:
                    data = await response.json()

                    if len(data['data']) == 0:
                        await ctx.send(f"⚠️ No user found with the username: {username}")
                    else:
                        user_data = data['data'][0]  # Get the first result
                        user_id = user_data['id']
                        user_name = user_data['name']
                        user_creation_date = user_data['created']
                        user_avatar_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png"

                        # Send a detailed embed
                        embed = discord.Embed(
                            title=f"✅ {user_name}'s Roblox Profile",
                            color=0x00ff00
                        )
                        embed.add_field(name="User ID", value=user_id, inline=False)
                        embed.add_field(name="Username", value=user_name, inline=False)
                        embed.add_field(name="Creation Date", value=user_creation_date, inline=False)
                        embed.set_thumbnail(url=user_avatar_url)
                        embed.set_footer(text="Roblox Profile Verification")

                        await ctx.send(embed=embed)
                else:
                    await ctx.send(f"⚠️ Roblox API returned an error (status code: {response.status}). Please try again later.")
    except Exception as e:
        await ctx.send(f"⚠️ An error occurred while fetching data: {str(e)}")
        logging.error(f"Error in roblox_verify command: {e}")
# Start the bot
keep_alive()  # Keeps the bot alive if using services like Replit
bot.run(os.getenv("DISCORD_TOKEN"))  # Use environment variable for the token