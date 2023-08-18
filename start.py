import asyncio

import discord
from opencj_listener import OpenCJListener
from opencj_discord import OpenCJDiscord, start_bot
import sys


async def main():
    if len(sys.argv) < 2:
        raise Exception('Not called for a specific game, exiting..')

    # Support cod2 and cod4
    game_name = sys.argv[1]
    if game_name != 'cod4' and game_name != 'cod2':
        raise Exception('Requested unsupported game. Supported are cod2 and cod4')

    # Parse the configuration
    token = None
    channel_id = None
    guild_id = None
    with open(f'config_{game_name}', 'r') as cfg_file:
        lines = cfg_file.readlines()
        for line in lines:
            if '=' not in line:
                raise Exception(f'Config contains invalid line: {line}')
            parts = line.split('=')
            cfg_id = parts[0]
            cfg_val = '='.join(parts[1:]) if len(parts) >= 2 else parts[1]
            if cfg_id == 'token':
                token = cfg_val
            elif cfg_id == 'channelid':
                channel_id = cfg_val
            elif cfg_id == 'guildid':
                guild_id = cfg_val
            else:
                raise Exception(f'Unknown configuration option: {cfg_id}')

    # Check whether all necessary information is available
    if not token:
        raise Exception(f'Missing configuration option: token')
    if not channel_id:
        raise Exception(f'Missing configuration option: channelid')
    if not guild_id:
        raise Exception(f'Missing configuration option: guildid')

    # Everything is ready, set up Discord integration module and game server listener
    print('Setting up modules..')
    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True
    dc = OpenCJDiscord(intents=intents)
    ls = OpenCJListener(dc, game_name)
    dc.set_gameserver(ls)
    dc.set_channel_id(channel_id)
    dc.set_guild_id(guild_id)

    # Create tasks for Discord integration and game server listener
    task_discord = asyncio.create_task(start_bot(dc, token))
    task_listener = asyncio.create_task(ls.start())

    #await task_discord
    print('Starting game server listener and Discord integration module..')
    await asyncio.gather(task_discord, task_listener)


if __name__ == "__main__":
    asyncio.run(main())
