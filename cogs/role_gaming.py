import discord
from typing import Optional
from discord.ext import commands
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "assets" / "khusus gaming.png"

class PickRole_Gaming(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="post_role-gaming", description="Ngirim chat Pewarna Nickname ke channel ambil-role")
    @commands.has_permissions(administrator=True)
    async def post_rolegaming(self, ctx):
        ambil_gambar = discord.File(IMAGE_PATH, filename="khusus gaming.png")

        embed = discord.Embed(
            description = "🔫 <@&918149510381858886>\n🎶 <@&918149638572371968>\n<:standard_cube:1267294528541560882> <@&918060425336201276>\n<:gtav_logo:1454370088030441641> <@&1427220753786343544>\n<:l4d2_logo:1500238213678104866> <@&1502672334027493436>",
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
    await bot.add_cog(PickRole_Gaming(bot))