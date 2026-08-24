import discord
from discord.ext import commands

class About(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="about", description="Liat info tentang saya.")
    async def about(self, ctx: commands.Context):

        embed = discord.Embed(
            title = "Tentang Bot",
            description = "Halo, aku cuma maskot server ini yang kebetulan ditugasin ngejagain. Namaku Aika Yokina. Aku berumur 17 tahun. Salam kenal. Untuk info lebih lanjut soal diriku, bisa cek di <#1533541868653117571>.",
            color = 0xDE82CF
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/863959650448703538/1540201066455371888/bunga.png?ex=6a891785&is=6a87c605&hm=69d799fb0347fd7461acc9e4aeaaa32563dbaf31a05cc239f6ae10301e6dba47&")
        embed.set_image(url="https://cdn.discordapp.com/attachments/863959650448703538/1540201112265687150/tumpukan_silly_aika.png?ex=6a891790&is=6a87c610&hm=023ac31af69e956f69a04a71e86c570019348445c4a5130a0e34cb5f6ca9ffd1&")

        embed.set_author(icon_url=str(self.bot.user.display_avatar.url), name=str(self.bot.user))

        embed.add_field(
            name = "Nama",
            value = "Aika Yokina",
            inline = True
        )
        embed.add_field(
            name = "Umur",
            value = "17 tahun",
            inline = True
        )
        embed.add_field(
            name = "Jenis kelamin",
            value = "Perempuan",
            inline = True
        )
        embed.add_field(
            name = "Tinggi",
            value = "154cm",
            inline = True
        )
        embed.add_field(
            name = "Berat",
            value = "~47kg",
            inline = True
        )
        embed.add_field(
            name = "Kebangsaan",
            value = "Indonesia",
            inline = True
        )

        embed.set_footer(text="Untuk info statisik bot, cek ak!stats")

        await ctx.send(embed=embed)
        print("[Aika] Command about dieksekusi")

async def setup(bot: commands.Bot):
    await bot.add_cog(About(bot))