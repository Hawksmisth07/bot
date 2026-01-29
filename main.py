import discord
import os
import google.generativeai as genai
from dotenv import load_dotenv
from keep_alive import keep_alive

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Gemini
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env file.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Configure Discord Client
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
client = discord.Client(intents=intents)

# Gemini Model
# Using gemini-1.5-flash for speed/cost, can be changed to gemini-1.5-pro
model = genai.GenerativeModel('gemini-flash-latest')

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.event
async def on_message(message):
    # Don't respond to ourselves
    if message.author == client.user:
        return

    # Optional: Only respond if mentioned or in a specific channel, 
    # for now we respond to everything for simplicity, or we can check for a prefix.
    # Let's make it respond to direct mentions OR if it's a DM.
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = client.user in message.mentions
    
    # Logic: Respond if DM or Mentioned. 
    # If you want it to respond to ALL messages in a channel, remove the 'if' check below.
    if is_dm or is_mentioned:
        # Show typing indicator while generating response
        async with message.channel.typing():
            try:
                # Clean up the message content (remove the mention)
                user_message = message.content.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()
                
                if not user_message and not message.attachments:
                    await message.reply("Hullo! You mentioned me? How can I help?")
                    return

                # Generate response from Gemini
                # We can add history here for context if needed later
                response = model.generate_content(user_message)
                
                # Discord has a 2000 char limit per message.
                if len(response.text) > 2000:
                    # Split message or just send the first chunk for now works for simple start
                    # A robust solution would chunk it.
                    chunks = [response.text[i:i+2000] for i in range(0, len(response.text), 2000)]
                    for chunk in chunks:
                        await message.reply(chunk)
                else:
                    await message.reply(response.text)

            except Exception as e:
                print(f"Error generating response: {e}")
                await message.reply("Sorry, I had some trouble thinking of a response.")

if __name__ == '__main__':
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not found in .env file.")
    else:
        try:
            keep_alive()
            client.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"Error running bot: {e}")
