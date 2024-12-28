from enum import Enum





SHARD_COUNT = 4


class RoomRedisKeys(Enum):
    ROOMS = "room"
    MESSAGES = "messages"
    USERS = "users"


class NotificationGroupTypes(Enum):
    ALL = "all"
    ROOM = "room"
    INDIVIDUAL = "individual"


class NotificationPrefix(Enum):
    SERVER = "SERVER"
    ADMIN = "ADMIN"
    CREATOR = "CREATOR"


class NotificationLevels(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"



class RoomTypes:
    PUBLIC = "public"
    PRIVATE = "private"

    ROOM_TYPE_CHOICES = [
        (PUBLIC, "Public"),
        (PRIVATE, "Private"),
    ]