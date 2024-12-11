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
intents.members = True  # Nécessaire pour récupérer les membres
intents.presences = True  # Nécessaire pour vérifier le statut des membres
intents.voice_states = True  # Nécessaire pour vérifier qui est en vocal

# Initialisation du bot
bot = discord.Client(intents=intents)

# Variables pour les noms des salons
ONLINE_CHANNEL_NAME = "membres-en-ligne"
VOICE_CHANNEL_NAME = "membres-en-vocal"

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


@tasks.loop(minutes=1)  # Mettre à jour toutes les 1 minute
async def update_channels():
    for guild in bot.guilds:
        # Vérifier ou créer le salon pour les membres en ligne
        online_channel = discord.utils.get(guild.text_channels, name=ONLINE_CHANNEL_NAME)
        if not online_channel:
            online_channel = await guild.create_text_channel(ONLINE_CHANNEL_NAME)

        # Vérifier ou créer le salon pour les membres en vocal
        voice_channel = discord.utils.get(guild.text_channels, name=VOICE_CHANNEL_NAME)
        if not voice_channel:
            voice_channel = await guild.create_text_channel(VOICE_CHANNEL_NAME)

        # Récupérer les membres en ligne
        online_members = [member for member in guild.members if member.status != discord.Status.offline]

        # Récupérer les membres en vocal
        voice_members = [member for vc in guild.voice_channels for member in vc.members]

        # Renommer les salons avec les informations mises à jour
        await online_channel.edit(name=f"{ONLINE_CHANNEL_NAME}-{len(online_members)}")
        await voice_channel.edit(name=f"{VOICE_CHANNEL_NAME}-{len(voice_members)}")

@bot.event
async def on_guild_join(guild):
    # Créer les salons s'ils n'existent pas lorsqu'un bot rejoint un nouveau serveur
    if not discord.utils.get(guild.text_channels, name=ONLINE_CHANNEL_NAME):
        await guild.create_text_channel(ONLINE_CHANNEL_NAME)
    if not discord.utils.get(guild.text_channels, name=VOICE_CHANNEL_NAME):
        await guild.create_text_channel(VOICE_CHANNEL_NAME)

# === Lancer le bot ===
keep_alive()
bot.run(TOKEN)

