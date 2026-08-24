import discord, time, datetime, platform, psutil, urllib.request, json, socket, os
from discord.ext import commands

waktu_mulai = time.time()
psutil.cpu_percent()

def get_container_ram_limit() -> float:
    """Mengecek batasan RAM dari cgroups (Docker/LXC) dalam MB."""
    cgroup_paths = [
        "/sys/fs/cgroup/memory.max",
        "/sys/fs/cgroup/memory/memory.limit_in_bytes"
    ]
    for path in cgroup_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    val = f.read().strip()
                    if val != "max" and val.isdigit():
                        limit_bytes = int(val)
                        if limit_bytes < (1024 ** 4):  # Abaikan jika nilai unlimited bawaan (> 1 TB)
                            return limit_bytes / (1024 * 1024)
            except Exception:
                pass
    return psutil.virtual_memory().total / (1024 * 1024)

def get_hosting_provider() -> str:
    # nge-fetch provider host ISP atau provider; kalau gabisa, balik ke hostname sistem
    # cara 1: cari tau network ISP/ASN 
    try:
        req = urllib.request.Request("http://ip-api.com/json/?fields=isp,org,as", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            data = json.loads(response.read().decode())
            provider = data.get('org') or data.get('isp') or ""
            
            # bersihin nomor prefix ASN kalo ada
            if provider.startswith("AS"):
                provider = " ".join(provider.split()[1:])
            
            # normalisasi nama provider
            provider_upper = provider.upper()
            if "SNAJU DEVELOPMENT" in provider_upper:
                return "HeavenCloud"
            elif "TELKOM INDONESIA" in provider_upper:
                return "lokal/self-hosted"
            
            if provider:
                return provider
    except Exception:
        pass
    # cara 2: node sistem / balik ke hostname (fallback)
    try:
        hostname = socket.gethostname()
        if hostname:
            return hostname
    except Exception:
        pass
    return "lokal/self-hosted"

def make_bar(persen:float, panjang:int=11) -> str:
    terisi = int(round(panjang * persen / 100))
    return "█" * terisi + "░" * (panjang - terisi)

def format_size(mb_value: float) -> str:
    #format MB ke GB kalo kegedean
    if mb_value >= 1024:
        return f"{mb_value / 1024:.1f} GB"
    return f"{int(mb_value)} MB"

class LinksView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Source code (repositori GitHub)", url="https://github.com/AbinDai/Aika-Yokina-BinRoom-Mascot-Discord-Bot/"))
        self.add_item(discord.ui.Button(label="Gabung dengan BinRoom", url="https://discord.gg/cDMxkAkMYm"))
        self.add_item(discord.ui.Button(label="Info hosting", url="https://heavencloud.in/"))

class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="stats", description="Liat statistik tentang bot ini.")
    async def stats(self, ctx:commands.Context):
        # langsung defer biar ga kena aturan timeout 3 detik nya discord
        await ctx.defer()

        guild_color = ctx.guild.me.color if ctx.guild else 0xD774C5
        
        embed = discord.Embed(title="Informasi sistem Aika", color=guild_color)

        avatar = self.bot.user.display_avatar.url
        embed.set_author(name=str(self.bot.user), icon_url=avatar)
        embed.set_thumbnail(url=avatar)

        # Row 1: Identity
        app_info = await self.bot.application_info()
        owner_name = app_info.owner.name if app_info.owner else "arumugi_4405"

        embed.add_field(name="Nama", value=self.bot.user.name, inline=True)
        embed.add_field(name="Pengembang", value=f"@{owner_name}", inline=True)
        embed.add_field(name="Dibuat", value=discord.utils.format_dt(self.bot.user.created_at, style="d"), inline=True)

        # Row 2: Runtime
        waktu_aktif = str(datetime.timedelta(seconds=int(round(time.time() - waktu_mulai))))
        embed.add_field(name="ID Bot", value=str(self.bot.user.id), inline=True)
        embed.add_field(name="Waktu Aktif", value=waktu_aktif, inline=True)
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)

        # Row 3: Environment
        embed.add_field(name="Bahasa Program", value=f"Python v{platform.python_version()}", inline=True)
        embed.add_field(name="Library", value=f"discord.py v{discord.__version__}", inline=True)
        embed.add_field(name="Sistem Operasi", value=platform.system(), inline=True)

        # info ram
        ram_info = psutil.virtual_memory()

        #a kurasi alokasi RAM container vs Host
        cgroup_limit_mb = get_container_ram_limit() 
        ram_total_mb = min(ram_info.total / (1024 * 1024), cgroup_limit_mb) 
        ram_avail_mb = ram_info.available / (1024 * 1024) 
        ram_used_mb = max(0.0, ram_total_mb - ram_avail_mb) 
        ram_pct = int((ram_used_mb / ram_total_mb) * 100) if ram_total_mb > 0 else 0 

        ram_total_mb = int(ram_info.total / (1024*1024))
        ram_used_mb = int(ram_info.used / (1024*1024))
        ram_pct = int(ram_info.percent)

        # info disk
        disk_info = psutil.disk_usage('/')
        disk_total_mb = int(disk_info.total / (1024*1024))
        disk_used_mb = int(disk_info.used / (1024*1024))
        disk_pct = int(disk_info.percent)

        # handling cpu dinamis
        is_cloud = ram_total_mb < 1000
        cpu_limit = 60.0 if is_cloud else 100.0
        
        cpu_raw = psutil.cpu_percent()
        cpu_rel_pct = min((cpu_raw / cpu_limit) * 100, 100.0)

        # blok visual 
        cpu_str  = f"{int(cpu_raw)}%"
        ram_str  = f"{format_size(ram_used_mb)} ({ram_pct}%)"
        disk_str = f"{format_size(disk_used_mb)} ({disk_pct}%)"

        sys_info = (
            "```\n"
            f"CPU : {cpu_str:<15} [{make_bar(cpu_rel_pct)}] {int(cpu_limit)}%\n"
            f"RAM : {ram_str:<15} [{make_bar(ram_pct)}] {format_size(ram_total_mb)}\n"
            f"Disk: {disk_str:<15} [{make_bar(disk_pct)}] {format_size(disk_total_mb)}\n"
            "```"
        )
        embed.add_field(name="Alokasi Sistem", value=sys_info, inline=False)

        # info cpu ram disk lebih lanjut
        proc = psutil.Process()
        bot_ram_mb = proc.memory_info().rss / (1024 * 1024)
        bot_ram_pct = (bot_ram_mb / ram_total_mb) * 100

        try:
            disk_io = psutil.disk_io_counters()
            read_gb = disk_io.read_bytes / (1024 ** 3)
            write_gb = disk_io.write_bytes / (1024 ** 3)
            io_str = f"{read_gb:.1f}G R / {write_gb:.1f}G W"
        except Exception:
            io_str = "N/A"


        # row 5: field khusus info cpu
        cpu_cores = psutil.cpu_count(logical=True) or "N/A"
        #fetch clock speed secara aman bniar sysfs ga gampang ngehang 
        try:
            freq_info = psutil.cpu_freq()
            cpu_freq = f"{freq_info.current:.0f} MHz" if freq_info and freq_info.current else "N/A"
        except Exception:
            cpu_freq = "N/A"

        embed.add_field(
            name="CPU",
            value=(
                f"**Cores:** {cpu_cores} Threads\n"
                f"**Clock:** {cpu_freq}\n"
                f"**Batas:** {int(cpu_limit)}%"
            ),
            inline=True
        )

        # field khusus info ram
        ram_avail_mb = int(ram_info.available / (1024*1024))
        embed.add_field(
            name="RAM",
            value=(
                f"**Digunakan:** {format_size(bot_ram_mb)}\n"
                f"**Tersisa:** {format_size(ram_avail_mb)}\n"
                f"**Terpakai:** {bot_ram_pct:.1f}%"
            ),
            inline=True
        )

        # fetch tipe file sistem (kyk NTFS, ext4)
        try:
            partitions = psutil.disk_partitions()
            # cari akar sistem '/' or 'C:\\'
            root_fs = next((p.fstype for p in partitions if p.mountpoint in ('/', 'C:\\')), "N/A")
            if not root_fs or root_fs == "N/A":
                root_fs = partitions[0].fstype if partitions else "N/A"
        except Exception:
            root_fs = "N/A"

        # format I/O secara bersih
        try:
            disk_io = psutil.disk_io_counters()
            read_gb = disk_io.read_bytes / (1024 ** 3)
            write_gb = disk_io.write_bytes / (1024 ** 3)
            io_str = f"R: {read_gb:.1f}GB, W: {write_gb:.1f}GB"
        except Exception:
            io_str = "N/A"

        # cari tau jenis filesystem 
        try:
            partitions = psutil.disk_partitions()
            root_fs = next((p.fstype for p in partitions if p.mountpoint in ('/', 'C:\\')), "N/A")
            if not root_fs or root_fs == "N/A":
                root_fs = partitions[0].fstype if partitions else "N/A"
        except Exception:
            root_fs = "N/A"

        # field khusus info disk
        disk_free_mb = int(disk_info.free / (1024*1024))
        embed.add_field(
            name="Disk",
            value=(
                f"**Tersedia:** {format_size(disk_free_mb)}\n"
                f"**Format:** {root_fs.upper()}\n"
                f"**I/O:** {io_str}"
            ),
            inline=True
        )

        nama_hostingan = get_hosting_provider()

        embed.set_footer(text=f"Aika di-hosting di: {nama_hostingan}", icon_url="https://cdn.discordapp.com/attachments/863959650448703538/1540201066455371888/bunga.png?ex=6a8b11c5&is=6a89c045&hm=2f7837e9e91cf914975584cb8ba5f001f80ea54d36c86e643547b1f23a111b26&")

        is_admin = getattr(ctx.author.guild_permissions, "administrator", False) if ctx.guild else False
        
        await ctx.send(
            content="...ngapain liat2 internalku? Gak penting amat 🧐" if not is_admin else None,
            embed=embed,
            view=LinksView(),
        )
        print("[Aika] Command stats dieksekusi")

async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))