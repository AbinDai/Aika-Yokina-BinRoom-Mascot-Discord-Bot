import discord
from discord.ext import commands
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "assets" / "aturan.png"

class Rule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="post_inforule", description="Ngirim chat info server ke channel info-server")
    @commands.has_permissions(administrator=True)
    async def post_rule(self, ctx):
        ambil_gambar = discord.File(IMAGE_PATH, filename="aturan.png")

        embed = discord.Embed(        
            title = "Mohon dibaca dan dipahami agar terhindar dari konsekuensi yang tidak diinginkan.",
            description = "1. Dilarang membuat kegaduhan.\n2. Dilarang SARA.\n3. Gunakan fitur IIspoilerII jika ingin mengirim konten sensitif.\n4. Posting meme bisa di <#904972673124282428>, tapi harus juga diposting di <#904972956281757706>.\n5. Saat musikan, sebelum meng-skip lagu, pastikan bahwa lagunya bukan request-an orang. (Bisa cek pakai command `now playing`).\n6. Patuhi juga [Pedoman Komunitas Discord](https://discord.com/guidelines) agar akunmu aman dari patroli Discord.",
            color = discord.Color(16774141)
        ).set_footer(text="Server kami basically bebas, asal jangan kelewatan aja :)")

        channel = self.bot.get_channel(904972338687270992)
        if channel is None:
            await ctx.send("❌ I couldn't find the target channel.")
            return
        
        await channel.send(file=ambil_gambar)
        await channel.send(embed=embed)

        await ctx.send(f"✅ Pesan info rule sukses terkirim di channel {channel.mention}.")

async def setup(bot):
    await bot.add_cog(Rule(bot))