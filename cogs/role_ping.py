import discord
from typing import Optional
from discord.ext import commands
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "assets" / "ping.png"

class PickRole_Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="post_role-ping", description="Ngirim chat Pewarna Nickname ke channel ambil-role")
    @commands.has_permissions(administrator=True)
    async def post_roleping(self, ctx):
        ambil_gambar = discord.File(IMAGE_PATH, filename="ping.png")

        embed = discord.Embed(
            description = "<:TheHx_icon:1501261469180887110> <@&905034343796314132>\n<:Discordpink:1539758228131414136> <@&1539844848251707423>\n~~🌙 <@&960106628689039391>~~ (Ramadan only)",
            color = discord.Color(0xfff3fd)
        ).set_footer(text="React dengan emoji sesuai pada teks untuk mengamil role yang diinginkan.")

        channel = self.bot.get_channel(1539871181765611560)
        if channel is None:
            await ctx.send("❌ Channel-nya gaada. Coba cek lagi ID-nya.")
            return
        
        await channel.send(file=ambil_gambar)
        await channel.send(embed=embed)

        await ctx.send(f"✅ Pesan info server server terkirim di channel {channel.mention}.")

async def setup(bot):
    await bot.add_cog(PickRole_Ping(bot))