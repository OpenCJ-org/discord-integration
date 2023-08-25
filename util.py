import re


def replace_colors(str):
    return re.sub('\^\d{1}', '', str)


def replace_ctrl(str):
    return re.sub(r'[\x00-\x1F]+','.', str)


def sanitize(str):
    return re.sub('["\x7F\\\\]+', '.', replace_ctrl(replace_colors(str)))


def get_clean_name(name):
    # Basic sanity check since players may be messing around with the separator character
    name = sanitize(name)
    if len(name) >= 2:
        # Shorten the name if it's too long
        name = name[:32] if len(name) > 32 else name
        return name
    return None


def get_clean_message(message):
    message = sanitize(message)
    if len(message) > 0:
        message = message[:128] if len(message) > 128 else message
        return message
    return None