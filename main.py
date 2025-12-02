
import discord
from discord.ext import commands
import json
import os

TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", "0"))
SONGS_FILE = os.getenv("SONGS_FILE", "songs.json")

if not os.path.exists(SONGS_FILE):
    with open(SONGS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

with open(SONGS_FILE, "r", encoding="utf-8") as f:
    songs = json.load(f)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

def save_songs():
    with open(SONGS_FILE, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=4)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def save(ctx, link: str, *, name: str):
    if ADMIN_ROLE_ID != 0 and ADMIN_ROLE_ID not in [r.id for r in ctx.author.roles]:
        return await ctx.send("❌ شما اجازه ذخیره آهنگ را ندارید.")

    songs[name] = link
    save_songs()
    await ctx.send(f"✔️ آهنگ **{name}** ذخیره شد!")

@bot.command()
async def list(ctx):
    if not songs:
        return await ctx.send("آرشیو خالی است.")
    msg = "\n".join([f"- **{name}**: {url}" for name, url in songs.items()])
    await ctx.send(msg)

@bot.command()
async def remove(ctx, *, name: str):
    if ADMIN_ROLE_ID != 0 and ADMIN_ROLE_ID not in [r.id for r in ctx.author.roles]:
        return await ctx.send("❌ شما اجازه حذف ندارید.")
    if name not in songs:
        return await ctx.send("چنین آهنگی یافت نشد.")
    del songs[name]
    save_songs()
    await ctx.send(f"🗑️ آهنگ **{name}** حذف شد.")

bot.run(TOKEN)
