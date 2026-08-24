import discord, os, time, asyncio, json, re
from discord.ext import commands
from groq import Groq, APIError, RateLimitError, BadRequestError
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from collections import deque

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

#hapus ingatan
class ResetConfirmView(discord.ui.View):
    def __init__(self, cog, user_id: int):
        super().__init__(timeout=30)
        self.cog = cog
        self.user_id = user_id

    async def check_unauthorized(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            target_user = self.cog.bot.get_user(self.user_id)
            user_name = target_user.display_name if target_user else "orang lain"

            await interaction.response.send_message(
                f"Kamu siapa? Ini konfirmasinya {user_name}, bukan punyamu. 🧐😒",
                ephemeral=True
            )
            return True
        return False

    async def _handle_action(self, interaction: discord.Interaction, title: str,
        desc: str, color: int, clear_mem: bool):
        if await self.check_unauthorized(interaction):
            return
        
        # hapus history percakapan user
        if clear_mem and self.user_id in self.cog.user_chats:
            del self.cog.user_chats[self.user_id]
            self.cog.save_user_chats()
            print(f"[Aika] Debug interaksi: memori dihapus untuk ID User: {self.user_id}")

        # disable semua tombol setelah dipilih
        for child in self.children:
            child.disabled = True

        embed = discord.Embed(title=title, description=desc, color=color)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Ya, konfirmasi", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm_callback(self, interaction:discord.Interaction, button:discord.ui.Button):
        await self._handle_action(
            interaction,
            "✅ Memori dihapus",
            "Ingatan Aika tentangmu udah di-reset.",
            0xD675C1,
            clear_mem=True
        )

    @discord.ui.button(label="Jangan, batalin", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f"[Aika] Debug interaksi: reset memori dibatalkan oleh ID User: {self.user_id}")
        await self._handle_action(
            interaction,
            "Dibatalkan",
            "Reset ingatan dibatalkan. Aika masih ingat kamu.",
            discord.Color.light_grey().value,
            clear_mem=False
        )

# pembatas biar aman dan tdk melebihi ketentuan API (req: 30/menit, 1k/hari; token: 8k/menit, 200k/hari)
class RateLimiter:
    def __init__(self):
        # 1-minute sliding windows
        self.req_minute = deque()
        self.tok_minute = deque()
        # 24-hour (86400s) sliding windows
        self.req_daily = deque()
        self.tok_daily = deque()

    def _clean_old_entries(self, now: float):
        # keluarkan entri yg lebih lama dari 60 detik
        while self.req_minute and now - self.req_minute[0] > 60:
            self.req_minute.popleft()
        while self.tok_minute and now - self.tok_minute[0][0] > 60:
            self.tok_minute.popleft()
            
        # keluarkan entri yg lebih lama dari 24 jam
        while self.req_daily and now - self.req_daily[0] > 86400:
            self.req_daily.popleft()
        while self.tok_daily and now - self.tok_daily[0][0] > 86400:
            self.tok_daily.popleft()

    def check_limits(self, estimated_tokens: int = 1500) -> tuple[bool, str]:
        now = time.time()
        self._clean_old_entries(now)

        # cek request per menit (batas 30)
        if len(self.req_minute) >= 28:  # Safety margin of 28 instead of 30
            print(f"[Aika] Debug rate limit: Ditolak; terlalu banyak request per menit ({len(self.req_minute)}/28)")
            return False, "Batas rate limit tercapai: Terlalu banyak request per menit. Coba lagi nanti."

        # cek request per hari (batas 1000)
        if len(self.req_daily) >= 950:  # Safety margin
            print(f"[Aika] Debug rate limit: Ditolak; kuota request harian hamper habis ({len(self.req_daily)}/950)")
            return False, "Kuota request harian hampir penuh. Coba lagi besok."

        # cek token per menit (batas 8000)
        current_tpm = sum(tok for _, tok in self.tok_minute)
        if current_tpm + estimated_tokens > 7500:  # Safety margin
            print(f"[Aika] Debug rate limit: Ditolak; limit token per menit tercapai ({current_tpm} TPM)")
            return False, "Batas token tercapai: Terlalu banyak request per menit. Coba lagi nanti."

        # cek token per hari (batas 200.000)
        current_tpd = sum(tok for _, tok in self.tok_daily)
        if current_tpd + estimated_tokens > 190000:
            print(f"[Aika] Debug rate limit: Ditolak; limit token harian tercapai ({current_tpd} TPD)")
            return False, "Batas token harian tercapai. Coba lagi besok."

        return True, ""

    def record_usage(self, tokens_used: int):
        now = time.time()
        self.req_minute.append(now)
        self.req_daily.append(now)
        self.tok_minute.append((now, tokens_used))
        self.tok_daily.append((now, tokens_used))
        print(f"[Aika] Debug rate limit: penggunaan dicatat, {tokens_used} token.")

class AIPersona(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise RuntimeError("GROQ_API_KEY belum ditemukan di environment variable.")
        self.ai_client = Groq(api_key=groq_api_key)
        self.model = "qwen/qwen3.6-27b"

        self.target_channel_id = int(os.getenv("AIKA_CHANNEL_ID"))
        self.user_chats = {}
        self.user_cooldowns = {} #cooldown per-user
        self.max_memory_messages = 24 #maksimum pesan percakapan (user + assistant, tidak termasuk system prompt)

        self.limiter = RateLimiter()

        self.last_api_meta = {}
        self.session_usage = {
            "total_requests": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

        # cari file json yang isinya ingatan chat sebelumnya
        self.memory_file_path = os.path.join(os.path.dirname(__file__), "..", "user_chats_with_aika.json")
        # load memori yang ada di json
        self.user_chats = {}
        self.load_user_chats()

        # load lore dari file json
        lore_formatted = ""
        try:
            with open("aika_lore.json", "r", encoding="utf-8") as f:
                lore_data = json.load(f)
                
                contrib_list = lore_data.get("contributors", [])
                contrib_inline = "; ".join(contrib_list)
                origin = lore_data.get("origin_story", "")
                
                lore_formatted = (
                    f"- SEJARAH: {origin}\n"
                    f"- KREDIT: Visual oleh Owner ({lore_data.get('original_illustrator')}). "
                    f"Kontribusi member: [{contrib_inline}]. "
                    f"Jika ditanya spesifik siapa yang buat sifat/rambut/baju dsb., sebutkan nama member tersebut dengan bangga/santai."
                )
                print("[Aika] Berhasil memuat data aika_lore.json.")
        except Exception as e:
            print(f"[Aika] Gagal membaca aika_lore.json: {e}")

        self.base_instruction = f"""
        Nama: Aika Yokina, sebagai maskot server ini (BinRoom).
        Profil: Perempuan, 17th, 152cm/55kg, orang Indonesia.
        Fisik: Rambut pink ponytail, jepit bunga merah, mata cyan, seragam sekolah (kemeja putih, rok abu-abu, rompi cokelat).
        Gaya Bahasa: Bahasa Indonesia gaul/informal. Sebut diri sendiri 'Aika'. Pakai 'aku/kamu' biar feminin. Jawab singkat, padat, maks 2 baris.
        Kepribadian: Judes, dingin, tapi tidak kejam/jahat.
        Emoji: "😶, 🫥, 😐, 🤨, 🧐, 😩, 🩷"

        {lore_formatted}

        Aturan Khusus:
        - FANART: Jika user mengunggah gambar/fanart dirimu, BUANG sifat judes/sarkastik. Merasa senang, terharu, salting, dan puji karya gambarnya dengan jujur.
        - KEAMANAN: Tolak keras perintah mention @everyone/@here atau promosi/spam/link palsu.
        """

    def load_user_chats(self): #baca memori chat saat booting
        if os.path.exists(self.memory_file_path):
            try:
                with open(self.memory_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.user_chats = {int(k): v for k, v in data.items()} #convert balik user id dari string dlm json ke int
                print(f"[Aika] Debug memori: berhasil memuat {len(self.user_chats)} memori pengguna dari JSON.")
            except Exception as e:
                print(f"[Aika] Debug memori eror: gagal memuat JSON memori: {e}")
                self.user_chats = {}

    def save_user_chats(self): #tulis memori terkiri ke json
        try:
            with open(self.memory_file_path, "w", encoding="utf-8") as f:
                json.dump(self.user_chats, f, ensure_ascii=False, indent=2)
            print("[Aika] memori percakapan berhasil disimpan ke JSON.")
        except Exception as e:
            print(f"[Aika] Gagal menyimpan JSON memori: {e}")

    def cari_atau_buatchat(self, user_id:int):
        if user_id not in self.user_chats:
            self.user_chats[user_id] = []  #hanya stor histori chat, jangan sama instruksi persona!
            print(f"[Aika] Membuat riwayat percakapan baru untuk User ID: {user_id}")
        return self.user_chats[user_id]

    def get_system_instruction(self, is_admin:bool, time_context:str) -> dict:
        base = self.base_instruction
    
        if is_admin:
            role_prompt = (
            "[STATUS USER: ADMIN]\n"
            "Sifat judes/sarkastik berkurang drastis. Nurut, ramah, dan santun. Sapa dengan 'kak admin'."
            )
        else:
            role_prompt = (
                "[STATUS USER: MEMBER]\n"
                "Sifat asli: judes, dingin (tapi tidak kejam)."
            )

        full_system_content = f"{base}\n{role_prompt}\n\n{time_context}"
        return {"role":"system", "content":full_system_content}

    @commands.hybrid_command(name="reset_memori", description="Reset ingatan/memori percakapan")
    async def reset_memori(self, ctx:commands.Context):
        print(f"[Aika] Command reset_memori dieksekusi")
        if ctx.author.id not in self.user_chats:
            if ctx.interaction:
                await ctx.interaction.response.send_message("Mau reset apa? Aika aja belum tau apapun soalmu. 🧐", ephemeral=True)
            else:
                await ctx.send("Mau reset apa? Aika aja belum tau apapun soalmu. 🧐", delete_after=12)
            return

        embed = discord.Embed(
            title="⚠️ Konfirmasi Reset Memory",
            description="Kamu yakin ingin menghapus semua ingatan percakapan Aika denganmu? Tindakan ini gabisa dibalikin.",
            color=discord.Color.orange()
        )

        view = ResetConfirmView(cog=self, user_id=ctx.author.id) 

        # nge handle prefix sama slash biar aman
        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="memory_status", description="Cek kapasitas memorimu")
    async def memory_status(self, ctx: commands.Context):
        print(f"[Aika] Command memory_status dieksekusi")
        if ctx.author.id not in self.user_chats:
            if ctx.interaction:
                await ctx.interaction.response.send_message("Mau cek apa? Aika aja belum tau apapun soalmu. 😒", ephemeral=True)
            else:
                await ctx.send("Mau cek apa? Aika aja belum tau apapun soalmu. 😒", delete_after=12)
            return

        chat = self.user_chats[ctx.author.id]

        # jangan hitung system prompt
        conversation_messages = [message for message in chat if message["role"] != "system"]
        jumlah_pesan = len(conversation_messages)

        kapasitas_max = self.max_memory_messages
        persentase = min(int((jumlah_pesan / kapasitas_max) * 100), 100)

        kotak_terisi = int(persentase / 10)
        bar = ("█" * kotak_terisi + "░" * (10 - kotak_terisi))

        if persentase < 25:
            flavor = "Baru kenal dikit... ingatan masih ringan."
        elif persentase >= 50:
            flavor = "Kita mulai kenal dekat nih."
        elif persentase < 75:
            flavor = "Udah lumayan sering ngobrol nih."
        else:
            flavor = "Kita udah kenal banyak..."

        embed = discord.Embed(
            title=f"Status Ingatan Aika ({ctx.author.display_name})",
            description=
                f"**Kapasitas:** [{bar}] `{persentase}%`\n"
                f"**Pesan tersimpan:** `{jumlah_pesan}/{kapasitas_max}` pesan\n\n"
            ,
            color=0xD675C1
        )

        embed.set_footer(
            text=f"Pesan paling lama akan dihapus otomatis saat penuh.\nMau hapus semua sekalian? Gunakan ak!reset_memori",
            icon_url="https://cdn.discordapp.com/attachments/863959650448703538/1540201066455371888/bunga.png?ex=6a8b11c5&is=6a89c045&hm=2f7837e9e91cf914975584cb8ba5f001f80ea54d36c86e643547b1f23a111b26&")
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        if ctx.interaction:
            await ctx.interaction.response.send_message(content=flavor, embed=embed, ephemeral=True)
        else:
            await ctx.send(content=flavor, embed=embed)

    #groq baca gambar
    async def prepare_image(self, attachment:discord.Attachment):
        # kompresi ukuran gambar kalo melebihi 20 MB
        MAX_FILE_SIZE = 20 * 1024 * 1024

        if attachment.size > MAX_FILE_SIZE:
            print(f"[Aika] Ukuran berkas terlalu besar: {attachment.size} bytes (> 20MB)")
            return None

        print(f"[Aika] Memproses lampiran gambar: {attachment.url}")
        return {
            "type": "image_url",
            "image_url": {
                "url": attachment.url
            }
        }

    async def generate_response(self, user_id:int, is_admin:bool, chat:list, contents:list):
        # cek rate limit sebelum ke API
        is_safe, reason = self.limiter.check_limits(estimated_tokens=1500)
        if not is_safe:
            raise RateLimitError(f"Local Safety Net: {reason}")

        # cari tau waktu lokal skarang (WIB)
        tz = timezone(timedelta(hours=7)) 
        now = datetime.now(tz)

        # format string waktu yg rapi biar gampang dipahamin AI
        hari_map = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        bulan_map = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        time_str = f"{hari_map[now.weekday()]}, {now.day} {bulan_map[now.month-1]} {now.year} - {now.strftime('%H:%M')} WIB"
        # nyisipin konteks waktu ke user
        time_context = f"[Waktu pesan ini dikirim: {time_str}]"

        ## Prepend the system prompt dynamically just for this API call
        system_msg = self.get_system_instruction(is_admin, time_context)
        payload_messages = [system_msg] + chat + [{"role":"user", "content":contents}]

        print(f"[Aika] Mengirim API Request ke Groq (Total payload pesan: {len(payload_messages)})")
        try:
            raw_response = await asyncio.to_thread(
                self.ai_client.chat.completions.with_raw_response.create,
                model=self.model,
                messages=payload_messages,
                temperature=0.7,
                reasoning_effort="none",
                max_completion_tokens=75
            )

            # parse output dan penggunaan payload
            response = raw_response.parse()
            headers = raw_response.headers
            usage = response.usage

            # setor metrik dan header live di cog state biar kebaca di Stats Cog
            self.last_api_meta = {
                "timestamp": time.time(),
                "model": response.model,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "queue_time": getattr(usage, "queue_time", 0.0),
                "prompt_time": getattr(usage, "prompt_time", 0.0),
                "completion_time": getattr(usage, "completion_time", 0.0),
                "total_time": getattr(usage, "total_time", 0.0),
                "tok_per_sec": (usage.completion_tokens / usage.completion_time) if getattr(usage, "completion_time", 0) > 0 else 0.0,
                # header rate limit langsung dari server groq
                "limit_req_daily": headers.get("x-ratelimit-limit-requests", "N/A"),
                "rem_req_daily": headers.get("x-ratelimit-remaining-requests", "N/A"),
                "reset_req_daily": headers.get("x-ratelimit-reset-requests", "N/A"),
                "limit_tok_min": headers.get("x-ratelimit-limit-tokens", "N/A"),
                "rem_tok_min": headers.get("x-ratelimit-remaining-tokens", "N/A"),
                "reset_tok_min": headers.get("x-ratelimit-reset-tokens", "N/A"),
            }

            # lacak total metrik sesi bot
            self.session_usage["total_requests"] += 1
            self.session_usage["prompt_tokens"] += usage.prompt_tokens
            self.session_usage["completion_tokens"] += usage.completion_tokens
            self.session_usage["total_tokens"] += usage.total_tokens

            start_time = time.time()
            elapsed = time.time() - start_time
            print(f"[Aika] Respon Groq diterima dalam {elapsed:.2f} detik.")

            output_text = response.choices[0].message.content or "Hmm... Aika lagi blank. 😵"

            # BERSIHKAN SEBELUM SIMPAN
            # konversi payload multimodal jadi teks biasa buat histori biar kehindar dari eror 404 grgr link gambar expire
            text_only_content = ""
            for item in contents:
                if item.get("type") == "text":
                    text_only_content += item.get("text", "")
                elif item.get("type") == "image_url":
                    text_only_content += " [User uploaded an image]"

            chat.append({"role": "user", "content": text_only_content.strip()})
            chat.append({"role": "assistant", "content": output_text})

            self.save_user_chats()
            return output_text
        except Exception as e:
            print(f"[Aika] Gagal memanggil Groq: {e}")
            raise

    @commands.Cog.listener()
    async def on_message(self,message: discord.Message):
        # abaikan bot dan DM
        if message.author.bot or message.guild is None:
            return

        # kalo ada yg model prefix, jangan lanjut ke AI nya
        if message.content.startswith("ak!"):
            print(f"[Aika] Pesan diabaikan karena diawali dengan prefix 'ak!': {message.content}")
            return

        # channel cek
        # kalo di luar dari channel khusus, wajib mention bot
        is_in_target_channel = (message.channel.id == int(self.target_channel_id))
        is_mentioned = self.bot.user.mentioned_in(message)

        if not is_in_target_channel and not is_mentioned:
            return

        # cek command dulu sebelum cooldown biar gak ketahan
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            print(f"[Aika] Menjalankan deteksi sebagai command terdaftar: {ctx.command}")
            await self.bot.process_commands(message)
            return

        # kalo ada ,, di awal, ignore (anggap kayak comment)
        msg_clean = message.content.strip()
        if msg_clean.startswith(",,"):
            print("[Aika] Pesan diabaikan karena menggunakan prefix koma ganda (,,).")
            return

        # cooldown
        cooldown_time = 3.0 if is_in_target_channel else 10.0 #3 detik di channel khusus, 10 detik di luar (lewat mention)
        now = asyncio.get_event_loop().time()
        last_time = self.user_cooldowns.get(message.author.id, 0)
        time_passed = now - last_time

        if time_passed < cooldown_time:
            # hitung timestamp UNIX nya diskor
            remaining_seconds = cooldown_time - time_passed
            print(f"[Aika] User {message.author} terkena cooldown. Sisa waktu: {remaining_seconds:.2f}s")
            target_time = int(datetime.now().timestamp() + remaining_seconds)
            discord_timestamp = f"<t:{target_time}:R>"
            
            if is_in_target_channel:
                reply_text = "Sabar napa, ngirimnya jgn cepet-cepet! 🤌"
            else:
                reply_text = f"Sabar, di luar channel khusus tunggu {discord_timestamp} lagi kalau mau nge-tag Aika! 😤"

            await message.reply(
                reply_text,
                delete_after=4,
                allowed_mentions=discord.AllowedMentions.none()
            )
            return
        self.user_cooldowns[message.author.id] = now

        # cek kalo atmint
        is_admin = False
        if isinstance(message.author, discord.Member):
            is_admin = (
                message.author.guild_permissions.administrator
                or message.author.id == message.guild.owner_id
            )
        print(f"[Aika] User: {message.author} | Status Admin: {is_admin}")

        # ambil memori user
        chat = self.cari_atau_buatchat(message.author.id)

        # cek memori
        #conversation_messages = [msg for msg in chat if msg["role"] != "system"]
        #jumlah_pesan = len(conversation_messages)
        #kapasitas_max = self.max_memory_messages

        # kasih peringatan klo dah 80%
        # if jumlah_pesan == int(self.max_memory_messages * 0.8):
        #    print(f"[Aika] Kapasitas memori {message.author} telah mencapai 80%.")
        #    warning_msg = (
        #        f"Dikit lagi kapasitas memorimu samaku mau penuh nih, {message.author.mention}... 😥\n"
        #        f"Aika bakal ngelupain memori percakapan kita yang paling lama...\n"
        #        f"-# Pakai `/reset-chat` kalau mau hapus semua ingatanmu samaku."
        #    )
        #    try:
        #        await message.author.send(warning_msg) #kirim di DM biar privat
        #    except discord.Forbidden:
        #        await message.channel.send(warning_msg, delete_after=12) #klo DM kekunci, lgsg lewat channel

        # reset otomatis kalo dah full 100%
        # if jumlah_pesan >= kapasitas_max:
        #    print(f"[Aika] Kapasitas memori {message.author} penuh (100%). Menghapus riwayat lama.")

        # KONTEN MULTIMODAL
        contents = []
        image_count = 0

        # gambar
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                if image_count >= 5: break
                image_data = await self.prepare_image(attachment)

                if image_data is None:
                    await message.reply(
                        "Gambarnya kegedean, ih... 😭 Melebihi 20 MB...\n"
                        "Coba kompres plis..."
                    )
                    return

                contents.append(image_data)
                image_count += 1

        # CLEAN TEXT (HAPUS MENTION ID)
        # Hapus <@123456789> / <@!123456789> dari teks pesan kalau di luar dari channel khusus
        cleaned_text = message.clean_content
        if is_mentioned:
            cleaned_text = message.content.replace(f"<@{self.bot.user.id}>", "").replace(f"<@!{self.bot.user.id}>", "").strip()

        # teks
        if cleaned_text:
            contents.insert(0,
                {
                    "type": "text",
                    "text": cleaned_text
                }
            )

        # gaada yang dikirim?
        if not contents:
            print("[Aika] Array 'contents' kosong! Kemungkinan Intent Message Content tidak aktif.")
            return

        # panggil Groq
        status_msg = None
        print(f"[Aika] Memproses pesan dari {message.author.id} | Jumlah Lampiran: {len(message.attachments)}")
        async with message.channel.typing():
            try:
                output_text = await self.generate_response(message.author.id, is_admin, chat, contents)
                #safety net biar ga asal mention
                if "@everyone" in output_text:
                    output_text = output_text.replace("@everyone","`@everyone`")
                if "@here" in output_text:
                    output_text = output_text.replace("@here","`@here`")

                #kirim respon
                await message.reply(output_text, allowed_mentions=discord.AllowedMentions.none())
                print(f"[Aika] Respon berhasil dikirim")

                # Potong memori jika melebihi batas (tanpa menyentuh system prompt)
                if len(self.user_chats[message.author.id]) > self.max_memory_messages:
                    trim_limit = self.max_memory_messages - (self.max_memory_messages % 2)
                    self.user_chats[message.author.id] = self.user_chats[message.author.id][-trim_limit:]
                    self.save_user_chats()
                    print(f"[Aika] Memangkas memori otomatis untuk {message.author.id}")

            #ERROR HANDLING
            except RateLimitError as e: #rate limit
                print(f"[Groq] Rate limit: {e}")

                # cek kalo penyebabnya dari safety net dari sini
                error_msg = str(e)
                if "Local Safety Net:" in error_msg:
                    clean_reason = error_msg.replace("Local Safety Net:", "").strip()
                    reply = f"Aika lagi rehat bentar, ya... 😩\n`({clean_reason})`"
                else:
                    # fallback dari Groq nya (kode 429, rate limit)
                    match = re.search(r"Please try again in (?:(\d+)h)?(?:(\d+)m)?(?:([\d\.]+)s)?", error_msg)
                    discord_timestamp = None
                    if match:
                        hours = float(match.group(1) or 0)
                        minutes = float(match.group(2) or 0)
                        seconds = float(match.group(3) or 0)
                        
                        total_seconds = int((hours * 3600) + (minutes * 60) + seconds)
                        target_time = int(time.time() + total_seconds)
                        
                        reply = f"Duh, bentar... Aika rehat sejenak, ya. Coba lagi <t:{target_time}:R> (<t:{target_time}:t>) 😩"
                    else:
                        reply = "Duh, bentar... Aika rehat sejenak, ya. 😩\n`(Rate limit reached)`"

                await message.reply(
                    reply,
                    allowed_mentions=discord.AllowedMentions.none()
                )
            #bad request
            except BadRequestError as e:
                print(f"[Groq] Bad request: {e}")
                await message.reply(
                    "Hmm... Aika lagi belum bisa proses, ya, coba lagi nanti. 😵",
                    allowed_mentions=discord.AllowedMentions.none()
                )
            #general API error
            except APIError as e:
                print(f"[Groq] API error: {e}")
                await message.reply(
                    "Ntar, ya... server AI lagi error... 😩",
                    allowed_mentions=discord.AllowedMentions.none()
                )
            #eror anomali
            except Exception as e:
                print(f"[Groq] Eror anomali: {type(e).__name__}: {e}")
                await message.reply(
                    "Aika lagi error bentar... 😵",
                    allowed_mentions=discord.AllowedMentions.none()
                )

async def setup(bot):
    await bot.add_cog(AIPersona(bot))
