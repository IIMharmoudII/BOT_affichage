import discord
from discord.ext import tasks
from flask import Flask
from threading import Thread
import os

# Charger le token directement depuis les variables d'environnement
TOKEN = os.getenv('TOKEN_BOT_DISCORD')

if not TOKEN:
    raise ValueError("Le token du bot Discord n'est pas défini dans les variables d'environnement.")

# Configurer les intents
intents = discord.Intents.default()
intents.members = True  # Nécessaire pour récupérer les membres
intents.presences = True  # Nécessaire pour vérifier le statut des membres
intents.voice_states = True  # Nécessaire pour vérifier qui est en vocal

# Initialisation du bot
bot = discord.Client(intents=intents)

# Variables pour les noms des salons
VOICE_CHANNEL_VOC_NAME = "🔈・𝐄𝐧 𝐕𝐨𝐜"
VOICE_CHANNEL_ONLINE_NAME = "👥・𝐄𝐧 𝐋𝐢𝐠𝐧𝐞"

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
    await update_channels()  # Mettre à jour les salons à chaque démarrage

@tasks.loop(minutes=1)  # Mettre à jour toutes les 1 minute
async def update_channels():
    for guild in bot.guilds:
        # Vérifier l'existence des salons vocaux avant de les créer
        voice_channel_online = discord.utils.get(guild.voice_channels, name=VOICE_CHANNEL_ONLINE_NAME)
        if not voice_channel_online:
            # Si le salon n'existe pas, on le crée
            voice_channel_online = await guild.create_voice_channel(VOICE_CHANNEL_ONLINE_NAME)

        voice_channel_voc = discord.utils.get(guild.voice_channels, name=VOICE_CHANNEL_VOC_NAME)
        if not voice_channel_voc:
            # Si le salon n'existe pas, on le crée
            voice_channel_voc = await guild.create_voice_channel(VOICE_CHANNEL_VOC_NAME)

        # Récupérer les membres en ligne
        online_members = [member for member in guild.members if member.status != discord.Status.offline]

        # Récupérer les membres en vocal
        voice_members = [member for vc in guild.voice_channels for member in vc.members]

        # Mettre à jour les noms des salons vocaux
        await voice_channel_online.edit(name=f"👥・𝐄𝐧 𝐋𝐢𝐠𝐧𝐞 : {len(online_members)}")
        await voice_channel_voc.edit(name=f"🔈・𝐄𝐧 𝐕𝐨𝐜 : {len(voice_members)}")

@bot.event
async def on_guild_join(guild):
    # Créer les salons vocaux s'ils n'existent pas lorsqu'un bot rejoint un nouveau serveur
    voice_channel_online = discord.utils.get(guild.voice_channels, name=VOICE_CHANNEL_ONLINE_NAME)
    if not voice_channel_online:
        await guild.create_voice_channel(VOICE_CHANNEL_ONLINE_NAME)

    voice_channel_voc = discord.utils.get(guild.voice_channels, name=VOICE_CHANNEL_VOC_NAME)
    if not voice_channel_voc:
        await guild.create_voice_channel(VOICE_CHANNEL_VOC_NAME)

# === Lancer le bot ===
keep_alive()
bot.run(TOKEN)
