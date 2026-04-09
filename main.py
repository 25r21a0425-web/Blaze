import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import google.generativeai as genai

# ---------------- GEMINI AI SETUP ----------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------- BOT SETUP ----------------
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

    embed = discord.Embed(
        title="✅ Task Added",
        description=f"**{task}** added successfully!",
        color=0x2ecc71
    )
    await ctx.send(embed=embed)

@bot.command()
async def tasks(ctx):
    data = load_data(FILES["tasks"])
    user = str(ctx.author.id)

    if user not in data or len(data[user]) == 0:
        embed = discord.Embed(
            title="📭 No Tasks",
            description="You have no tasks.",
            color=0xe74c3c
        )
        await ctx.send(embed=embed)
        return

    msg = "\n".join([f"**{i+1}.** {t}" for i, t in enumerate(data[user])])

    embed = discord.Embed(
        title="📋 Your Tasks",
        description=msg,
        color=0x3498db
    )
    await ctx.send(embed=embed)

# ---------------- ATTENDANCE ----------------
@bot.command()
async def mark(ctx):
    data = load_data(FILES["attendance"])
    user = str(ctx.author.id)

    data[user] = data.get(user, 0) + 1
    save_data(FILES["attendance"], data)

    embed = discord.Embed(
        title="✅ Attendance Marked",
        description="Your attendance recorded.",
        color=0xf1c40f
    )
    await ctx.send(embed=embed)

@bot.command()
async def attendance(ctx):
    data = load_data(FILES["attendance"])
    user = str(ctx.author.id)

    count = data.get(user, 0)

    embed = discord.Embed(
        title="📊 Attendance",
        description=f"Total: **{count}**",
        color=0x9b59b6
    )
    await ctx.send(embed=embed)

# ---------------- STUDY SESSION ----------------
@bot.command()
async def startsession(ctx):
    data = load_data(FILES["sessions"])
    user = str(ctx.author.id)

    data[user] = "active"
    save_data(FILES["sessions"], data)

    embed = discord.Embed(
        title="📚 Session Started",
        description="Focus mode ON 🔥",
        color=0x1abc9c
    )
    await ctx.send(embed=embed)

@bot.command()
async def endsession(ctx):
    data = load_data(FILES["sessions"])
    user = str(ctx.author.id)

    if data.get(user) != "active":
        await ctx.send("❌ No active session")
        return

    data[user] = "ended"
    save_data(FILES["sessions"], data)

    embed = discord.Embed(
        title="⏱️ Session Ended",
        description="Great work 🎉",
        color=0xe67e22
    )
    await ctx.send(embed=embed)

# ---------------- BUTTON PANEL ----------------
@bot.command()
async def panel(ctx):
    button1 = Button(label="➕ Add Task", style=discord.ButtonStyle.green)
    button2 = Button(label="📋 View Tasks", style=discord.ButtonStyle.blurple)

    async def add_task_callback(interaction):
        await interaction.response.send_message(
            "Type your task like:\n`!addtask your_task`",
            ephemeral=True
        )

    async def view_task_callback(interaction):
        data = load_data(FILES["tasks"])
        user = str(interaction.user.id)

        if user not in data or len(data[user]) == 0:
            await interaction.response.send_message("No tasks ❌", ephemeral=True)
            return

        msg = "\n".join([f"{i+1}. {t}" for i, t in enumerate(data[user])])
        await interaction.response.send_message(
            f"📋 Your Tasks:\n{msg}",
            ephemeral=True
        )

    button1.callback = add_task_callback
    button2.callback = view_task_callback

    view = View()
    view.add_item(button1)
    view.add_item(button2)

    await ctx.send("🎛️ Control Panel:", view=view)

# ---------------- GEMINI AI COMMAND ----------------
@bot.command()
async def ask(ctx, *, question):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(question)

        embed = discord.Embed(
            title="🤖 AI Assistant",
            description=response.text,
            color=0x5865F2
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Error: {e}")

# ---------------- RUN BOT ----------------
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
