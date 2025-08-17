import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True  # Needed to manage roles

bot = commands.Bot(command_prefix="?", intents=intents)

# Role IDs
SETUP_ROLE_ID = 1406638586027311296  # Role allowed to setup verification
VERIFIED_ROLE_ID = 1406641285644816576  # Role given to verified users
CHECK_EMOJI = "✅"

# Store the messages the bot creates for verification
setup_messages = set()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    author_roles = [role.id for role in message.author.roles]
    
    # Only allow users with the setup role to create verification messages
    if SETUP_ROLE_ID in author_roles and message.content.startswith("?verification.setup = "):
        # Extract text inside quotes
        try:
            text_to_send = message.content.split('=')[1].strip()
            if text_to_send.startswith('"') and text_to_send.endswith('"'):
                text_to_send = text_to_send[1:-1]  # remove quotes
        except:
            text_to_send = "Verification"

        # Delete original message
        await message.delete()

        # Send verification message
        sent_msg = await message.channel.send(text_to_send)
        await sent_msg.add_reaction(CHECK_EMOJI)
        setup_messages.add(sent_msg.id)

    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    # Ignore bot reactions
    if user.bot:
        return

    # Only handle our verification messages
    if reaction.message.id in setup_messages and str(reaction.emoji) == CHECK_EMOJI:
        guild = reaction.message.guild
        member = guild.get_member(user.id)
        verified_role = guild.get_role(VERIFIED_ROLE_ID)
        
        if verified_role in member.roles:
            return  # Already has role
        
        try:
            await member.add_roles(verified_role)
            print(f"Added {verified_role.name} role to {member.name}")
        except discord.Forbidden:
            print(f"Missing permissions to add role to {member.name}")

# Run the bot
bot.run(os.getenv("TOKEN"))
