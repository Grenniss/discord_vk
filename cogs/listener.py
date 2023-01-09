import discord

from discord.ext import commands

from .utils.base_cog import BaseCog
import requests
import aiohttp
import io

class Listener(BaseCog):
    def __init__(self, *args):
        super().__init__(*args)

    async def get_files(self, links):
        files = []
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(links):
                async with session.get(url) as resp:
                    if resp.status != 200:
                        print("Не получилось загрузить изображение")
                    img_byte = io.BytesIO(await resp.read())
                    files.append(discord.File(img_byte, f'image{i}.png'))
        return files

    async def create_embed(self, user_data, description, data):
        em = discord.Embed(description = description)
        em.set_author(
            name = f"{user_data['first_name']} {user_data['last_name']}",
            icon_url = user_data["photo_100"],
            url = f"https://vk.com/id{data['from_id']}"
        )
        return em

    async def forward_to_channel(self, data: dict) -> discord.TextChannel:
        channel = self.bot.get_channel(self.bot.config.forward_to_discord_channel_id)

        vk = self.bot.get_cog("VK")
        users_get_response = vk.vk_api.method(
            "users.get",
            values={"user_ids": data["from_id"], "fields": "photo_100"},
        )
        user_data = users_get_response[0] if users_get_response else None
        if user_data is None:
            return
        if data["type"] == "image":
            images = await self.get_files(links = data["urls"])
            em = await self.create_embed(user_data = user_data, description = "", data = data)
            return await channel.send(embed = em, files = images)
        elif data["type"] == "image/text":
            images = await self.get_files(links = data["urls"])
            em = await self.create_embed(user_data = user_data, description = data["text"], data = data)
            return await channel.send(embed = em,  files = images)
        elif data["type"] == "text":
            if data["urls"]:
                em = await self.create_embed(user_data = user_data, description = "", data = data)
                return await channel.send(data["urls"], embed = em)
            else:
                em = await self.create_embed(user_data = user_data, description = data["text"], data = data)
                return await channel.send(embed = em)
        elif data["type"] == "sticker":
            em = await self.create_embed(user_data = user_data, description = "Наклейка", data = data)
            return await channel.send(embed = em)

    async def on_vk_message(self, data: dict):
        await self.forward_to_channel(data = data)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await message.channel.send()
        await self.bot.wait_until_ready()
        vk = self.bot.get_cog("VK")

        if (
            message.author.bot
            or message.channel.id != self.bot.config.forward_to_discord_channel_id
        ):
            return

        if message.attachments:
            attachment = [url.url for url in message.attachments]
            session = requests.Session()
            data = [vk.upload.photo_messages(photos = session.get(i, stream = True).raw)[0] for i in attachment]
        else:
            attachment = None

        if attachment is None and not message.content:
            return
    
        request_values = {"random_id": 0, "peer_id": vk.FIRST_CHAT_PEER_ID}

        if message.content and attachment:
            request_values[
                "message"
            ] = self.bot.phrases.vk_message_attachment_fmt.format(
                message = message,
                content = message.content
            )
            request_values["attachment"] = ",".join([f'photo{user["owner_id"]}_{user["id"]}' for user in data])
        elif attachment:
            request_values["message"] = self.bot.phrases.vk_attachment_fmt.format(
                message = message
            )
            request_values["attachment"] = ",".join([f'photo{user["owner_id"]}_{user["id"]}' for user in data])
        else:
            request_values["message"] = self.bot.phrases.vk_message_fmt.format(
                message=message
            )
        vk.vk_api.method("messages.send", values = request_values)


def setup(bot):
    bot.add_cog(Listener(bot))
