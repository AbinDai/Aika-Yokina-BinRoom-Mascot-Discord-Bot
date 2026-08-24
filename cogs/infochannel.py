import discord
from discord.ext import commands
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

IMAGE_PATH = BASE_DIR / "assets" / "info channel.png"

class InfoChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="post_infochannel", description="Ngirim chat info channel ke channel info-server")
    @commands.has_permissions(administrator=True)
    async def post_infochannel(self, ctx):
        ambil_gambar = discord.File(IMAGE_PATH, filename="info channel.png")

        embed = discord.Embed(
            description =
            "<#904972136328888343>: Halaman awal.\n"
            "<#904973494813614141>: Log keluar dan masuk member.\n"
            "<#1498144198577356831>: Live preview para member yang sedang online, dibagi atas tiga kategori (online, idle, DND).\n"
            "||⚠️ PERHATIAN: CHANNEL INI JUGA SEBAGAI HONEYPOT ALIAS JEBAKAN UNTUK MENANGKAP AKUN BERMASALAH YANG MENGIRIM LINK PHISHING. JIKA ANDA SEDANG TIDAK DI-HACK ATAU AKUN AMAN SEPENUHNYA DI TANGAN ANDA, JANGAN MENGIRIM APAPUN DI SINI ATAU NANTI AKAN DI-TIMEOUT 28 HARI. HUBUNGI STAF JIKA TIDAK DISENGAJA.||",
            color = discord.Color(0xFFF3FD)
        )
        embed.add_field( #1
            name="Halaman Rumah",
            value=
            "<#904972338687270992>: Info lengkap tentang server, aturan, dan keterangan role serta channel\n"
            "<#904973389784031242>: Pengumuman server. Infonya tentang pembaruan server, event baru, dll.\n"
            "<#904992841753841694>: Galeri dan koleksi lengkap gambar-gambar maskot server, Aika Yokina, beserta info singkat tentangnya.\n"
            "<#916543184434253856>: Kompilasi momen-momen kocak.",
            inline=False)
        embed.add_field( #2
            name="Lantai 1",
            value=
            "<#1191881505786560572>: Silakan perkenalkan diri di sini. *Tak kenal maka tak sayang*, ea :v\n"
            "<#904972673124282428>: General 1. Di sini tempat chatting utama.\n"
            "<#904972771816243230>: General 2. Di sini alternatifnya agar menghindari pemotongan topik dll.\n"
            "<#904973034920767499>: Tempat khusus untuk akses perintah bot.\n"
            "<#1053584751904174130>: Khusus untuk spam.",
            inline=False)
        embed.add_field( #3
            name="Lantai 2",
            value
            ="<#904972956281757706>: Tempat meme.\n"
            "<#904972979811807252>: Pamerkan karyamu! Ilustrasi, fotografi, apapun itu.\n"
            "<#904992619468308480>: Khusus untuk MEE6 mem-posting info kenaikan level para member.\n"
            "<#904973095406821376>: Khusus promosi. Silakan ngiklan di sini. Tapi ingat, 2 jam per pesan promosi, dan notifnya akan masuk ke semua orang (setara dengan nge-tag `@everyone`, jadi gunakan dengan bijak).",
            inline=False)
        embed.add_field( #4
            name="Lantai 3",
            value
            ="ℹ️ Di server ini, kita cuma pakai 1 room aja untuk menghemat tempat. Kalau butuh lebih, kami nyediain opsi untuk bikin VC sendiri.\n\n"
            "ℹ️ Di server ini juga, kami pakai <@513423712582762502>. Kalau kamu VC-an dan tidak sedang open mic, pesanmu bakal dibacain sama bot-nya, jadinya memudahkan bagiyang lagi main game dll. Gaperlu harus liat chat secara manual.\n\n"
            "<#905053252872179722>: Tempat atur VC kustom mu. Bebas mau namain apa, pokoknya atur di sini.\n"
            "<#905000403987488769>: Kalau sedang VC-an, silakan pakai channel ini untuk ngobrol.\n"
            "<#1101103048291536976>: VC utama.\n"
            "<#1118452853636333620>: Di sini kamu bisa bikin VC sendiri. VC ini dipegang oleh <@472911936951156740>. Kalau kamu join di sini, kamu akan dibuatkan VC baru oleh bot-nya dan akan langsung dipindahkan ke situ secara otomatis.",
            inline=False)
        
        embed.set_footer(text="Informasi dari masing-masing channel juga bisa dibaca di bio khususnya. Dan untuk kategori Bawah Tanah, well, self-explanatory aja yah.")

        channel = self.bot.get_channel(904972338687270992)
        if channel is None:
            await ctx.send("❌ I couldn't find the target channel.")
            return
        
        await channel.send(file=ambil_gambar)
        await channel.send(embed=embed)

        await ctx.send(f"✅ Pesan info channel sukses terkirim di channel {channel.mention}.")

async def setup(bot):
    await bot.add_cog(InfoChannel(bot))