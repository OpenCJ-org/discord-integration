# Event types and logic

from enum import Enum
from util import sanitize
import sys
from syslog import syslog

class GameEvent():
    # These event numbers are hardcoded in opencj_discord.cpp and discord.gsc, do not change (only append)
    event_map = {
        0: 'PlayerMessageEvent',
        1: 'MapStartedEvent',
        2: 'PlayerCountChangedEvent',
    }

    @staticmethod
    def create(event_type, args):
        event_type = int(event_type)
        if event_type in GameEvent.event_map:
            try:
                event_name = GameEvent.event_map[event_type]
                event_class = getattr(sys.modules[__name__], event_name)
                if event_class:
                    inst = event_class()
                    if inst.create(args):
                        return inst
            except Exception as e:
                syslog(f'Failed to create event for: {e}')
                pass # Doesn't exist or failed to create
        return None


class PlayerMessageEvent():
    def create(self, args):
        # Special case, since player names and messages can contain a variety of characters
        str = ' '.join(args)
        if ';' in str:
            parts = str.split(';')
            name = parts[0]
            message = parts[1] if len(parts) == 1 else ';'.join(parts[1:])

            # Basic sanity check since players may be messing around with the separator character
            name = sanitize(name)
            if len(name) >= 2:
                # Shorten the name if it's too long
                name = name[:32] if len(name) > 32 else name

                # Don't assign player name yet, only when message is also valid
                message = sanitize(message)
                if len(message) > 0:
                    self.message = message[:128] if len(message) > 128 else message
                    self.player_name = name
                    return True
            else:
                syslog('A player has an invalid name') # Better not log it now, but useful to know
        return False

    @property
    def message(self):
        return self._message if self._message else ""

    @message.setter
    def message(self, val):
        self._message = val

    @property
    def player_name(self):
        return self._player_name if self._player_name else ""

    @player_name.setter
    def player_name(self, val):
        self._player_name = val


class MapStartedEvent():
    def create(self, args):
        if len(args) == 1:
            self.map_name = args[0]
            return True
        return False

    @property
    def map_name(self):
        return self._map_name if self._map_name else "unknown"

    @map_name.setter
    def map_name(self, val):
        self._map_name = val


class PlayerCountChangedEvent():
    def create(self, args):
        if len(args) == 1:
            self.player_count = int(args[0])
            return True
        return False
    
    @property
    def player_count(self):
        return self._player_count if self._player_count else 0

    @player_count.setter
    def player_count(self, val):
        self._player_count = val
