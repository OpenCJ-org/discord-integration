# Event types and logic

from enum import Enum
from util import get_clean_message, get_clean_name, sanitize
import sys
from syslog import syslog

class GameEvent():
    # These event numbers are hardcoded in opencj_discord.cpp and discord.gsc, do not change (only append)
    event_map = {
        0: 'PlayerMessageEvent',
        1: 'MapStartedEvent',
        2: 'PlayerCountChangedEvent',
        3: 'PlayerJoinedEvent',
        4: 'PlayerLeftEvent',
        5: 'RunFinishedEvent',
        6: 'PlayerRenamedEvent'
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
            self.name = get_clean_name(parts[0])
            self.message = get_clean_message(parts[1] if len(parts) == 1 else ';'.join(parts[1:]))
            return self.name is not None and self.message is not None
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


class PlayerJoinedEvent():
    def create(self, args):
        if len(args) == 1:
            self.player_name = args[0]
            return True
        return False

    @property
    def player_name(self):
        return self._player_name

    @player_name.setter
    def player_name(self, val):
        self._player_name = val


class PlayerLeftEvent():
    def create(self, args):
        if len(args) == 1:
            self.player_name = args[0]
            return True
        return False

    @property
    def player_name(self):
        return self._player_name

    @player_name.setter
    def player_name(self, val):
        self._player_name = val


class RunFinishedEvent():
    def create(self, args):
        # Special case, since player names can contain a variety of characters
        str = ' '.join(args)
        if ';' in str:
            parts = str.split(';')
            if len(parts) == 5:
                self.player_name = get_clean_name(parts[0])
                self.runID = int(parts[1])
                self.time_str = parts[2]
                self.map_name = parts[3]
                self.route_name = parts[4]
                return self.player_name is not None
        return False

    @property
    def player_name(self):
        return self._player_name

    @player_name.setter
    def player_name(self, val):
        self._player_name = val

    @property
    def runID(self):
        return self._runID

    @runID.setter
    def runID(self, val):
        self._runID = val

    @property
    def time_str(self):
        return self._time_str

    @time_str.setter
    def time_str(self, val):
        self._time_str = val

    @property
    def map_name(self):
        return self._map_name

    @map_name.setter
    def map_name(self, val):
        self._map_name = val

    @property
    def route_name(self):
        return self._route_name

    @route_name.setter
    def route_name(self, val):
        self._route_name = val


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
