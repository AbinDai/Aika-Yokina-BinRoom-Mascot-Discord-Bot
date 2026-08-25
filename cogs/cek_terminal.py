import discord, sys, io, re, collections
from discord import app_commands
from discord.ext import commands
from typing import Optional

# ring buffer global buat nampung output stdout dan stderr di memori
TAMPUNGAN_LOG = collections.deque(maxlen=100)

class PengalirLog(io.TextIOBase): #ngalirin output terminal ke terminal asli sekaligus ke buffer memori
    def __init__(self, stream_asli):
        self.stream_asli = stream_asli

    def write(self, buf: str) -> int:
        self.stream_asli.write(buf)
        for baris in buf.splitlines():
            if baris.strip():
                TAMPUNGAN_LOG.append(baris)
        return len(buf)

    def flush(self) -> None:
        self.stream_asli.flush()

#belokin stdout dan stderr bawaan lewat pengalir log
sys.stdout = PengalirLog(sys.stdout)
sys.stderr = PengalirLog(sys.stderr)

class LogTerminal(commands.Cog): #module khusus dev buat ngeliat log terminal langsung dari diskor
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        
        self.ANSI = {
            "reset": "\x1b[0m",
            "bold": "\x1b[1m",
            "merah": "\x1b[0;31m",
            "merah_tebal": "\x1b[1;31m",
            "hijau": "\x1b[0;32m",
            "kuning": "\x1b[0;33m",
            "sian": "\x1b[0;36m",
            "pink": "\x1b[0;35m",
            "pink_tebal": "\x1b[1;35m",
            "abu": "\x1b[0;30m",
        }

        self.pola_eror = [
            (r"\b(KeyboardInterrupt|SystemExit|CancelledError)\b", self.ANSI["merah_tebal"]),
            (r"\b(CommandInvokeError|HTTPException|NotFound|Forbidden|DiscordException|ClientConnectorError)\b", self.ANSI["pink_tebal"]),
            (r"\b(SyntaxError|IndentationError|TypeError|ValueError|KeyError|AttributeError|ImportError|ModuleNotFoundError|NameError|ZeroDivisionError|FileNotFoundError|UnboundLocalError)\b", self.ANSI["merah"]),
            (r"\b(UserWarning|DeprecationWarning|RuntimeWarning|Warning)\b", self.ANSI["kuning"]),
            (r"\b(200 OK|201 Created)\b", self.ANSI["hijau"]),
            (r"\b(400|401|403|404|429|500|502|503)\b", self.ANSI["merah"]),
        ]

    def format_log_ansi(self, teks_mentah:str) -> str: #nge-parse teks mentah terus ditempelin warna ANSI
        baris_terformat = []

        for baris in teks_mentah.splitlines():
            #cek kalo barisnya ada indikasi eror
            is_baris_eror = any(
                kw_eror in baris.lower() 
                for kw_eror in ["eror", "error", "gagal", "exception", "traceback"]
            ) or baris.strip().startswith("[Groq]")

            # format tag khusus [Aika] dan [Groq]
            # merah klo baris eror, pink kalau normal
            if "[Aika]" in baris:
                warna_tag = self.ANSI["merah_tebal"] if is_baris_eror else self.ANSI["pink_tebal"]
                baris = baris.replace("[Aika]", f"{warna_tag}[Aika]{self.ANSI['reset']}")

            if "[Groq]" in baris:
                baris = baris.replace("[Groq]", f"{self.ANSI['merah_tebal']}[Groq]{self.ANSI['reset']}")

            # format path file traceback
            if baris.strip().startswith("File "):
                baris = re.sub(
                    r'File "(.*?)"',
                    f'File "{self.ANSI["sian"]}\\1{self.ANSI["reset"]}"',
                    baris
                )
                baris = re.sub(
                    r'line (\d+)',
                    f'line {self.ANSI["kuning"]}\\1{self.ANSI["reset"]}',
                    baris
                )
                baris = re.sub(
                    r'in ([\w<>]+\b)',
                    f'in {self.ANSI["pink_tebal"]}\\1{self.ANSI["reset"]}',
                    baris
                )

            # format marker shell / venv
            elif any(marker in baris for marker in ("PS ", "(.venv)", "venv", "$")):
                baris = f"{self.ANSI['abu']}{baris}{self.ANSI['reset']}"

            # format header traceback
            elif baris.startswith("Traceback"):
                baris = f"{self.ANSI['bold']}{self.ANSI['kuning']}{baris}{self.ANSI['reset']}"

            # highlight exception standar sama status code
            else:
                for pola, warna in self.pola_eror:
                    if re.search(pola, baris):
                        baris = re.sub(pola, f"{warna}\\1{self.ANSI['reset']}", baris)
                        break

            baris_terformat.append(baris)

        return "\n".join(baris_terformat)

    @commands.hybrid_command(name="cek_terminal", description="Ngeliat terminal log (HANYA DEV)")
    @commands.is_owner()
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(jumlah_baris="Jumlah baris log yang mau diambil dari memori (default: 8, max: 50)")
    async def cek_terminal(self, ctx: commands.Context, jumlah_baris: Optional[int] = None):
        if jumlah_baris is not None:
            judul_embed = f"Terminal Aika ({jumlah_baris} baris)"
            baris_diambil = jumlah_baris
        else:
            judul_embed = "Terminal Aika"
            baris_diambil = 8 

        total_baris = max(1, min(baris_diambil, 50)) #pembatas smpe 50
        output_mentah = list(TAMPUNGAN_LOG)[-total_baris:] 
        
        if not output_mentah:
            await ctx.send("Belum ada log yang tersimpan di memori.", ephemeral=True) 
            return

        warna_embed = discord.Color.from_str("#D675C1") 

        pola_deteksi_eror = r"(Traceback|Error|Exception|KeyboardInterrupt|SystemExit|HTTPException|Forbidden|NotFound|400|401|403|404|429|500|\[Groq\]|Gagal|eror)" 

        if any(re.search(pola_deteksi_eror, baris, re.IGNORECASE) for baris in output_mentah): 
            warna_embed = discord.Color.red() #ganti jadi merah kalo ada eror

        log_terformat = self.format_log_ansi("\n".join(output_mentah)) 

        if len(log_terformat) > 3900: 
            log_terformat = log_terformat[-3900:] 
            if "\x1b" in log_terformat[:8] and "[" not in log_terformat[:8]: 
                log_terformat = log_terformat[log_terformat.find("m") + 1:] 

        embed = discord.Embed(
            title=judul_embed,
            description=f"```ansi\n{log_terformat}\n```", #[cite: 4]
            color=warna_embed 
        )

        await ctx.send(embed=embed, ephemeral=True)

    @cek_terminal.error
    async def error_cek_terminal(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.NotOwner):
            await ctx.send("❌ Gaboleh, cuma owner yang boleh pake ini command.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(LogTerminal(bot))