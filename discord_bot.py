# discord_bot.py
import os
import discord
import json
import pika
import threading
import time
import asyncio
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from Backend.core.database import SessionLocal
from Backend.models.models import URL
from Backend.core.logger import log

# -- Initial Setup --
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID") # Channel for alerts
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
ALERT_QUEUE_NAME = "alerts_queue"
ALERT_EXCHANGE_NAME = "alerts_exchange"

# Intents define the events the bot will listen to
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

def get_db_session():
    """Generates a database session."""
    return SessionLocal()

# --- RabbitMQ Consumer Logic ---
def alert_consumer_thread():
    """Thread that connects to RabbitMQ and consumes alert messages."""
    
    def process_alert_message(ch, method, properties, body):
        """Callback function to process a message from the alerts_queue."""
        try:
            data = json.loads(body.decode())
            log.info(f"Alert received from RabbitMQ: {data['title']}")
            # Schedule the async task to run on the bot's main event loop
            bot.loop.create_task(send_discord_alert_from_thread(data))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            log.error(f"Error processing alert message: {e}")

    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            
            channel.exchange_declare(exchange=ALERT_EXCHANGE_NAME, exchange_type='fanout')
            
           
            result = channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            
            
            channel.queue_bind(exchange=ALERT_EXCHANGE_NAME, queue=queue_name)
            
            
            channel.basic_consume(queue=queue_name, on_message_callback=process_alert_message)
            
            log.info(f"Alert consumer thread started, listening to exchange '{ALERT_EXCHANGE_NAME}'.")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            log.error(f"Alert consumer could not connect to RabbitMQ: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            log.error(f"An error occurred in the alert consumer thread: {e}")
            break

async def send_discord_alert_from_thread(data: dict):
    """Asynchronously sends the alert message to the Discord channel."""
    if not DISCORD_CHANNEL_ID:
        log.error("Cannot send alert, DISCORD_CHANNEL_ID is not set.")
        return
    try:
        # Wait until the bot is fully connected before trying to get the channel
        await bot.wait_until_ready()
        channel = bot.get_channel(int(DISCORD_CHANNEL_ID))
        if not channel:
            log.error(f"Cannot send alert, channel not found with ID: {DISCORD_CHANNEL_ID}")
            return

        colors = {"INFO": discord.Color.blue(), "WARNING": discord.Color.orange(), "CRITICAL": discord.Color.red()}
        embed = discord.Embed(
            title=data.get("title"),
            description=data.get("message"),
            color=colors.get(data.get("level", "INFO").upper(), discord.Color.default())
        )
        embed.set_footer(text="Encurtador de Links - Alerta da API")
        await channel.send(embed=embed)
    except Exception as e:
        log.error(f"Failed to send alert from thread to Discord: {e}")


# -- Bot Events --
@bot.event
async def on_ready():
    """Event triggered when the bot successfully logs in."""
    if not DISCORD_GUILD_ID:
        log.error("DISCORD_GUILD_ID not set in .env. Cannot sync commands.")
        return
    try:
        guild = discord.Object(id=int(DISCORD_GUILD_ID))
        await tree.sync(guild=guild)
        log.info(f"Commands synced for guild: {DISCORD_GUILD_ID}")
        print(f"✅ Discord Bot logged in as {bot.user}")
    except Exception as e:
        log.error(f"Failed to sync commands: {e}")

# -- Slash Commands ('/') --
@tree.command(
    name="stats",
    description="Get statistics for a shortened URL.",
    guild=discord.Object(id=int(DISCORD_GUILD_ID))
)
async def stats(interaction: discord.Interaction, short_code: str):
    """Fetches and displays statistics for a given short_code."""
    await interaction.response.defer()
    log.info(f"Discord command '/stats' received for code: {short_code}")
    db: Session = get_db_session()
    try:
        db_url = db.query(URL).filter(URL.short_code == short_code).first()
        if not db_url:
            await interaction.followup.send(f"❌ Could not find any URL with the code `{short_code}`.")
            return

        embed = discord.Embed(
            title=f"📊 Stats for `/{short_code}`",
            color=discord.Color.blue()
        )
        embed.add_field(name="Original URL", value=f"||{db_url.original_url}||", inline=False)
        embed.add_field(name="Clicks", value=str(db_url.current_clicks), inline=True)
        click_limit = "Unlimited" if db_url.max_clicks == 0 else str(db_url.max_clicks)
        embed.add_field(name="Click Limit", value=click_limit, inline=True)
        status = "Active"
        if db_url.max_clicks > 0 and db_url.current_clicks >= db_url.max_clicks:
            status = "Expired"
        embed.add_field(name="Status", value=status, inline=True)
        embed.set_footer(text=f"Created on: {db_url.created_at.strftime('%Y-%m-%d %H:%M')}")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        log.error(f"Error in /stats command: {e}")
        await interaction.followup.send("⚠️ An unexpected error occurred while fetching stats.")
    finally:
        db.close()

# -- Bot Execution --
if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        log.error("DISCORD_BOT_TOKEN not found. Bot cannot start.")
    else:
        # Start the RabbitMQ consumer in a separate thread
        consumer = threading.Thread(target=alert_consumer_thread, daemon=True)
        consumer.start()
        
        # Start the Discord bot
        bot.run(DISCORD_BOT_TOKEN)