import asyncio
from game_concepts import theFire
import file_management


async def part1_forest(cmd, modifiers, message, data, main_channel):
    if cmd == "light":
        await theFire.stoke_fire(message, data, main_channel)

        file_management.save(data)

        return True


    return False

