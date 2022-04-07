from vkbottle import Bot, load_blueprints_from_package
from notification import starter
from elschool_top import starter_top
from vkbottle import BaseMiddleware
from vkbottle.bot import Message, Bot
from database import DB
from converter_html import app
import config


async def start(bot):
    print("START NOTIFICATION!")
    await starter(bot)


async def start_top():
    print("START TOP!")
    await starter_top()



class RegistrationMiddleware(BaseMiddleware[Message]):
    async def pre(self):
        if self.event.from_id < 0:
            self.stop("Groups are not allowed to use bot")

        # print(self.event)
        print(f"{self.event.from_id}: {self.event.text}")
        result = await DB.select_by_user_id(self.event.from_id)

        if result is None:
            await DB.add_new_user(self.event.from_id)
        await DB.create_if_not_create_notification(self.event.from_id)

    async def post(self):
        pass


bot = Bot(config.token)

for bp in load_blueprints_from_package("handlers"):
    bp.load(bot)

print("START")
bot.loop_wrapper.add_task(start(bot))

###############
bot.loop_wrapper.add_task(start_top())
bot.labeler.message_view.register_middleware(RegistrationMiddleware)
bot.run_forever()