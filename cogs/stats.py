import discord, time, datetime, platform, psutil, urllib.request, json, socket, os, shutil
from discord.ext import commands

waktu_mulai = time.time()

# Inisialisasi pelacakan CPU proses awal
proc = psutil.Process(os.getpid())
proc.cpu_percent()

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
                        if limit_bytes < (1024 ** 4):  # Abaikan jika > 1 TB
                            return limit_bytes / (1024 * 1024)
            except Exception:
                pass
    return psutil.virtual_memory().total / (1024 * 1024)

def get_container_disk_limits() -> tuple[float, float]:
    """
    Mengambil total quota disk container dan sisa quota dalam MB.
    Mengutamakan ENV `SERVER_DISK` (Pterodactyl), lalu fallback ke cgroup/shutil.
    """
    bot_used_mb = get_bot_directory_size_mb(".")
    
    # 1. Cek jika host menyediakan ENV disk quota (Pterodactyl/Custom ENV)
    env_disk = os.getenv("SERVER_DISK")  # Pterodactyl menyediai variabel ini di beberapa setup
    if env_disk and env_disk.isdigit():
        total_mb = float(env_disk)
        return total_mb, max(0.0, total_mb - bot_used_mb)

    # 2. Cek drive via shutil
    try:
        total, used, free = shutil.disk_usage(".")
        total_mb = total / (1024 * 1024)
        
        # Jika berada di container cloud (RAM < 2GB) tapi disk terbaca raksasa (>100GB host leak)
        ram_limit = get_container_ram_limit()
        if total_mb > 100000 and ram_limit < 2000:
            total_mb = 1024.0  # Default container quota fallback
    except Exception:
        total_mb = 1024.0

    free_mb = max(0.0, total_mb - bot_used_mb)
    return total_mb, free_mb

def get_bot_directory_size_mb(path: str = ".") -> float:
    """Menghitung total ukuran berkas bot di direktori aktif."""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except Exception:
        pass
    return total_size / (1024 * 1024)

def get_hosting_provider() -> str:
    try:
        req = urllib.request.Request("http://ip-api.com/json/?fields=isp,org,as", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            data = json.loads(response.read().decode())
            provider = data.get('org') or data.get('isp') or ""
            
            if provider.startswith("AS"):
                provider = " ".join(provider.split()[1:])
            
            provider_upper = provider.upper()
            if "SNAJU DEVELOPMENT" in provider_upper:
                return "HeavenCloud"
            elif "IPXO GTT" in provider_upper:
                return "Wispbyte"
            elif "TELKOM INDONESIA" in provider_upper:
                return "lokal/self-hosted"
            
            if provider:
                return provider
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        if hostname:
            return hostname
    except Exception:
        pass
    return "lokal/self-hosted"

def make_bar(persen: float, panjang: int = 11) -> str:
    terisi = int(round(panjang * max(0.0, min(persen, 100.0)) / 100))
    return "█" * terisi + "░" * (panjang - terisi)

def format_size(mb_value: float) -> str:
    if mb_value >= 1024:
        return f"{mb_value / 1024:.1f} GB"
    return f"{int(mb_value)} MB"

class LinksView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(discord.ui.Button(label="Source code (repositori GitHub)", url="https://github.com/AbinDai/Aika-Yokina-BinRoom-Mascot-Discord-Bot/"))
        self.add_item(discord.ui.Button(label="Gabung dengan BinRoom", url="https://discord.gg/cDMxkAkMYm"))

        link_info_hosting = get_hosting_provider()
        if "HeavenCloud" in link_info_hosting:
            self.add_item(discord.ui.Button(label="Info hosting", url="https://heavencloud.in/"))
        elif "Wispbyte" in link_info_hosting:
            self.add_item(discord.ui.Button(label="Info hosting", url="https://wispbyte.com/"))
        

class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="stats", description="Liat statistik tentang bot ini.")
    async def stats(self, ctx: commands.Context):
        await ctx.defer()
        
        embed = discord.Embed(title="Informasi sistem Aika", color=0xD675C1)

        avatar = self.bot.user.display_avatar.url
        embed.set_author(name=str(self.bot.user), icon_url=avatar)
        embed.set_thumbnail(url=avatar)

        # Row 1: Identity
        app_info = await self.bot.application_info()
        owner_name = f"<@{app_info.owner.id}>" if app_info.owner else "@arumugi_4405"

        embed.add_field(name="Nama", value=self.bot.user.name, inline=True)
        embed.add_field(name="Pengembang", value=owner_name, inline=True)
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

        # --- ISOLATED CONTAINER METRICS ---
        process = psutil.Process(os.getpid())
        
        # 1. CPU Usage
        cpu_cores = psutil.cpu_count(logical=True) or 1
        raw_cpu = process.cpu_percent(interval=None)
        bot_cpu_pct = raw_cpu / cpu_cores

        # 2. RAM Usage & Container Limits
        ram_total_mb = get_container_ram_limit()
        bot_ram_mb = process.memory_info().rss / (1024 * 1024)
        ram_avail_mb = max(0.0, ram_total_mb - bot_ram_mb)
        bot_ram_pct = (bot_ram_mb / ram_total_mb) * 100 if ram_total_mb > 0 else 0.0

        # 3. Disk Usage & Container Limits
        disk_total_mb, disk_free_mb = get_container_disk_limits()
        bot_disk_mb = get_bot_directory_size_mb(".")
        bot_disk_pct = (bot_disk_mb / disk_total_mb) * 100 if disk_total_mb > 0 else 0.0

        # Dynamic cloud detection & limits
        is_cloud = ram_total_mb < 1000
        cpu_limit = 60.0 if is_cloud else 100.0
        cpu_rel_pct = min((bot_cpu_pct / cpu_limit) * 100, 100.0)

        # Formatted system overview block
        cpu_str  = f"{bot_cpu_pct:.2f}%"
        ram_str  = f"{format_size(bot_ram_mb)} ({bot_ram_pct:.1f}%)"
        disk_str = f"{format_size(bot_disk_mb)} ({bot_disk_pct:.2f}%)"

        sys_info = (
            "```\n"
            f"CPU : {cpu_str:<15} [{make_bar(cpu_rel_pct)}] {int(cpu_limit)}%\n"
            f"RAM : {ram_str:<15} [{make_bar(bot_ram_pct)}] {format_size(ram_total_mb)}\n"
            f"Disk: {disk_str:<15} [{make_bar(bot_disk_pct)}] {format_size(disk_total_mb)}\n"
            "```"
        )
        embed.add_field(name="Penggunaan Bot", value=sys_info, inline=False)

        # Field CPU
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

        # Field RAM
        embed.add_field(
            name="RAM",
            value=(
                f"**Digunakan:** {format_size(bot_ram_mb)}\n"
                f"**Tersisa:** {format_size(ram_avail_mb)}\n"
                f"**Terpakai:** {bot_ram_pct:.1f}%"
            ),
            inline=True
        )

        # Field Disk
        try:
            partitions = psutil.disk_partitions()
            root_fs = next((p.fstype for p in partitions if p.mountpoint in ('/', 'C:\\')), "N/A")
            if not root_fs or root_fs == "N/A":
                root_fs = partitions[0].fstype if partitions else "N/A"
        except Exception:
            root_fs = "N/A"

        try:
            disk_io = process.io_counters()
            read_mb = disk_io.read_bytes / (1024 ** 2)
            write_mb = disk_io.write_bytes / (1024 ** 2)
            io_str = f"R: {read_mb:.1f}MB, W: {write_mb:.1f}MB"
        except Exception:
            io_str = "N/A"

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
