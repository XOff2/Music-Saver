# main.py
import os
import json
from pathlib import Path
from typing import Optional
import discord
from discord.ext import commands

# ---------- Configuration (from environment) ----------
TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_ROLE_ID_STR = os.getenv("ADMIN_ROLE_ID", "").strip()
SONGS_FILE = os.getenv("SONGS_FILE", "songs.json")
PREFIX = os.getenv("BOT_PREFIX", "?")  # default prefix ?

# validate token
if not TOKEN:
    raise SystemExit("DISCORD_TOKEN environment variable is required.")

# ADMIN_ROLE_ID can be empty -> treat as no-role restriction
try:
    ADMIN_ROLE_ID = int(ADMIN_ROLE_ID_STR) if ADMIN_ROLE_ID_STR else None
except ValueError:
    ADMIN_ROLE_ID = None

# ---------- Data file setup ----------
DATA_PATH = Path(SONGS_FILE)
if not DATA_PATH.exists():
    DATA_PATH.write_text(json.dumps([], indent=2), encoding="utf-8")

def load_songs():
    try:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_songs(data):
    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

# ---------- Bot setup ----------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ---------- UI View: Paste button (sends DM with command) ----------
class PasteView(discord.ui.View):
    def __init__(self, command_text: str):
        super().__init__(timeout=None)
        self.command_text = command_text

    @discord.ui.button(label="Paste Command", style=discord.ButtonStyle.success, emoji="🎧")
    async def paste(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # send DM to the user who clicked
            await interaction.user.send(f"Here is your command:\n```\n{self.command_text}\n```")
            await interaction.response.send_message("✅ I DM'ed the command to you.", ephemeral=True)
        except discord.Forbidden:
            # can't DM user
            await interaction.response.send_message("❌ I couldn't DM you. Please enable DMs from server members.", ephemeral=True)

# ---------- Helper: permission check ----------
def is_admin_or_no_restriction(member: discord.Member) -> bool:
    if ADMIN_ROLE_ID is None:
        return True
    return any(r.id == ADMIN_ROLE_ID for r in member.roles)

# ---------- Commands ----------

@bot.event
async def on_ready():
    print(f"Bot ready — Logged in as {bot.user} (prefix: {PREFIX})")

@bot.command(name="save")
async def cmd_save(ctx: commands.Context, *, name: str):
    """Save a music name. Usage: ?save <music name>"""
    if not is_admin_or_no_restriction(ctx.author):
        await ctx.reply("❌ You don't have permission to save songs.", mention_author=False)
        return

    name = name.strip()
    if not name:
        await ctx.reply("❌ Please provide a non-empty song name. Usage: ?save <music name>", mention_author=False)
        return

    songs = load_songs()
    # command to run on other music bot:
    command_text = f"/play {name}"  # we store the play command text (kept as plain text)
    songs.insert(0, {"name": name, "command": command_text})
    save_songs(songs)

    # Embed response with bold song title and Paste button
    embed = discord.Embed(title="🎶 Music Saved!", color=0x5865F2)
    embed.description = f"**{name}** has been added to the list."
    embed.add_field(name="Command", value=f"```\n{command_text}\n```", inline=False)
    await ctx.send(embed=embed, view=PasteView(command_text))

@bot.command(name="list")
async def cmd_list(ctx: commands.Context):
    """List saved songs. Usage: ?list"""
    songs = load_songs()
    if not songs:
        embed = discord.Embed(title="📁 No Saved Music", description="Your saved list is empty.", color=0xFFCC00)
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title="🎵 Saved Music", color=0x00BFFF)
    # show up to 25 items
    for item in songs[:25]:
        # Bold name; command shown as inline code
        embed.add_field(name=f"⭐ **{item['name']}**", value=f"`{item['command']}`", inline=False)
    # footer with total count
    embed.set_footer(text=f"Total: {len(songs)}")
    await ctx.send(embed=embed)

@bot.command(name="search")
async def cmd_search(ctx: commands.Context, *, query: str):
    """Search saved songs. Usage: ?search <text>"""
    query = query.strip().lower()
    if not query:
        await ctx.reply("❌ Please give a search query. Usage: ?search <text>", mention_author=False)
        return

    songs = load_songs()
    results = [s for s in songs if query in s["name"].lower()]

    if not results:
        embed = discord.Embed(title="🔍 No Results", description="No matching songs were found.", color=0xFF4444)
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title=f"🔎 Search Results for \"{query}\"", color=0x34D399)
    for item in results[:25]:
        embed.add_field(name=f"🎵 **{item['name']}**", value=f"`{item['command']}`", inline=False)
    embed.set_footer(text=f"Found: {len(results)}")
    await ctx.send(embed=embed)

@bot.command(name="remove")
async def cmd_remove(ctx: commands.Context, *, name: str):
    """Remove a saved song (admins only unless ADMIN_ROLE_ID empty). Usage: ?remove <song name>"""
    if not is_admin_or_no_restriction(ctx.author):
        await ctx.reply("❌ You don't have permission to remove songs.", mention_author=False)
        return

    name = name.strip()
    songs = load_songs()
    remaining = [s for s in songs if s["name"].lower() != name.lower()]
    if len(remaining) == len(songs):
        await ctx.reply("❌ No such song found.", mention_author=False)
        return

    save_songs(remaining)
    embed = discord.Embed(title="🗑️ Removed", description=f"**{name}** has been removed from the list.", color=0xFF4444)
    await ctx.send(embed=embed)

# ---------- Run ----------
bot.run(TOKEN)
