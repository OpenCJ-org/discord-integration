import re


def replace_colors(str):
    return re.sub('\^\d{1}', '', str)


def replace_ctrl(str):
    return re.sub(r'[\x00-\x1F]+','?', str)


def sanitize(str):
    return re.sub('["\x7F\\\\]+', '?', replace_ctrl(replace_colors(str)))
