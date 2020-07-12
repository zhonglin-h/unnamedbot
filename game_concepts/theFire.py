import asyncio
import xml_processing
import file_management

fire_dimming_interval = 60

message_dict = file_management.read_json("text/theFire.json")

# Constants
text_messages = message_dict = file_management.read_json("text/theFire.json")


def theFire_initialization(data, main_channel):
    if data.state > 0:
        asyncio.create_task(darkness(data, main_channel))
        if data.cooldown["stoke"] != 1:
            asyncio.create_task(set_timer(data, "stoke", 20, main_channel))


async def set_timer(data, name, duration, channel, sleep_segments = 5):
    # add timer result to cooldowns
    if not name in data.cooldown.keys():
        data.cooldown[name] = -1
        data.progress_msg_id[name] = -1
    if data.cooldown[name] == -1:
        data.cooldown[name] = 0
        progress_bar = list('`' + '-' * sleep_segments + '`') # 10 * '-'
        message = await channel.send(''.join(progress_bar))
        data.progress_msg_id[name] = message.id

        # count down in segments with length of segment_duration
        data.cooldown[name] = 0
        segment_duration = duration / sleep_segments
        while sleep_segments > 0:
            await asyncio.sleep(segment_duration)
            sleep_segments -= 1
            progress_bar[len(progress_bar) - sleep_segments - 2] = '='
            await message.edit(content = ''.join(progress_bar))
        data.cooldown[name] = 1
        file_management.save(data)
    else:
        await channel.send("ERROR timer not reset")


async def darkness(data, channel):
    while True:
        if data.light_lvl > 0:
            data.light_lvl -= 1
            await xml_processing.send_loaded_message("light_" + str(data.light_lvl), text_messages, channel)
        await asyncio.sleep(fire_dimming_interval)


async def stoke_fire(message, data, channel):
    if data.cooldown["stoke"] == 1:
        await channel.send(message.author.display_name + " stoke the fire.")
        data.light_lvl = 5
        await xml_processing.send_loaded_message("light_5", text_messages, channel)
        data.cooldown["stoke"] = -1
        asyncio.create_task(set_timer(data, "stoke", 20, channel))
