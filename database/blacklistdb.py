from database.mongo import cli

cli = cli["Userbot"]["Blacklist"]


async def check_blacklist(chat_id, trigger):
    return cli.find({"chat_id": chat_id, "trigger": trigger})


async def add_to_blacklist(chat_id, trigger):
    to_check = await check_blacklist(chat_id, trigger)
    if not to_check:
        cli.insert_one({"chat_id": chat_id, "trigger": trigger})
        return True
    else:
        cli.update_one(
            {
                "_id": to_check["_id"],
                "chat_id": to_check["chat_id"],
                "trigger": to_check["trigger"],
            },
            {"$set": {"trigger": trigger}},
        )
        return False


async def rm_from_blacklist(chat_id, trigger):
    to_check = await check_blacklist(chat_id, trigger)
    if not to_check:
        return False
    else:
        cli.delete_one(
            {
                "_id": to_check["_id"],
                "chat_id": to_check["chat_id"],
                "trigger": to_check["trigger"],
            }
        )


async def get_chat_blacklist(chat_id):
    return cli.find({"chat_id": chat_id})


async def num_blacklist_filters(chat_id):
    check = await get_chat_blacklist(chat_id)
    if check:
        return check.count()
    else:
        False
