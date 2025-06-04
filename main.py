import discord
import os
import logging

import asyncio #asyncronous sleep
import aiohttp #used for the robloxverify command

import random #used for the roll command
import datetime #used for the uptime command

from discord.ext import commands
from discord import app_commands

import signal #for the shutdown command

#CONST
TEST_GUILD_ID = 739136163255943239
BOT_PREFIX = "!"
GAME_URL = "https://www.roblox.com/games/104246316485544/Project-GTR"

HIDE_COMMANDS_RESPONSE = { #this will be used if you want to the response to be hidden
  "shutdown": True
}

#ENV
bot_token = os.environ['DISCORD_BOT_TOKEN']

#VARS:
handler_for_log = logging.FileHandler(filename='bot_errors.log', encoding='utf-8', mode='w')

startup_time = datetime.datetime.now(datetime.timezone.utc)

shutdown_flag = False


#functions
async def get_http_session(client: commands.Bot):
  session = getattr(client, "session", None)
  if session is None or session.closed:
    setattr(client, "session", aiohttp.ClientSession()) 
  return session

async def handle_shutdown(client:commands.Bot):
  global shutdown_flag
  if shutdown_flag:
      return
  print("Shutdown initiated. Sending message to all servers...")
  shutdown_flag = True
  embed = discord.Embed(
    title="🔴 Bot is Going Down!",
    description="I'm shutting down for maintenance or due to an update/error. See you soon!",
    color=0xff0000
  )

  for guild in client.guilds:
    for channel in guild.text_channels:
      if channel.permissions_for(guild.me).send_messages:
          try:
              print("SHUT DOWN MSG SENT.")
              #await channel.send(embed=embed)
              break  # Only send to one channel per server
          except Exception as e:
              print(f"Failed to send in {channel.name}: {e}")          

  session = getattr(client, "session",)
  if session and (not session.closed):
    await session.close()

  await client.close()


class Client(commands.Bot):
  def __init__(self):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    super().__init__(command_prefix=BOT_PREFIX, intents=intents)

  async def on_ready(self):
    print(f'Logged in as {self.user} (ID: {self.user})')
    await self.change_presence(activity=discord.Game(name="!help | Overpowered Productions"))
    await get_http_session(self)


  async def setup_hook(self):
    await self.tree.sync(guild=discord.Object(id=TEST_GUILD_ID))
    print(f"Synced slash commands for user {self.user}")

  async def on_disconnect(self):
    print("Bot disconnected")
    session = getattr(client, "session",)
    if session and (not session.closed):
      await session.close()
client = Client()

# [[MODERATION COMMANDS]]
# shutdown_command
@client.hybrid_command(name="shutdown", with_app_command=True, description="Shutdown the bot")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
@commands.has_permissions(administrator=True)

async def shutdown(ctx: commands.Context):
    if ctx.interaction:
        await ctx.interaction.response.send_message("Shutting down...", ephemeral=HIDE_COMMANDS_RESPONSE["shutdown"])
    else:
        await ctx.send("Shutting down...")
    await handle_shutdown(client)

# clear_command
@client.hybrid_command(name="clear", with_app_command=True, description="Clear messages")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
@commands.has_permissions(manage_messages=True)
async def clear(ctx: commands.Context, amount: int):
    if isinstance(ctx.channel, discord.TextChannel):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Cleared {amount} messages.", delete_after=5)
    else:
        await ctx.send("This command can only be used in a text channel.")


# [[BASIC COMMANDS]]
# ping_command
@client.hybrid_command(name="ping", with_app_command=True, description="Ping the bot")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
async def ping(ctx: commands.Context):
  await ctx.send(f'Pong! {round(client.latency * 1000)}ms')


# hello_command
@client.hybrid_command(name="hello", with_app_command=True, description="Say hello to the bot")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
async def hello(ctx: commands.Context):
    await ctx.send(f"Hello {ctx.author.mention}!")

# [[FUN COMMANDS]]
# roll_comand
@client.hybrid_command(name="roll", with_app_command=True, description="Roll a dice")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
async def roll(ctx: commands.Context, sides: int=6):
  result = random.randint(1, sides)
  await ctx.send(f'🎲 You rolled a {result}!')

