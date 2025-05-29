import discord
import asyncio
import os
import random
import aiohttp
import datetime # Import the datetime module
from discord.ext import commands
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

    # Send as a direct message to the user
    try:
        await ctx.author.send(embed=embed)
        # Delete the original command message if possible
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass  # Bot doesn't have permission to delete messages
    except discord.Forbidden:
        # If DM fails, send a temporary message in the channel
        msg = await ctx.send("❌ I couldn't send you a DM! Please check your privacy settings.")
        await asyncio.sleep(5)
        await msg.delete()

# Remove the default help command to replace it with our custom one
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
        value="`!roll [sides]` - Roll a dice (default 6 sides)\n`!8ball <question>` - Ask the magic 8-ball",
        inline=False
    )

    embed.add_field(
        name="⚙️ Utility Commands",
        value="`!status` - Check bot status\n`!announce` - Announce bot is online\n`!robloxverify <username>` - Verify a Roblox user\n`!updates` - View bot updates\n`!version` - Show bot version\n`!help` - Show this help menu",
        inline=False
    )

    embed.set_footer(text="Made by Overpowered Productions! | Use ! before each command")
    await ctx.send(embed=embed)

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
        print(f"Unhandled error: {error}")

@bot.command(name='robloxverify')
async def roblox_verify(ctx, *, username: str):
    """Verify a Roblox username and get user information"""
    try:
        timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
        if username:
            # Search for the username to get the exact user ID and username
            # URL encode the username to handle special characters properly (like spaces)
            from urllib.parse import quote
            search_url = f"https://users.roblox.com/v1/users/search?keyword={quote(username)}&limit=1"
            async with session.get(search_url) as response:
                if response.status != 200:
                    await ctx.send(f"❌ Error searching for user (Status: {response.status})")
                    return
                search_data = await response.json()
                
                if not search_data.get('data') or len(search_data['data']) == 0:
                    await ctx.send(f"❌ No user found with username: {username}")
                    return
                
                user_id = search_data['data'][0]['id']
                exact_username = search_data['data'][0]['name']
                display_name = search_data['data'][0]['displayName']
                
                # Get detailed user information
                user_url = f"https://users.roblox.com/v1/users/{user_id}"
                async with session.get(user_url) as response:
                    if response.status != 200:
                        await ctx.send(f"❌ Error getting user details (Status: {response.status})")
                        return
                    
                    user_data = await response.json()

                    # Create verification embed
                    embed = discord.Embed(
                        title="🎮 Roblox User Verified!",
                        description=f"Successfully found Roblox user: **{exact_username}**",
                        color=0x00b2ff
                    )
                    
                    embed.add_field(name="👤 Username", value=exact_username, inline=True)
                    embed.add_field(name="✨ Display Name", value=display_name, inline=True)
                    embed.add_field(name="🆔 User ID", value=user_id, inline=True)
                    
                    if user_data.get('description'):
                        embed.add_field(name="📝 Bio", value=user_data['description'][:100] + "..." if len(user_data['description']) > 100 else user_data['description'], inline=False)
                    
                    embed.add_field(name="📅 Created", value=user_data.get('created', 'Unknown')[:10], inline=True)
                    embed.add_field(name="🔗 Profile", value=f"[View Profile](https://www.roblox.com/users/{user_id}/profile)", inline=True)
                    
                    avatar_url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=150x150&format=Png&isCircular=false"
                    async with session.get(avatar_url) as avatar_response:
                        if avatar_response.status == 200:
                            avatar_data = await avatar_response.json()
                            if avatar_data.get('data') and avatar_data['data']:
                                embed.set_thumbnail(url=avatar_data['data'][0]['imageUrl'])

                            embed.set_footer(text=f"Verified by {ctx.author.display_name}")
                    await ctx.send(embed=embed)
        else:  # If username is not provided or invalid format is provided then show error message and return the error message from the API to the user for debugging purposes if needed (like if the API is down or the user is not found)
            await ctx.send("❌ Please enter a username to verify.")
            return
    except Exception as e:
        await ctx.send("❌ An error occurred while verifying the Roblox user. Please try again later.")
        print(f"Roblox verify error: {e}")
            
@bot.command(name='updates')
async def bot_updates(ctx):
    """Shows the latest bot updates and changelog"""
    embed = discord.Embed(
        title="🔄 Bot Updates & Changelog",
        description="Here are the latest updates to Overpowered Productions Bot!",
        color=0x7289da
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

@bot.command(name='version')
async def version_command(ctx):
    """Shows the current bot version and information"""
    embed = discord.Embed(
        title="🤖 Bot Version Info",
        description="Overpowered Productions Discord Bot",
        color=0x9932cc
    )
    
    embed.add_field(name="📋 Version", value="1.3.0", inline=True)
    embed.add_field(name="🐍 Python", value="3.11+", inline=True)
    embed.add_field(name="📚 Discord.py", value="2.5.2+", inline=True)

    embed.add_field(name="👨‍💻 Developer", value="ScriptNex", inline=True)
    embed.add_field(name="🏢 Organization", value="Overpowered Productions", inline=True)
    embed.add_field(name="📅 Last Updated", value="May 2025", inline=True)

    embed.add_field(
        name="🚀 Features",
        value="• Discord Commands\n• Roblox Integration\n• 24/7 Uptime\n• Auto-announcements",
        inline=False
    )
    
    embed.set_footer(text="Type !updates to see the full changelog!")
    await ctx.send(embed=embed)

# Get token from environment variables
token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
    print("Please add your Discord bot token to the Secrets tab.")
else:
    keep_alive()  # Start the keep-alive server before running the bot

    bot.run(token)