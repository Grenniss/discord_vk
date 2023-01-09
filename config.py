# Токен бота из https://discord.com/developers
bot_token: str = ""

# Префиксы команд бота
command_prefixes: list = ["!", "!!"]


# Ключ доступа VK сообщества
vk_api_token = ""

# ID сообщества бота (как получить -> https://imgur.com/o9vs0Jb)
vk_group_id = None

# ID дискорд канала, в который пересылать сообщения из вк
forward_to_discord_channel_id = None

# ID дискорд канала, который прослушивать
listen_from_discord_channel_id = None

# Системные переменные
debug: bool = False
