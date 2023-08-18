import re


def replace_colors(str):
    return re.sub('\^\d{1}', '', str)


def sanitize(str):
    return re.sub('[^a-zA-Z0-9 !#\$%&\'\(\)\*\+,\-\./:<=>\?@\[\\\]\^_]', '?', replace_colors(str))
