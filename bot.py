import discord
from discord.ext import commands
import os
import sys
import logging
from aiohttp import web
import asyncio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Selfbot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='>', intents=intents, self_bot=True)

# Global token storage
authenticated_token = None
web_server = None

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
    
    if not ctx.message.attachments:
        return
    
    attachment = ctx.message.attachments[0]
    
    if not attachment.content_type or not attachment.content_type.startswith('image/'):
        return
    
    try:
        image_data = await attachment.read()
        await bot.user.edit(avatar=image_data)
        print(f"PFP changed to {attachment.filename}")
        await ctx.message.delete()
    except Exception as e:
        print(f"Error: {str(e)}")

@bot.command()
async def stream(ctx, channel_id: str, *, status_text: str):
    """
    Set streaming status
    Usage: >stream [CHANNEL_ID] [STATUS TEXT]
    """
    
    try:
        activity = discord.Streaming(
            name=status_text,
            url=f"https://twitch.tv/{channel_id}"
        )
        await bot.change_presence(activity=activity)
        print(f"Status set to: {status_text}")
        await ctx.message.delete()
    except Exception as e:
        print(f"Error: {str(e)}")

@bot.command()
async def streampic(ctx, channel_id: str, *, status_text: str):
    """
    Set streaming status with a custom picture
    """
    
    try:
        if not ctx.message.attachments:
            return
        
        attachment = ctx.message.attachments[0]
        
        if not attachment.content_type or not attachment.content_type.startswith('image/'):
            return
        
        image_data = await attachment.read()
        await bot.user.edit(avatar=image_data)
        
        activity = discord.Streaming(
            name=status_text,
            url=f"https://twitch.tv/{channel_id}"
        )
        await bot.change_presence(activity=activity)
        
        print(f"PFP changed to {attachment.filename}")
        print(f"Status set to: {status_text}")
        await ctx.message.delete()
    except Exception as e:
        print(f"Error: {str(e)}")

@bot.command()
async def stopstream(ctx):
    """Stop streaming status"""
    
    try:
        await bot.change_presence(activity=None)
        print("Streaming status removed")
        await ctx.message.delete()
    except Exception as e:
        print(f"Error: {str(e)}")

async def handle_login(request):
    """Handle login page and token submission"""
    global authenticated_token
    
    if request.method == 'GET':
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Discord Bot Login</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; background: #36393f; color: white; }
                .container { max-width: 400px; margin: 0 auto; background: #2f3136; padding: 30px; border-radius: 8px; }
                h1 { color: #7289da; }
                input { width: 100%; padding: 10px; margin: 10px 0; border: none; border-radius: 4px; box-sizing: border-box; }
                button { background: #7289da; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; }
                button:hover { background: #5a73c4; }
                .info { background: #40444b; padding: 15px; border-radius: 4px; margin: 20px 0; font-size: 14px; }
                .info p { margin: 8px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Discord Bot Login</h1>
                <div class="info">
                    <p><strong>How to get your token:</strong></p>
                    <p>1. Open Discord in browser</p>
                    <p>2. Press Ctrl+Shift+I (DevTools)</p>
                    <p>3. Go to: Application → Local Storage → discord.com</p>
                    <p>4. Find "token" and copy the value</p>
                    <p>5. Paste it below</p>
                </div>
                <form method="POST">
                    <input type="password" name="token" placeholder="Paste your Discord token here" required autofocus>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    elif request.method == 'POST':
        data = await request.post()
        token = data.get('token', '').strip()
        
        if not token:
            return web.Response(text="Token is required!", status=400)
        
        authenticated_token = token
        print(f"\n✓ Token received! Length: {len(token)}")
        print("Connecting to Discord...\n")
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Success</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; background: #36393f; color: white; }
                .container { max-width: 400px; margin: 0 auto; background: #2f3136; padding: 30px; border-radius: 8px; }
                h1 { color: #43b581; }
                .success { background: #40444b; padding: 15px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✓ Login Successful!</h1>
                <div class="success">
                    <p>Your token has been received.</p>
                    <p>The bot is now connecting...</p>
                    <p>You can close this window.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')

async def start_web_server(port=8080):
    """Start web server for login"""
    global web_server
    
    app = web.Application()
    app.router.add_get('/', handle_login)
    app.router.add_post('/', handle_login)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"🌐 Login page is running!")
    print(f"📱 Open: https://discord-pfp-selfbot-h.up.railway.app/")
    print(f"⏳ Waiting for token...\n")
    
    return runner

async def wait_for_token(timeout=600):
    """Wait for token to be submitted via web form"""
    global authenticated_token
    
    start_time = asyncio.get_event_loop().time()
    
    while authenticated_token is None:
        if asyncio.get_event_loop().time() - start_time > timeout:
            print("❌ Login timeout! No token received.")
            return None
        
        await asyncio.sleep(1)
    
    return authenticated_token

async def main():
    print("=" * 50)
    print("Discord PFP & Status Selfbot")
    print("=" * 50 + "\n")
    
    global authenticated_token
    
    # Check if token is in environment variables
    token = os.getenv('DISCORD_TOKEN')
    port = int(os.getenv('PORT', 8080))
    
    if token:
        print(f"✓ Using token from environment variable")
        authenticated_token = token
    else:
        # Start web server for login
        print("No DISCORD_TOKEN found. Starting web login...\n")
        
        web_runner = await start_web_server(port=port)
        
        try:
            authenticated_token = await wait_for_token()
            
            if not authenticated_token:
                await web_runner.cleanup()
                sys.exit(1)
        except Exception as e:
            print(f"Error during login: {e}")
            await web_runner.cleanup()
            sys.exit(1)
    
    # Connect bot
    try:
        await bot.start(authenticated_token)
    except discord.errors.LoginFailure as e:
        print(f"❌ Invalid token! Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped.")
        sys.exit(0)
