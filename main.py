import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import random

# ---------------- BOT SETUP ----------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- FILES ----------------
FILES = {
    "tasks": "tasks.json",
    "attendance": "attendance.json",
    "sessions": "sessions.json"
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
        await ctx.send("📭 You have no tasks.")
        return

    msg = "\n".join([f"{i+1}. {t}" for i, t in enumerate(data[user])])

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

    await ctx.send("✅ Attendance marked")

@bot.command()
async def attendance(ctx):
    data = load_data(FILES["attendance"])
    user = str(ctx.author.id)

    count = data.get(user, 0)
    await ctx.send(f"📊 Attendance: {count}")

# ---------------- STUDY SESSION ----------------
@bot.command()
async def startsession(ctx):
    data = load_data(FILES["sessions"])
    user = str(ctx.author.id)

    data[user] = "active"
    save_data(FILES["sessions"], data)

    await ctx.send("📚 Session started! Stay focused 🔥")

@bot.command()
async def endsession(ctx):
    data = load_data(FILES["sessions"])
    user = str(ctx.author.id)

    if data.get(user) != "active":
        await ctx.send("❌ No active session")
        return

    data[user] = "ended"
    save_data(FILES["sessions"], data)

    await ctx.send("⏱️ Session ended. Good job 🎉")

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

# ---------------- SMART DEMO AI ----------------
@bot.command()
async def ask(ctx, *, question):
    q = question.lower()

    greetings = [
        "Hey there! 👋 How can I help you today?",
        "Hi! 😊 What would you like to know?",
        "Hello! I'm here to help you with anything."
    ]

    time_responses = [
        "Time is fascinating—it's how we measure change from past to future.",
        "In physics, time is considered the fourth dimension along with space.",
        "You can think of time as a continuous flow that moves everything forward."
    ]

    blackhole_responses = [
        "A black hole is a region in space where gravity is so strong that nothing can escape.",
        "They form when massive stars collapse into extremely dense objects.",
        "Black holes are one of the most mysterious phenomena in the universe!"
    ]

    study_responses = [
        "Try focusing in short intervals like 25 minutes, then take breaks.",
        "Consistency is more important than long hours—stay regular.",
        "Avoid distractions and create a clean study environment."
    ]

    ai_responses = [
        "AI stands for Artificial Intelligence—machines that can think and learn.",
        "It's about building systems that solve problems like humans.",
        "You're currently interacting with a simulated AI system 😉"
    ]

    default_responses = [
        "That's an interesting question! Let me think...",
        "Hmm, that connects to multiple concepts.",
        "Good question! It involves deeper understanding.",
        "I like that question—it shows curiosity!"
    ]

    if any(word in q for word in ["hello", "hi", "hey"]):
        answer = random.choice(greetings)

    elif "time" in q:
        answer = random.choice(time_responses)

    elif "black hole" in q:
        answer = random.choice(blackhole_responses)

    elif "study" in q or "focus" in q:
        answer = random.choice(study_responses)

    elif "ai" in q:
        answer = random.choice(ai_responses)

    else:
        answer = random.choice(default_responses) + " It relates to science, logic, or general knowledge."

    embed = discord.Embed(
        title="🤖 AI Assistant",
        description=answer,
        color=0x5865F2
    )

    await ctx.send(embed=embed)

# ---------------- RUN BOT ----------------
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
