import discord, os, asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN_BOT")

OWNER_ID = 1524951093560213638

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

class AikaYokina(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def interaction_check(self, interaction:discord.Interaction) -> bool:
        if interaction.guild is None and interaction.user.id != OWNER_ID:
            print("[Aika] Ada yang mencoba mengeksekusi command lewat DM, aksi dicegat.")
            return False
        return True

bot = AikaYokina(command_prefix="ak!", intents=intents)

@bot.check
async def block_dm_prefix_commands(ctx:commands.Context) -> bool:
    if ctx.guild is None and ctx.author.id != OWNER_ID:
        print("[Aika] Ada yang mencoba mengeksekusi command lewat DM, aksi dicegat.")
        return False
    return True

@bot.event
async def on_ready():
    await bot.change_presence(
        status = discord.Status.dnd,
        activity = discord.CustomActivity(name="Main di BinRoom...")
    )
    print(f"🟢 {bot.user} sudah online")

    try:
        synced = await bot.tree.sync()
        print(f"[Aika] {len(synced)} slash command berhasil disinkronkan.")
    except Exception as e:
        print(f"[Aika] Gagal menyinkronkan slash command: {e}")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())