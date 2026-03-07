# This module functions as a gateway for the game server.
# It receives events from Discord module and forwards them to the game server
# It receives events from the game server and forwards them to the Discord module

import logging
import asyncio
import socket
from opencj_events import GameEvent

logger = logging.getLogger(__name__)

class OpenCJListener():
    """
Interface between Discord and the game server
    """
    server = None # Listener socket
    client = None # Game server client that is connected
    port = None # socket's TCP port
    dc = None # Discord integration module instance

    @staticmethod
    def parse_game_event(data):
        """
    Parse data (typically an event name with arguments) and try to create an event from it.
    If it fails, it means either we didn't receive all the data or the event is unknown
        """
        if ' ' in data:
            event_parts = data.split(' ')
            event_type = event_parts[0]
            event_args = event_parts[1:]
            event = GameEvent.create(event_type, event_args)
            if event:
                return event
        return None


    def __init__(self, discord_module, game_name):
        self.dc = discord_module
        self.port = 28961


    async def handle_client(self, client):
        """
    This is the main loop that handles a client connection.
    The client can either be the Discord integration script or the game server
        """
        # New client connected, closing previous since only one game server is expected
        if self.client is not None:
            logger.info('Unexpected game server client connected, dropping previous')
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()

        self.client = client

        # Process incoming data from client
        logger.info('Now handling new game server client')
        loop = asyncio.get_event_loop()
        event = None # Events and their arguments are separated by space
        data = None
        while True:
            data = await loop.sock_recv(client, 512)
            if not data:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
                self.client = None
                # Client disconnected
                break

            data = data.decode('ascii', errors='ignore')
            # Might receive multiple events at once
            if '\n' in data:
                lines = data.split('\n')
            else:
                lines = [data]

            # Go through each event
            for line in lines:
                # Just a newline
                if len(line) == 0:
                    continue

                event = OpenCJListener.parse_game_event(line)
                if event:
                    # Have the Discord handler perform an action based on this event
                    # Don't await this otherwise this won't work if Discord is down
                    # TODO: if this keeps stacking tasks because Discord is down, might need to cancel the previous task?
                    loop.create_task(self.dc.on_game_event(event))
                else:
                    # Shouldn't always keep this on, but currently for debugging it's useful
                    logger.info(f'Flushing: {line}')


    async def on_discord_message(self, name, msg):
        if self.client is not None:
            data = f'^8[^7Discord^8]^7 {name}: {msg}'
            await asyncio.get_event_loop().sock_sendall(self.client, data.encode('ascii', 'ignore'))
        else:
            logger.info('Can\'t handle Discord event yet, no game server is listening')


    async def start(self):
        """
    This sets up a TCP localhost socket and listens to it for clients.
    A client can be the Discord integration script or the game server.
        """
        if not self.port:
            raise Exception('Running game server listener before setting port')

        logger.info('Running game server listener')

        # Set up the TCP socket as non-blocking and start listening
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('127.0.0.1', self.port))
        self.server.listen(1)
        self.server.setblocking(False)

        logger.info('Server is listening for connections')
        loop = asyncio.get_event_loop()
        while True:
            client, _ = await loop.sock_accept(self.server)
            logger.info(f'New client connected')
            loop.create_task(self.handle_client(client))
