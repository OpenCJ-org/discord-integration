# Test game server listener by emulating the Discord side

import asyncio
import socket
from opencj_listener import OpenCJListener


class OpenCJDiscord:
    gameserver = None


    def set_game_server(self, gameserver):
        self.gameserver = gameserver


    # Injection functions for testing purposes
    async def inject_message(self, name, msg):
        await self.gameserver.on_discord_message(name, msg)


async def test(dc):
    # Set up the client socket
    print('Setting up client socket...')
    socket_path = '/tmp/opencj_events_cod4'
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.setblocking(False)
    try:
        loop = asyncio.get_event_loop()
        await loop.sock_connect(client, socket_path)
    except FileNotFoundError as fnfe:
        raise Exception('Could not connect to game server listener')

    # Let server set up the client before injecting
    await asyncio.sleep(1)

    # Await data from the game server listener when we send an event
    print('Injecting data and awaiting response..')
    await dc.inject_message('test', 'this is an injected message')
    data = await asyncio.get_event_loop().sock_recv(client, 512)
    if not data:
        print('Did not receive response')
    else:
        data = data.decode('utf-8')
        print('Received response')
    return data


async def main():
    # Set up fake Discord module to inject events
    dc = OpenCJDiscord()
    ls = OpenCJListener(dc, 'cod4')
    dc.set_game_server(ls)

    # Set up the listener
    print('Starting game server listener..')
    task_listener = asyncio.create_task(ls.start())

    # Give the listener time to bind before starting the task task
    await asyncio.sleep(1)

    # Wait until the test task is complete and then cancel the listener since it runs indefinitely
    data = await test(dc)
    task_listener.cancel()

    # Verify the data is as expected
    expected_msg = '[Discord] test: this is an injected message'
    if data != expected_msg:
        raise Exception(f'Expected:\n{expected_msg}\nGot\n{data}')
    else:
        print('Test successful!')


if __name__ == "__main__":
    asyncio.run(main())