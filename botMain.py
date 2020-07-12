import asyncio
from game_concepts import theFire
from game_concepts import part1_forest
import file_management
from discord.ext import commands


# --------------- BOT SETUP ------------------

token_file = open("data/roomtoken", "r")
TOKEN = token_file.read()
botprefix = '!'

bot = commands.Bot(botprefix)

@bot.event
async def on_connect():
    bot.data = file_management.read_saves()

    # save main channel
    if bot.data.main_channel_id != -1:
        bot.main_channel = await bot.fetch_channel(bot.data.main_channel_id)
    else:
        bot.main_channel = None

    # startup any timers
    theFire.theFire_initialization(bot.data, bot.main_channel)

    print("roombot ready!")


@bot.event
async def on_message(message):
    if message.author == bot.user:  # don't respond to itself
        return
    if message.content.startswith(botprefix):
        await process_command(message)


# ---------------- BOT COMMANDS -----------------

async def process_command(message):
    input_split = message.content[len(botprefix):].split()

    # /// General Commands ///

    # no commands
    if len(input_split) == 0:
        await message.channel.send("Don't know this command!")
        return

    cmd = input_split[0]
    modifiers = input_split[1:]

    if cmd.lower() == 'hello':
        await message.channel.send("Hello!")
        return

    elif cmd == 'reset':
        bot.data = file_management.reset()

        await message.channel.send("Reset!")

        return

    elif cmd == 'setmain':
        bot.data.main_channel_id = message.channel.id
        bot.main_channel = message.channel

        await message.channel.send("Set this channel as main channel!")
        return
    else:

        # /// Game Setup Commands ///

        if bot.data.state == 0:
            if cmd == "trytimer":
                if bot.main_channel == None:
                    await message.channel.send("ERROR: main channel not set. Please use !setmain to set current channel" + \
                            " as main channel.")
                else:
                    #timer_thread = Thread(target=await set_timer(bot.data, "temp", 5))
                    task = asyncio.create_task(theFire.set_timer(bot.data, "temp", 10, bot.main_channel))
                    #timer_thread.start()
                    # timer_thread = Thread(target=await set_timer(bot.data, "temp2", 10))
                    # timer_thread.start()
                    # task = asyncio.create_task(set_timer(bot.data, "temp2", 10))
                return
            elif cmd == "resettimer":
                if "temp" in bot.data.cooldown.keys():
                    bot.data.cooldown["temp"] = -1
                    await message.channel.send("Timer reset.")
                else:
                    await message.channel.send("Timer not started.")
                return
            elif cmd == "start":
                if bot.main_channel == None:
                    await message.channel.send("Main channel not set.")
                    return

                bot.data.state = 1
                bot.data.cooldown["stoke"] = 1
                bot.data.progress_msg_id["stoke"] = -1

                await theFire.stoke_fire(message, bot.data, bot.main_channel)
                asyncio.create_task(theFire.darkness(bot.data, bot.main_channel))

                file_management.save(bot.data)

                return

        # /// Game Phase 1: The Fire ///

        elif bot.data.state == 1:
            if await part1_forest.part1_forest(cmd, modifiers, message, bot.data, bot.main_channel) == True:
                return


        await message.channel.send("Don't know this command!")


bot.run(TOKEN)
