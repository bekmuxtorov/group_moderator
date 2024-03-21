import re

REGEXS = [
    r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.\S+', 
    r'@\w+', r'https?:\/\/t\.me\/\+?[\w-]+', 
    r'https?:\/\/www\.instagram\.com\/[\w-]+',
    r'https?:\/\/www\.facebook\.com\/[\w-]+',
    r'https?:\/\/youtube\.com\/@[\w-]+',
    r'https?:\/\/ummalife\.com\/[\w-]+',
    ]


async def get_urls(text: str):
    urls = []
    for regex in REGEXS:
        urls += re.findall(regex, text)
    print(f"urls {urls}")
    return urls





