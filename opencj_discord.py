# The part of the bot that handles the integration with Discord side, and parses events from the game server listener

import asyncio
import discord
from util import sanitize
from opencj_events import PlayerMessageEvent, MapStartedEvent, PlayerCountChangedEvent
from syslog import syslog


class OpenCJDiscord(discord.Client):
    """
Class for Discord integration that will use and be used by the game server listener
    """
    gameserver = None # Game server listener, used to send events
    intents = None # Discord intents
    token = None # The authorization token for the bot
    guild_id = None # Guild (= server) where the channel is in
    channel_id = None # Channel where the server will read and send messages from
    map_name = None # Game server map name currently playing
    player_count = None # Total number of players currently on the game server
    is_ready = False # Whether or not the Discord bot is ready to process events

    def set_channel_id(self, channel_id):
        self.channel_id = int(channel_id)

    def set_guild_id(self, guild_id):
        self.guild_id = int(guild_id)

    def set_gameserver(self, gameserver):
        self.gameserver = gameserver


    async def on_game_event(self, event):
        """
    Perform an action on Discord based on the received game event
        """

        if not self.is_ready:
            syslog('Received event but not ready yet')
            return

        channel = self.get_channel(self.channel_id) # server-chat
        if isinstance(event, PlayerMessageEvent):
            await channel.send(f'**{event.player_name}**: {event.message}')
        elif isinstance(event, MapStartedEvent):
            self.map_name = event.map_name
            status = f'{self.map_name} ({self.player_count})' if self.player_count is not None else f'{self.map_name} (?)'
            await self.change_presence(activity=discord.Game(name=status))
        elif isinstance(event, PlayerCountChangedEvent):
            self.player_count = event.player_count
            status = f'{self.map_name} ({self.player_count})' if self.map_name else f'unknown ({self.player_count})'
            await self.change_presence(activity=discord.Game(name=status))
        else:
            syslog(f'Unhandled event: {event}')


    async def on_ready(self):
        """
    Gets called when the Discord bot is ready to roll
        """
        self.is_ready = True
        syslog(f'Logged in as {self.user}')


    async def on_message(self, message):
        """
    Gets called when a message is received from Discord
        """
        # OpenCJ server
        if message.guild.id == self.guild_id:
            # Ignore our own bot messages, otherwise computer will get a headache
            if message.author == self.user:
                return

            # Verify that this message is from the expected channel
            if isinstance(message.channel, discord.TextChannel):
                if message.channel.id == self.channel_id:
                    # Check if a handle to the game server listener is available yet
                    if not self.gameserver:
                        syslog('Received a message but game server listener isn\'t ready yet')
                        return

                    # Apply some basic restrictions
                    msg = sanitize(message.content)
                    msg = msg[:128] if len(msg) > 128 else msg

                    name = sanitize(message.author.display_name)
                    name = name[:32] if len(name) > 32 else name
                    if len(msg) > 0 and len(name) >= 3:
                        # Send the event to the gameserver listener to process
                        asyncio.create_task(self.gameserver.on_discord_message(name, msg))


async def start_bot(client, token):
    """
Start running the Discord client that listens for events
    """
    await client.start(token)

