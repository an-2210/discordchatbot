import discord
import os
import google.generativeai as genai
import yt_dlp as youtubedl
import asyncio
from datetime import datetime

import re

from discord.ext import commands
from discord import app_commands



DISCORD_TOKEN = "YOUR TOKEN"
GEMINI_API_KEY = "YOUR API"


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


# Initialize the bot
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True  # Enable message content intent
reminders = {}


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is now online!")
    try:
        synced = await bot.tree.sync()  # Sync slash commands with Discord
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Create a slash command to set reminders with date and time
@bot.tree.command(name="setreminder", description="Set a reminder with date and time")
async def set_reminder(interaction: discord.Interaction, date: str, time: str, message: str):
    # Parse date and time
    try:
        reminder_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    except ValueError:
        await interaction.response.send_message("Invalid date or time format. Use YYYY-MM-DD HH:MM.")
        return
    
    # Check if the reminder is in the past
    if reminder_datetime < datetime.now():
        await interaction.response.send_message("Reminder date and time are in the past.")
        return

    await interaction.response.send_message(f"Reminder set for {date} {time} with message: {message}")
    
    # Wait until the reminder time
    while datetime.now() < reminder_datetime:
        await asyncio.sleep(60)  # Check every minute
    
    # Send the reminder
    await interaction.followup.send(f"Reminder: {message}")

# Create a slash command to modify reminders
@bot.tree.command(name="modifyreminder", description="Modify a reminder")
async def modify_reminder(interaction: discord.Interaction, reminder_id: int, date: str, time: str, message: str):
    try:
        if reminder_id not in reminders:
            await interaction.response.send_message("Reminder not found.")
            return
        
        # Parse new date and time
        new_reminder_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        # Check if the new reminder is in the past
        if new_reminder_datetime < datetime.now():
            await interaction.response.send_message("New reminder date and time are in the past.")
            return
        
        # Update the reminder
        reminders[reminder_id]["datetime"] = new_reminder_datetime
        reminders[reminder_id]["message"] = message
        
        await interaction.response.send_message(f"Reminder {reminder_id} modified to {date} {time} with message: {message}")
    
    except Exception as e:
        await interaction.response.send_message("An error occurred while modifying the reminder.")
        print(f"Error modifying reminder: {e}")

# Create a slash command to delete reminders
@bot.tree.command(name="deletereminder", description="Delete a reminder")
async def delete_reminder(interaction: discord.Interaction, reminder_id: int):
    try:
        if reminder_id not in reminders:
            await interaction.response.send_message("Reminder not found.")
            return
        
        # Remove the reminder
        del reminders[reminder_id]
        
        await interaction.response.send_message(f"Reminder {reminder_id} deleted.")
    
    except Exception as e:
        await interaction.response.send_message("An error occurred while deleting the reminder.")
        print(f"Error deleting reminder: {e}")
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send(f"Welcome {member.mention} to {member.guild.name}!")

@bot.command(name='ask')
async def ask(ctx, *, question):
    try:
        response = model.generate_content(question)
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command(name="summarize")
async def summarize(ctx, *, message_to_summarize):
    try:
        prompt = f"Summarize this: {message_to_summarize}"
        response = model.generate_content(prompt)
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
# Global variables for the music player
voice_client = None
audio_source = None
is_playing = False

# Music command - Play music from a YouTube URL
@bot.command(name="play")
async def play(ctx, url: str):
    """Play a YouTube video in the voice channel"""
    global voice_client, audio_source, is_playing
    
    if not ctx.author.voice:
        await ctx.send("You need to join a voice channel first!")
        return

    channel = ctx.author.voice.channel

    # Join the voice channel
    if not voice_client:
        voice_client = await channel.connect()

    # Download audio from YouTube URL using yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        audio_source = discord.FFmpegPCMAudio(url2)

    # Play the audio
    if not is_playing:
        voice_client.play(audio_source, after=lambda e: print('done', e))
        is_playing = True
        await ctx.send(f"Now playing: {info['title']}")

# Music command - Pause the music
@bot.command(name="pause")
async def pause(ctx):
    """Pause the current music"""
    global is_playing

    if not voice_client or not is_playing:
        await ctx.send("No music is currently playing!")
        return

    voice_client.pause()
    is_playing = False
    await ctx.send("Music paused!")

# Music command - Resume the music
@bot.command(name="resume")
async def resume(ctx):
    """Resume the paused music"""
    global is_playing

    if not voice_client or is_playing:
        await ctx.send("Music is already playing!")
        return

    voice_client.resume()
    is_playing = True
    await ctx.send("Music resumed!")

# Music command - Stop the music and disconnect from the voice channel
@bot.command(name="stop")
async def stop(ctx):
    """Stop the music and disconnect from the voice channel"""
    global voice_client, is_playing

    if not voice_client:
        await ctx.send("I'm not connected to a voice channel!")
        return

    voice_client.stop()
    await voice_client.disconnect()
    voice_client = None
    is_playing = False
    await ctx.send("Music stopped and disconnected from the voice channel.")

# Poll command - Create a poll
@bot.command(name="poll")
async def poll(ctx, question: str, *choices: str):
    """Create a simple poll with multiple choices."""
    if len(choices) < 2:
        await ctx.send("You need to provide at least two choices!")
        return

    embed = discord.Embed(title=question, description="\n".join(f"{i+1}. {choice}" for i, choice in enumerate(choices)))
    message = await ctx.send(embed=embed)

    # Add reactions for each choice
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    for i in range(len(choices)):
        await message.add_reaction(emojis[i])

    await ctx.send("Poll created! Users can vote by reacting to the message.")



# Run the bot with your token
bot.run("your token")
