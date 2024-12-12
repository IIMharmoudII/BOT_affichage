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

# Noms de base des salons vocaux
BASE_ONLINE_CHANNEL_NAME = "\ud83d\udee5\ufe0f\u30fb\ud835\udd08\ud835\udd2c \ud835\udd11\ud835\udd22\ud835\udd29\ud835\udd29\ud835\udd2c\ud835\udd1e :"
BASE_VOICE_CHANNEL_NAME = "\ud83d\udd08\u30fb\ud835\udd08\ud835\udd2c \ud835\udd1c\ud835\udd1e\ud835\udd34 :"

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

@tasks.loop(seconds=30)  # Mettre à jour toutes les 30 secondes
async def update_channels():
    for guild in bot.guilds:
        # Chercher les salons existants en ignorant la valeur actuelle
        online_channel = discord.utils.find(
            lambda c: c.name.startswith(BASE_ONLINE_CHANNEL_NAME) and isinstance(c, discord.VoiceChannel),
            guild.voice_channels
        )
        voice_channel = discord.utils.find(
            lambda c: c.name.startswith(BASE_VOICE_CHANNEL_NAME) and isinstance(c, discord.VoiceChannel),
            guild.voice_channels
        )

        # Vérifier que les salons existent, sinon afficher un avertissement
        if not online_channel:
            print(f"[Avertissement] Le salon '{BASE_ONLINE_CHANNEL_NAME}' n'existe pas dans le serveur '{guild.name}'.")
        if not voice_channel:
            print(f"[Avertissement] Le salon '{BASE_VOICE_CHANNEL_NAME}' n'existe pas dans le serveur '{guild.name}'.")

        # Récupérer les membres en ligne et en vocal
        online_members = [member for member in guild.members if member.status != discord.Status.offline]
        voice_members = [member for vc in guild.voice_channels for member in vc.members]

        # Mettre à jour les noms des salons existants
        if online_channel:
            await online_channel.edit(name=f"{BASE_ONLINE_CHANNEL_NAME} {len(online_members)}")
        if voice_channel:
            await voice_channel.edit(name=f"{BASE_VOICE_CHANNEL_NAME} {len(voice_members)}")

# === Lancer le bot ===
keep_alive()
bot.run(TOKEN)
