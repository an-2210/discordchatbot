# discordchatbot
Overview
This is a feature-rich Discord chatbot that enhances user experience by providing the following functionalities:
Reminders: Set, modify, and delete reminders.
Text Summarization: Summarize long text messages for easy understanding.
Q&A: Answer general questions.
Music Playback: Plays and pauses music in voice channels.
      

#Features

1. Reminders
Users can set reminders for specific times.
Modify or delete existing reminders.
Receive a notification when the reminder is due.

2. Text Summarization
Extracts key points from long messages.
Helps users quickly grasp essential information.

3. Q&A
Answers general knowledge and factual questions.
Uses AI-powered responses for accuracy.

4. Music Playback
Play songs from various sources.
Pause, resume, skip, and stop playback.

5.Makes Polls
Takes in Question andoptions and makes a poll.

#Installation

#Prerequisites

Python 3.12.0
Discord bot token
Google Gemini API key
Python libraries: discord,os,google.generativeai,yt_dlp,asyncio.

#Setup
1.Clone this repository:
git clone 
git clone https://github.com/yourusername/discord-chatbot.git
cd discord-chatbot

2.Install dependencies
pip install -r requirements.txt

3. Create a .env file and add your bot token:
DISCORD_TOKEN=your-bot-token

4.Run your bot
python bot.py

#Commands
/setreminder <date> <time> <message>: Sets reminders
/modifyreminder <date> <time> <message>: Modify reminders
/deletereminder <date> <time> <message>:Deletes reminders
!summarize <text>: Summarizes texts
!ask <question>: Uses AI to give answer to questions
!play <URL>: Plays music when given url
!pause: pauses music if it is playing
!resume: resumes music if it is paused
!stop: Stops playing music
