import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- FILES ----------------
FILES = {
    "tasks": "tasks.json",
    "attendance": "attendance.json",
    "sessions": "sessions.json",
    "users": "users.json",
    "forms": "forms.json"
}

# Create files if not exist
for file in FILES.values():
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump({}, f)

def load_data(file):
    with open(file, "r") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ---------------- TASK COMMANDS ----------------
@bot.command()
async def addtask(ctx, *, task):
    data = load_data(FILES["tasks"])
    user = str(ctx.author.id)

    if user not in data:
        data[user] = []

    data[user].append(task)
    save_data(FILES["tasks"], data)

    await ctx.send("Task added successfully ✅")

@bot.command()
async def tasks(ctx):
    data = load_data(FILES["tasks"])
    user = str(ctx.author.id)

    if user not in data or len(data[user]) == 0:
        await ctx.send("No tasks found ❌")
        return

    msg = "\n".join([f"{i+1}. {t}" for i, t in enumerate(data[user])])
    await ctx.send(f"Your Tasks:\n{msg}")

# ---------------- ATTENDANCE ----------------
@bot.command()
async def mark(ctx):
    data = load_data(FILES["attendance"])
    user = str(ctx.author.id)

    data[user] = data.get(user, 0) + 1
    save_data(FILES["attendance"], data)

    await ctx.send("Attendance marked ✅")

@bot.command()
async def attendance(ctx):
    data = load_data(FILES["attendance"])
    user = str(ctx.author.id)

    count = data.get(user, 0)
    await ctx.send(f"Your attendance: {count}")

# ---------------- STUDY SESSION ----------------
@bot.command()
async def startsession(ctx):
    data = load_data(FILES["sessions"])
    user = str(ctx.author.id)

    data[user] = "active"
    save_data(FILES["sessions"], data)

    await ctx.send("Study session started 📚")

@bot.command()
async def endsession(ctx):
    data = load_data(FILES["sessions"])
    user = str(ctx.author.id)

    if data.get(user) != "active":
        await ctx.send("No active session ❌")
        return

    data[user] = "ended"
    save_data(FILES["sessions"], data)

    await ctx.send("Study session ended ⏱️")

# ---------------- RUN BOT ----------------
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
