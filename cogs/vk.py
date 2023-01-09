import threading

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from .utils.base_cog import BaseCog

class VK(BaseCog):
    FIRST_CHAT_PEER_ID = 2000000002

    def __init__(self, *args):
        super().__init__(*args)
        self.vk_api = vk_api.VkApi(token=self.bot.config.vk_api_token)
        self.vk_bot_long_poll = VkBotLongPoll(self.vk_api, self.bot.config.vk_group_id)
        self.vk_bot_thread = threading.Thread(
            target=self._listen_vk, name="vk_bot_thread"
        )
        self.upload = vk_api.VkUpload(self.vk_api)
        self.vk_bot_closed = False

    def _listen_vk(self):
        while True:
            try:
                for event in self.vk_bot_long_poll.listen():
                    if (
                        event.type != VkBotEventType.MESSAGE_NEW
                        or event.message["peer_id"] != self.FIRST_CHAT_PEER_ID
                    ):
                        continue
                            
                    if self.vk_bot_closed:
                        return

                    self.on_vk_message(event)
            except Exception as e:
                continue

    def on_vk_message(self, event):
        from_id = event.message["from_id"]
        if event.message["attachments"]:
            if event.message["attachments"][0]["type"] == "sticker":
                data = {
                    "type": "sticker",
                    "text": "Наклейка",
                    "from_id": from_id
                }
            elif event.message["attachments"][0]["type"] == "photo" and event.message["text"]:
                try:
                    links = [i["photo"]["sizes"][3]["urls"] for i in event.message["attachments"]]
                except:
                    links = [i["photo"]["sizes"][3]["url"] for i in event.message["attachments"]]
                data = {
                    "type": "image/text",
                    "urls": links,
                    "text": event.message["text"],
                    "from_id": from_id
                }

            elif event.message["attachments"][0]["type"] == "photo":
                try:
                    links = [i["photo"]["sizes"][3]["urls"] for i in event.message["attachments"]]
                except:
                    links = [i["photo"]["sizes"][3]["url"] for i in event.message["attachments"]]
                data = {
                    "type": "image",
                    "urls": links,
                    "from_id": from_id,
                    "text": ""
                }
        else:
            data = {
                "type": "text",
                "from_id": from_id
            }
            if "https://" in event.message["text"] or "http://" in event.message["text"]:
                data["text"] = ""
                data["urls"] = event.message["text"]
            else:
                data["text"] = event.message["text"]
                data["urls"] = ""

        listener_cog = self.bot.get_cog("Listener")
        self.bot.loop.create_task(listener_cog.on_vk_message(data))
        

    async def on_startup(self):
        self.vk_bot_thread.start()

    async def on_bot_close(self):
        self.vk_bot_closed = True
        self.vk_bot_long_poll.session.close()


def setup(bot):
    bot.add_cog(VK(bot))
