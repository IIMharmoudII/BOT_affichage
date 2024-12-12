# -*- coding: utf-8 -*-

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
BASE_ONLINE_CHANNEL_NAME = "👥・𝐄𝐧 𝐋𝐢𝐠𝐧𝐞 :"
BASE_VOICE_CHANNEL_NAME = "🔈・𝐄𝐧 𝐕𝐨𝐜 :"

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
    print("update_channels task started.")
    if not update_channels.is_running():
        update_channels.start()  # Lancer la mise à jour automatique des salons

@tasks.loop(seconds=30)  # Mettre à jour toutes les 30 secondes
async def update_channels():
    try:
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
                print(f"[Avertissement] Le salon {repr(BASE_ONLINE_CHANNEL_NAME)} n'existe pas dans le serveur {repr(guild.name)}.")
            if not voice_channel:
                print(f"[Avertissement] Le salon {repr(BASE_VOICE_CHANNEL_NAME)} n'existe pas dans le serveur {repr(guild.name)}.")

            # Récupérer les membres en ligne et en vocal
            online_members = [member for member in guild.members if member.status != discord.Status.offline]
            voice_members = [member for vc in guild.voice_channels for member in vc.members]

            # Journalisation pour le débogage
            print(f"Online members in {guild.name}: {len(online_members)}")
            print(f"Voice members in {guild.name}: {len(voice_members)}")

            # Mettre à jour les noms des salons existants
            if online_channel:
                await online_channel.edit(name=f"{BASE_ONLINE_CHANNEL_NAME} {len(online_members)}")
            if voice_channel:
                await voice_channel.edit(name=f"{BASE_VOICE_CHANNEL_NAME} {len(voice_members)}")
    except Exception as e:
        print(f"[Erreur] Une erreur est survenue dans update_channels: {e}")

# === Lancer le bot ===
keep_alive()
bot.run(TOKEN)
