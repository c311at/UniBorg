from database.mongo import cli

cli = cli["Userbot"]["Blacklist"]


async def add_blacklist(id):
    return cli.insert_one({"Blacklist": id})


async def check_blacklist(id):
    return bool(cli.find_one({"Blacklist": id}))


async def delete_blacklist(id):
    return cli.delete_one({"Blacklist": id})
