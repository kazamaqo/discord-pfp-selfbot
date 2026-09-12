import discord
from discord.ext import commands
import os
import sys
import logging
from aiohttp import web
import asyncio
from secrets import token_urlsafe

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
app_runner = None

# Store sessions
sessions = {}

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
    """Set streaming status"""
    
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
    """Set streaming status with a custom picture"""
    
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

async def handle_root(request):
    """Handle root page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Discord Bot Login</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background: #36393f; color: white; }
            .container { max-width: 500px; margin: 0 auto; background: #2f3136; padding: 30px; border-radius: 8px; }
            h1 { color: #7289da; margin-bottom: 30px; }
            .method { background: #40444b; padding: 20px; margin: 15px 0; border-radius: 4px; }
            .method h2 { color: #7289da; font-size: 18px; margin-top: 0; }
            .method p { margin: 10px 0; font-size: 14px; }
            .token-form { margin-top: 20px; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: none; border-radius: 4px; box-sizing: border-box; }
            button { background: #7289da; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; margin-top: 10px; }
            button:hover { background: #5a73c4; }
            .info { background: #40444b; padding: 15px; border-radius: 4px; margin: 20px 0; font-size: 12px; }
            .warning { color: #faa61a; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Discord Bot Login</h1>
            
            <div class="method">
                <h2>Method 1: Manual Token Entry</h2>
                <p>If you have a Discord token, paste it here:</p>
                <form method="POST" action="/login">
                    <input type="password" name="token" placeholder="Paste your Discord token" required>
                    <button type="submit">Login with Token</button>
                </form>
                <div class="info">
                    <p><strong>How to get token:</strong></p>
                    <p>1. Open Discord in browser</p>
                    <p>2. Press Ctrl+Shift+I</p>
                    <p>3. Application → Local Storage → discord.com</p>
                    <p>4. Find "token" key</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def handle_login(request):
    """Handle token login"""
    global authenticated_token
    
    if request.method == 'POST':
        data = await request.post()
        token = data.get('token', '').strip()
        
        if not token:
            return web.Response(text="Token is required!", status=400)
        
        # Remove common prefixes if accidentally included
        token = token.replace('MFA.', '').strip()
        
        print(f"\n📝 Token received!")
        print(f"   Length: {len(token)}")
        print(f"   Format check: {'✓' if len(token) > 50 else '❌'}")
        print(f"   Attempting connection...\n")
        
        authenticated_token = token
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Logging in...</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; background: #36393f; color: white; }
                .container { max-width: 400px; margin: 0 auto; background: #2f3136; padding: 30px; border-radius: 8px; }
                h1 { color: #7289da; }
                .loading { background: #40444b; padding: 20px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⏳ Logging in...</h1>
                <div class="loading">
                    <p>Connecting to Discord...</p>
                    <p>Check the server logs for status.</p>
                    <p style="font-size: 12px; margin-top: 20px;">You can close this window.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')

async def start_web_server(port=8080):
    """Start web server for login"""
    global app_runner
    
    app = web.Application()
    app.router.add_get('/', handle_root)
    app.router.add_post('/login', handle_login)
    
    app_runner = web.AppRunner(app)
    await app_runner.setup()
    site = web.TCPSite(app_runner, '0.0.0.0', port)
    await site.start()
    
    print(f"🌐 Web server started!")
    print(f"📱 Open: https://discord-pfp-selfbot-h.up.railway.app/")
    print(f"⏳ Waiting for token submission...\n")
    
    return app_runner

async def wait_for_token(timeout=600):
    """Wait for token to be submitted via web form"""
    global authenticated_token
    
    start_time = asyncio.get_event_loop().time()
    
    while authenticated_token is None:
        if asyncio.get_event_loop().time() - start_time > timeout:
            print("❌ Login timeout!")
            return None
        
        await asyncio.sleep(1)
    
    return authenticated_token

async def main():
    print("=" * 60)
    print("Discord PFP & Status Selfbot")
    print("=" * 60 + "\n")
    
    global authenticated_token, app_runner
    
    # Check if token is in environment variables
    token = os.getenv('DISCORD_TOKEN')
    port = int(os.getenv('PORT', 8080))
    
    if token:
        print(f"✓ Using token from environment variable")
        authenticated_token = token
    else:
        # Start web server for login
        print("Starting web login interface...\n")
        
        app_runner = await start_web_server(port=port)
        
        try:
            authenticated_token = await wait_for_token()
            
            if not authenticated_token:
                print("❌ No token received. Exiting.")
                if app_runner:
                    await app_runner.cleanup()
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error during login: {e}")
            if app_runner:
                await app_runner.cleanup()
            sys.exit(1)
    
    # Connect bot
    try:
        print("🔌 Connecting to Discord...\n")
        await bot.start(authenticated_token)
    except discord.errors.LoginFailure as e:
        print(f"\n❌ Login Failed: {str(e)}")
        print("\nPossible issues:")
        print("- Token is invalid or expired")
        print("- Token format is wrong")
        print("- Account is locked or banned")
        print("\nTry getting a fresh token from Discord DevTools")
        if app_runner:
            await app_runner.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        if app_runner:
            await app_runner.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nBot stopped.")
        sys.exit(0)
