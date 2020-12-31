import os
import random
from threading import Timer

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# client = discord.Client()
actionValuePair = {"start": "Trivia will start in a moment", "stop": "See you next time", "qtn": "Question"}
questionFile = r"D:\tests\python\discordBot\questions\questions.txt"
highScore = {}


class Timeout:
    def __init__(self, callback):
        self.callback = callback
        self.timeObj = None

    def startTimer(self):
        self.timeObj = Timer(10.0, self.callback)
        print("Timer started....")

    def stopTimer(self):
        self.timeObj.cancel()
        print("Timer stopped...")


async def stopTrivia(triviaChannel):
    await triviaChannel.send(embed=displayScore())
    await triviaChannel.send(embed=getEmbedMsg("stop"))


class QuizClient(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.question = None
        self.answer = None
        self.waitAnswer = False
        self.questionCount = 0
        self.highScore = {}

    async def on_message(self, message):
        if message.author == client.user:
            return

        if not self.waitAnswer:
            await message.channel.send(embed=getEmbedMsg(message.content))

            if message.content == "start":
                await self.nextQuestion(message.channel)

        elif self.waitAnswer:
            if message.content.strip().lower() == self.answer.lower():
                embed = discord.Embed(title="Trivia", color=0x8925da)
                embed.add_field(name=f"{message.author} got correct answer", value=self.answer, inline=True)
                incScore(message.author)
                await message.channel.send(embed=embed)
                self.waitAnswer = False
                await self.nextQuestion(message.channel)

        else:
            print(f"""keyword {message.content} not found""")

    async def nextQuestion(self, triviaChannel):
        if self.questionCount < 10:
            question = load_questions()
            self.question = question[0]
            self.answer = question[1]
            self.waitAnswer = True
            self.questionCount += 1
            await triviaChannel.send(embed=questionResp(self.question))
        else:
            await stopTrivia(triviaChannel)


def load_questions():
    with open(questionFile, mode="r") as qs:
        temp = random.choice(list(qs)).split(",Answer:")
        return temp[0], temp[1].strip()


def getEmbedMsg(action):
    embed = discord.Embed(title="Trivia", color=0x8925da)

    if action in actionValuePair:
        embed.add_field(name=action, value=actionValuePair[action], inline=True)
    else:
        embed.add_field(name=action, value=action, inline=True)

    return embed


def questionResp(question):
    embed = discord.Embed(title="Trivia", color=0x8925da)
    embed.add_field(name="Question", value=question, inline=True)
    return embed


def incScore(usr):
    if usr not in highScore:
        highScore[usr] = 1
    else:
        highScore[usr] += 1


def displayScore():
    embed = discord.Embed(title="Score", color=0x8925da)

    for usr in highScore:
        embed.add_field(name=f"""{usr}""", value=f"""{highScore[usr]}""", inline=False)

    return embed


client = QuizClient()

client.run(TOKEN)
