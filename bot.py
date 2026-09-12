import discord
from discord.ext import commands
import aiohttp
import os

# Selfbot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='>', intents=intents, self_bot=True)

@bot.event
async def on_ready():
    print(f'✓ Logged in as {bot.user}')
    print(f'✓ Ready to change PFP!')

@bot.command()
async def pfp(ctx):
    """Change your profile picture - upload an image with this command"""
    
    # Check if message has attachments
    if not ctx.message.attachments:
        await ctx.send("❌ Please upload an image with the command")
        return
    
    attachment = ctx.message.attachments[0]
    
    # Check if file is an image
    if not attachment.content_type or not attachment.content_type.startswith('image/'):
        await ctx.send("❌ Please upload a valid image file")
        return
    
    try:
        # Download the image
        image_data = await attachment.read()
        
        # Change the profile picture
        await bot.user.edit(avatar=image_data)
        
        await ctx.send(f"✓ PFP changed to {attachment.filename}!")
        print(f"✓ PFP changed successfully")
        
    except Exception as e:
        await ctx.send(f"❌ Error changing PFP: {str(e)}")
        print(f"Error: {str(e)}")

def main():
    print("=" * 50)
    print("Discord PFP Selfbot")
    print("=" * 50)
    
    # Get token from user
    token = input("\n🔑 Enter your Discord token: ").strip()
    
    if not token:
        print("❌ Token is required!")
        return
    
    print("\n⏳ Connecting...")
    
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        print("❌ Invalid token!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