# eight_ball_command
@client.hybrid_command(name="8ball", with_app_command=True, description="Ask the magic 8 ball a question")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
async def eight_ball(ctx: commands.Context):
  responses = [
      "It is certain", "Without a doubt", "Yes definitely",
      "You may rely on it", "As I see it, yes", "Most likely",
      "Outlook good", "Yes", "Signs point to yes", "Reply hazy, try again",
      "Ask again later", "Better not tell you now", "Cannot predict now",
      "Concentrate and ask again", "Don't count on it", "My reply is no",
      "My sources say no", "Outlook not so good", "Very doubtful"
  ]
  await ctx.send(f'🎱 {random.choice(responses)}')

# riddle_command
@client.hybrid_command(name="riddle", with_app_command=True, description="Get a riddle and try to answer it!")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
async def riddle(ctx: commands.Context):
  riddles = [
      ("I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?", "echo"),
      ("The more of this there is, the less you see. What is it?", "darkness"),
      ("What has keys but can't open locks?", "piano"),
      ("What can travel around the world while staying in the corner?", "stamp"),
      ("What has a heart that doesn’t beat?", "artichoke"),
      ("What comes once in a minute, twice in a moment, but never in a thousand years?", "the letter 'm'"),
      ("What is so fragile that saying its name breaks it?", "silence"),
      ("What can you catch, but not throw?", "cold"),
      ("What is full of holes but still holds a lot of weight?", "sieve"),
      ("I’m tall when I’m young, and I’m short when I’m old. What am I?", "candle")
  ]
  riddle, answer = random.choice(riddles)
  await ctx.reply(f"**Riddle:** {riddle}")
  def check(m):
      return m.author == ctx.author and m.channel == ctx.channel
  try:
      msg = await client.wait_for('message', check=check, timeout=60.0)
      if msg.content.lower() == answer.lower():
          await ctx.send("Correct! You got it!")
      else:
          await ctx.send(f"Sorry, the answer was: {answer}")
  except TimeoutError:
      await ctx.send(f"Sorry, you took too long. The answer was: {answer}")

# [[UTILITY COMMANDS]]
# status_command
@client.hybrid_command(name="status", with_app_command=True, description="Check the bot's status")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
async def status(ctx: commands.Context):
  account_age = datetime.datetime.now(datetime.timezone.utc) - client.user.created_at if client.user else None
  uptime = datetime.datetime.now(datetime.timezone.utc) - startup_time

  if not client.user:
    await ctx.send("❌ Bot is not fully initialized yet.")
    return
  embed = discord.Embed(
    title="🟢 Bot Status",
    description="I'm online and running perfectly!",
    color=0x00ff00
  )
  embed.add_field(name="Latency", value=f"{round(client.latency * 1000)}ms", inline=True)
  embed.add_field(name="Servers", value=str(len(client.guilds)), inline=True)
  if account_age:
    embed.add_field(name="Account Age", value=f"{account_age.days} days", inline=True)
  embed.add_field(name="Uptime", value=str(uptime).split(".")[0], inline=True)

  await ctx.send(embed=embed)

# version_command
@client.hybrid_command(name="version", with_app_command=True, description="Check the bot's version")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
async def version(ctx: commands.Context):
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

#updates_command
@client.hybrid_command(name="updates", with_app_command=True, description="Check the bot's updates")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
async def updates(ctx: commands.Context):
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

#help_command
client.remove_command("help")
@client.hybrid_command(name="help", with_app_command=True, description="you can view the help menu")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
async def help(ctx: commands.Context):
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

#announce_command
@client.hybrid_command(name="announce", with_app_command=True, description="Announce bot is online")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
async def announce(ctx: commands.Context):
  embed = discord.Embed(
    title="📢 Bot Status Announcement",
    description="I'm online and ready to serve!",
    color=0x00ff00
  )
  embed.add_field(name="Latency", value=f"{round(client.latency * 1000)}ms", inline=True)
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

