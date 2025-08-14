# discord_bot.py
import os
import discord
from discord.commands import Option
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from Backend.core.database import SessionLocal
from Backend.models.models import URL
from Backend.core.logger import log

# -- Configuração Inicial --
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 'Intents' definem quais eventos do Discord nosso bot quer receber.
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

def get_db_session():
    """Gera uma sessão de banco de dados."""
    return SessionLocal()

# -- Eventos do Bot --
@bot.event
async def on_ready():
    """Event triggered when the bot successfully logs in."""
    log.info(f"Discord Bot logged in as {bot.user}")
    print(f"Discord Bot logged in as {bot.user}") # Usamos print aqui para visibilidade imediata no terminal

# -- Comandos do Bot --
@bot.slash_command(
    name="stats",
    description="Get statistics for a shortened URL."
)
async def stats(
    ctx: discord.ApplicationContext,
    short_code: str=Option(str, description="The short code of the URL to check.", required=True)
):
    """Fetches and displays stats for a given short code."""
    await ctx.defer() # Confirma o recebimento do comando para evitar timeout

    log.info(f"Discord command '/stats' received for code: {short_code}")
    db: Session = get_db_session()
    
    try:
        db_url = db.query(URL).filter(URL.short_code == short_code).first()

        if not db_url:
            await ctx.followup.send(f"Sorry, I couldn't find any URL with the code `{short_code}`.")
            return

        # Criando uma 'Embed' para uma resposta bonita e organizada
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
        
        await ctx.followup.send(embed=embed)

    except Exception as e:
        log.error(f"Error during /stats command: {e}")
        await ctx.followup.send("An unexpected error occurred while fetching the stats.")
    finally:
        db.close()

# -- Executando o Bot --
if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        log.error("DISCORD_BOT_TOKEN not found in environment variables. Bot cannot start.")
    else:
        bot.run(DISCORD_BOT_TOKEN)