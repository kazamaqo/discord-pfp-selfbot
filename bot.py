import discord
from discord.ext import commands
import aiohttp
import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Selfbot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='>', intents=intents, self_bot=True)

# Enable discord.py debug logging
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
discord_logger.addHandler(handler)

@bot.event
async def on_ready():
    print(f'✓ Logged in as {bot.user}')
    print(f'✓ User ID: {bot.user.id}')
    print(f'✓ Ready to change PFP & status!')

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Error in {event}: {sys.exc_info()}")

@bot.command()
async def pfp(ctx):
    """Change your profile picture - upload an image with this command"""
    
    # Check if message has attachments
    if not ctx.message.attachments:
        return
    
    attachment = ctx.message.attachments[0]
    
    # Check if file is an image
    if not attachment.content_type or not attachment.content_type.startswith('image/'):
        return
    
    try:
        # Download the image
        image_data = await attachment.read()
        
        # Change the profile picture
        await bot.user.edit(avatar=image_data)
        
        print(f"PFP changed to {attachment.filename}")
        
        # Delete the message
        await ctx.message.delete()
        
    except Exception as e:
        print(f"Error: {str(e)}")

@bot.command()
async def stream(ctx, channel_id: str, *, status_text: str):
    """
    Set streaming status
    Usage: >stream [CHANNEL_ID] [STATUS TEXT]
    Example: >stream 123456789 streaming jin
    """
    
    try:
        # Create a Twitch activity
        activity = discord.Streaming(
            name=status_text,
            url=f"https://twitch.tv/{channel_id}"
        )
        
        await bot.change_presence(activity=activity)
        print(f"Status set to: {status_text}")
        
        # Delete the message
        await ctx.message.delete()
        
    except Exception as e:
        print(f"Error: {str(e)}")

@bot.command()
async def streampic(ctx, channel_id: str, *, status_text: str):
    """
    Set streaming status with a custom picture
    Upload an image with this command
    Usage: >streampic [CHANNEL_ID] [STATUS TEXT] [UPLOAD IMAGE]
    Example: >streampic 123456789 streaming jin [image]
    """
    
    try:
        # Check if message has attachments
        if not ctx.message.attachments:
            return
        
        attachment = ctx.message.attachments[0]
        
        # Check if file is an image
        if not attachment.content_type or not attachment.content_type.startswith('image/'):
            return
        
        # Download the image
        image_data = await attachment.read()
        
        # Change the profile picture
        await bot.user.edit(avatar=image_data)
        
        # Create a Twitch activity with status text
        activity = discord.Streaming(
            name=status_text,
            url=f"https://twitch.tv/{channel_id}"
        )
        
        await bot.change_presence(activity=activity)
        
        print(f"PFP changed to {attachment.filename}")
        print(f"Status set to: {status_text}")
        
        # Delete the message
        await ctx.message.delete()
        
    except Exception as e:
        print(f"Error: {str(e)}")

@bot.command()
async def stopstream(ctx):
    """Stop streaming status and reset to default"""
    
    try:
        await bot.change_presence(activity=None)
        print("Streaming status removed")
        
        # Delete the message
        await ctx.message.delete()
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    print("=" * 50)
    print("Discord PFP & Status Selfbot")
    print("=" * 50)
    
    # Get token from Railway environment variable
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("ERROR: DISCORD_TOKEN environment variable not set!")
        print("Please set DISCORD_TOKEN in Railway variables")
        sys.exit(1)
    
    print(f"Token found. Length: {len(token)}")
    print(f"Token starts with: {token[:20]}...")
    print("Attempting to connect...")
    
    try:
        bot.run(token)
    except discord.errors.LoginFailure as e:
        print("\n❌ LOGIN FAILED!")
        print("=" * 50)
        print("Possible reasons:")
        print("1. Token is invalid or expired")
        print("2. Token format is wrong")
        print("3. Account is locked/deleted")
        print("4. Token has extra spaces/characters")
        print("=" * 50)
        print(f"Error: {str(e)}")
        sys.exit(1)
    except discord.errors.GatewayNotFound:
        print("\n❌ Gateway not found!")
        print("Discord API unreachable")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