# [[ROBLOX COMMANDS]]
# robloxverify_command
@client.hybrid_command(name="robloxverify", with_app_command=True, description="Verify a Roblox user")
@app_commands.guilds(discord.Object(id=TEST_GUILD_ID))
async def robloxverify(ctx: commands.Context, username: str):
  session = await get_http_session(client)
  if session is None:
    await ctx.reply("❌ Failed to get HTTP session.")
    return
  await ctx.defer()
  ROBLOX_USER_LOOKUP_URL = "https://users.roblox.com/v1/usernames/users"
  ROBLOX_USER_DATA_URL = "https://users.roblox.com/v1/users"
  ROBLOX_AVATAR_URL = "https://thumbnails.roblox.com/v1/users/avatar-headshot"

  headers = {"Content-Type": "application/json"}
  payload = {"usernames": [username], "excludeBannedUsers": True}

  try:
      # Step 1: Get Roblox User ID
      async with session.post(ROBLOX_USER_LOOKUP_URL, headers=headers, json=payload) as response:
          if response.status != 200:
              await ctx.reply("❌ Failed to fetch user data.")
              return

          data = await response.json()
          if not data.get("data"):
              await ctx.reply("❌ No user found with that username.")
              return

          user_info = data["data"][0]
          user_id = user_info.get("id")

      # Step 2: Get Roblox User Profile
      async with session.get(f"{ROBLOX_USER_DATA_URL}/{user_id}") as response:
          if response.status != 200:
              await ctx.reply("❌ Failed to fetch user profile.")
              return

          user_data = await response.json()

      # Step 3: Get Roblox User Avatar
      avatar_url = None
      async with session.get(f"{ROBLOX_AVATAR_URL}?userIds={user_id}&size=420x420&format=Png&isCircular=false") as response:
          if response.status == 200:
              avatar_data = await response.json()
              if avatar_data.get("data"):
                  avatar_url = avatar_data["data"][0].get("imageUrl")

      # Step 4: Build the Embed
      embed = discord.Embed(
          title="🔍 Roblox Account Verification",
          description="Please confirm this is your Roblox account:",
          color=0x00FF00,
      )
      if avatar_url:
          embed.set_thumbnail(url=avatar_url)

      embed.add_field(name="👤 Username", value=user_data.get("name", "N/A"), inline=True)
      embed.add_field(name="✨ Display Name", value=user_data.get("displayName", "N/A"), inline=True)
      embed.add_field(name="🆔 User ID", value=str(user_id), inline=True)

      # Account creation date
      created_date = user_data.get("created", "")[:10] or "N/A"
      embed.add_field(name="📅 Account Created", value=created_date, inline=True)

      # External app display name
      external_app_name = user_data.get("externalAppDisplayName")
      if external_app_name and external_app_name != user_data.get("displayName"):
          embed.add_field(name="📱 External App Name", value=external_app_name, inline=True)

      # User description
      description = (user_data.get("description") or "*No description*").strip()
      if len(description) > 1024:
          description = description[:1021] + "..."
      embed.add_field(name="📝 Description", value=description, inline=False)

      # Verification instructions
      embed.add_field(
          name="✅ To Complete Verification:",
          value="React with ✅ if this is your account.\nReact with ❌ if this is not your account.",
          inline=False,
      )

      embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

      # Step 5: Send the Embed and Add Reactions
      message = await ctx.reply(embed=embed)
      await message.add_reaction("✅")
      await message.add_reaction("❌")
      # Step 6: Wait for User Reaction
      def check(reaction, user):
          return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]
      try:
        reaction, user = await client.wait_for("reaction_add", check=check, timeout=60.0)

        if reaction.emoji == "✅":
            await ctx.reply(f"username, **{user_data.get('name', 'n/a')}** has been saved!\n1. go to the game ---> [PROJECT GTR]({GAME_URL})\n2. type your discord username in the game (in the settings menu).\n3. retype !robloxverify <username> to get your role.")
        else:
            await ctx.reply("❌ Verification failed. Please try again with the correct username.")
        await message.delete()
      except asyncio.TimeoutError:
          await ctx.reply("⏳ Verification timed out. Please try again.")
          await message.delete()

  except Exception as e:
      logging.error(f"Error in roblox_verify command: {e}")
      await ctx.send(f"⚠️ An error occurred while fetching data: {e}")

#initialization



# Signal handling
def handle_signal(signal_num, frame):
    print(f"Received signal {signal_num}. Scheduling shutdown...")
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        print("Event loop is closed. Cannot schedule shutdown.")
    else:
        loop.create_task(handle_shutdown(client))

signal.signal(signal.SIGINT, handle_signal)  # Ctrl+C
signal.signal(signal.SIGTERM, handle_signal) # kill signal

client.run(bot_token, log_handler=handler_for_log, log_level=logging.DEBUG)
