import discord
from discord.ext import tasks
from flask import Flask
from threading import Thread
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT_DISCORD')

# Configurer les intents
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.voice_states = True

# Initialisation du bot
bot = discord.Client(intents=intents)

# Noms des salons vocaux
ONLINE_CHANNEL_NAME = "👥・𝐔𝐭 𝐛𝐨𝐞𝐬 :"
VOICE_CHANNEL_NAME = "🔈・𝐔𝐭 𝐛𝐬𝐨 :"

# === Serveur Web ===
app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === Gestion des événements du bot ===

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    update_channels.start()  # Lancer la mise à jour automatique des salons

@tasks.loop(minutes=1)  # Mettre à jour toutes les minutes
async def update_channels():
    for guild in bot.guilds:
        # Chercher les salons existants
        online_channel = discord.utils.get(guild.voice_channels, name=ONLINE_CHANNEL_NAME)
        voice_channel = discord.utils.get(guild.voice_channels, name=VOICE_CHANNEL_NAME)

        # Créer les salons s'ils n'existent pas
        if not online_channel:
            online_channel = await guild.create_voice_channel(ONLINE_CHANNEL_NAME)
        if not voice_channel:
            voice_channel = await guild.create_voice_channel(VOICE_CHANNEL_NAME)

        # Récupérer les membres en ligne et en vocal
        online_members = [member for member in guild.members if member.status != discord.Status.offline]
        voice_members = [member for vc in guild.voice_channels for member in vc.members]

        # Mettre à jour les noms des salons
        await online_channel.edit(name=f"👥・𝐔𝐭 𝐛𝐨𝐞𝐬 : {len(online_members)}")
        await voice_channel.edit(name=f"🔈・𝐔𝐭 𝐛𝐬𝐨 : {len(voice_members)}")

# === Lancer le bot ===
keep_alive()
bot.run(TOKEN)
