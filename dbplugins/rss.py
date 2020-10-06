# """created rss plugin for uniborg >> credid : @By_Azade"""

# import asyncio
# import html
# import logging
# import os
# import re

# from telethon import events

# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# # import schedule
# from feedparser import parse
# from sample_config import Config
# from sql_helpers.rss_sql import (add_url, check_url_availability, get_all,
#                                  get_urls, remove_url, update_url)
#

# logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
#                     level=logging.WARNING)
# logger = logging.getLogger(__name__)

# @borg.on(utils.admin_cmd(pattern=("rss ?(.*)")))
# async def show_url(event):
#     tg_chat_id = str(event.chat_id)
#     entity=await borg.get_input_entity(Config.RSS_POST_MSG_GROUP_ID)
#     if event.pattern_match.group(1):
#         tg_feed_link = event.pattern_match.group(1)
#         link_processed = parse(tg_feed_link)

#         if link_processed.bozo == 0:
#             feed_title = link_processed.feed.get("title", default="Unknown")
#             feed_description = "<i>{}</i>".format(
#                 re.sub('<[^<]+?>', '', link_processed.feed.get("description", default="Unknown")))
#             feed_link = link_processed.feed.get("link", default="Unknown")

#             feed_message = "<b>Feed Title:</b> \n{}" \
#                            "\n\n<b>Feed Description:</b> \n{}" \
#                            "\n\n<b>Feed Link:</b> \n{}".format(html.escape(feed_title),
#                                                                feed_description,
#                                                                html.escape(feed_link))

#             if len(link_processed.entries) >= 1:
#                 entry_title = link_processed.entries[0].get("title", default="Unknown")
#                 entry_description = "<i>{}</i>".format(
#                     re.sub('<[^<]+?>', '', link_processed.entries[0].get("description", default="Unknown")))
#                 entry_link = link_processed.entries[0].get("link", default="Unknown")

#                 entry_message = "\n\n<b>Entry Title:</b> \n{}" \
#                                 "\n\n<b>Entry Description:</b> \n{}" \
#                                 "\n\n<b>Entry Link:</b> \n{}".format(html.escape(entry_title),
#                                                                      entry_description,
#                                                                      html.escape(entry_link))
#                 final_message = feed_message + entry_message

#                 await borg.send_message(
#                     entity=entity,
#                     message=final_message,
#                     parse_mode='html'
#                 )
#             else:
#                 await borg.send_message(
#                     entity=Config.RSS_POST_MSG_GROUP_ID,
#                     message=feed_message,
#                     parse_mode='html'
#                 )
#         else:
#             await event.edit("This link is not an RSS Feed link")
#     else:
#         await event.edit("URL missing")

# @borg.on(utils.admin_cmd(pattern=("listrss ?(.*)")))
# async def list_urls(event):
#     tg_chat_id = str(event.chat_id)
#     entity=await borg.get_input_entity(Config.RSS_POST_MSG_GROUP_ID)
#     user_data = get_urls(tg_chat_id)

#     # this loops gets every link from the DB based on the filter above and appends it to the list
#     links_list = [row.feed_link for row in user_data]

#     final_content = "\n\n".join(links_list)

#     # check if the length of the message is too long to be posted in 1 chat bubble
#     if len(final_content) == 0:
#         await borg.send_message(
#             entity=entity,
#             message="This chat is not subscribed to any links"
#         )
#     elif len(final_content) <= Config.MAX_MESSAGE_SIZE_LIMIT:
#         await borg.send_message(
#             entity=entity,
#             message="This chat is subscribed to the following links:\n" + final_content
#         )
#     else:
#         await bot.send_message(
#             entity=entity,
#             parse_mode='html',
#             message="<b>Warning:</b> The message is too long to be sent"
#         )


# @borg.on(utils.admin_cmd(pattern=("addrss ?(.*)")))
# async def add_url_(event):
#     if event.pattern_match.group(1):
#         chat = await event.get_chat()

#         tg_chat_id = str(event.chat_id)

#         tg_feed_link = event.pattern_match.group(1)

#         link_processed = parse(tg_feed_link)

#         # check if link is a valid RSS Feed link
#         if link_processed.bozo == 0:
#             if len(link_processed.entries[0]) >= 1:
#                 tg_old_entry_link = link_processed.entries[0].link
#             else:
#                 tg_old_entry_link = ""

#             # gather the row which contains exactly that telegram group ID and link for later comparison
#             row = check_url_availability(tg_chat_id, tg_feed_link)

#             # check if there's an entry already added to DB by the same user in the same group with the same link
#             if row:
#                 await event.edit("This URL has already been added")
#             else:
#                 add_url(tg_chat_id, tg_feed_link, tg_old_entry_link)

#                 await event.edit("Added URL to subscription")
#         else:
#             await event.edit("This link is not an RSS Feed link")
#     else:
#         await event.edit("URL missing")

# @borg.on(utils.admin_cmd(pattern=("removerss ?(.*)")))
# async def remove_url_(event):
#     if event.pattern_match.group(1):
#         tg_chat_id = str(event.chat_id)

#         tg_feed_link = event.pattern_match.group(1)

#         link_processed = parse(tg_feed_link)

#         if link_processed.bozo == 0:
#             user_data = check_url_availability(tg_chat_id, tg_feed_link)

#             if user_data:
#                 remove_url(tg_chat_id, tg_feed_link)

#                 await event.edit("Removed URL from subscription")
#             else:
#                 await event.edit("You haven't subscribed to this URL yet")
#         else:
#             await event.edit("This link is not an RSS Feed link")
#     else:
#         await event.edit("URL missing")

# @borg.on(events.NewMessage(func=lambda e: e.is_group))
# async def rss_update(event):
#     user_data = get_all()
#     entity=await borg.get_input_entity(Config.RSS_POST_MSG_GROUP_ID)
#     # this loop checks for every row in the DB
#     for row in user_data:
#         row_id = row.id
#         tg_chat_id = row.chat_id
#         tg_feed_link = row.feed_link

#         feed_processed = parse(tg_feed_link)

#         tg_old_entry_link = row.old_entry_link

#         new_entry_links = []
#         new_entry_titles = []

#         # this loop checks for every entry from the RSS Feed link from the DB row
#         for entry in feed_processed.entries:
#             # check if there are any new updates to the RSS Feed from the old entry
#             if entry.link != tg_old_entry_link:
#                 new_entry_links.append(entry.link)
#                 new_entry_titles.append(entry.title)
#             else:
#                 break

#         # check if there's any new entries queued from the last check
#         if new_entry_links:
#             update_url(row_id, new_entry_links)
#         else:
#             pass

#         if len(new_entry_links) < 5:
#             # this loop sends every new update to each user from each group based on the DB entries
#             for link, title in zip(reversed(new_entry_links), reversed(new_entry_titles)):
#                 final_message = "<b>{}</b>\n\n{}".format(html.escape(title), html.escape(link))

#                 if len(final_message) <= Config.MAX_MESSAGE_SIZE_LIMIT:
#                     await borg.send_message(
#                         entity=entity,
#                         message=final_message,
#                         parse_mode='html'
#                     )
#                 else:
#                     await borg.send_message(
#                         entity=entity,
#                         message="<b>Warning:</b> The message is too long to be sent",
#                         parse_mode='html'
#                     )
#         else:
#             for link, title in zip(reversed(new_entry_links[-5:]), reversed(new_entry_titles[-5:])):
#                 final_message = "<b>{}</b>\n\n{}".format(html.escape(title), html.escape(link))

#                 if len(final_message) <= Config.MAX_MESSAGE_SIZE_LIMIT:
#                     await borg.send_message(
#                         entity=entity,
#                         message=final_message,
#                         parse_mode='html'
#                     )
#                 else:
#                     await borg.send_message(
#                         entity=entity,
#                         message="<b>Warning:</b> The message is too long to be sent",
#                         parse_mode='html'
#                     )

#             await borg.send_message(
#                 entity=entity,
#                 parse_mode='html',
#                 message="<b>Warning: </b>{} occurrences have been left out to prevent spam".format(len(new_entry_links) - 5)
#             )


# def rss_set(event):
#     user_data = get_all()

#     # this loop checks for every row in the DB
#     for row in user_data:
#         row_id = row.id
#         tg_feed_link = row.feed_link
#         tg_old_entry_link = row.old_entry_link

#         feed_processed = parse(tg_feed_link)

#         new_entry_links = []
#         new_entry_titles = []

#         # this loop checks for every entry from the RSS Feed link from the DB row
#         for entry in feed_processed.entries:
#             # check if there are any new updates to the RSS Feed from the old entry
#             if entry.link != tg_old_entry_link:
#                 new_entry_links.append(entry.link)
#                 new_entry_titles.append(entry.title)
#             else:
#                 break

#         # check if there's any new entries queued from the last check
#         if new_entry_links:
#             update_url(row_id, new_entry_links)
#         else:
#             pass

# if __name__ == '__main__':
#     scheduler = AsyncIOScheduler()
#     scheduler.add_job(rss_set, 'interval', seconds=10)
#     scheduler.add_job(rss_update, 'interval', seconds=10)
#     scheduler.start()
#     print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

#     # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
#     try:
#         asyncio.get_event_loop().run_forever()
#     except (KeyboardInterrupt, SystemExit):
#         pass
# # schedule.every(2).minutes.do(rss_set)
# # schedule.every(2).minutes.do(rss_update)
# # schedule.every().hour.do(job)
# # schedule.every().day.at("10:30").do(job)
# # schedule.every(5).to(10).minutes.do(job)
# # schedule.every().monday.do(job)
# # schedule.every().wednesday.at("13:15").do(job)
# # schedule.every().minute.at(":17").do(job)
# # schedule.every(1).seconds.do(job)
# # loop = asyncio.get_event_loop()
# # while True:
# #     loop.run_until_complete(schedule.run_pending())
# #     time.sleep(1)

# # __help__ = """
# #  - /addrss <link>: add an RSS link to the subscriptions.
# #  - /removerss <link>: removes the RSS link from the subscriptions.
# #  - /rss <link>: shows the link's data and the last entry, for testing purposes.
# #  - /listrss: shows the list of rss feeds that the chat is currently subscribed to.
# # NOTE: In groups, only admins can add/remove RSS links to the group's subscription
# # """

# # __mod_name__ = "RSS Feed"

# # job = updater.job_queue

# # job_rss_set = job.run_once(rss_set, 5)
# # job_rss_update = job.run_repeating(rss_update, interval=60, first=60)
# # job_rss_set.enabled = True
# # job_rss_update.enabled = True

# # SHOW_URL_HANDLER = CommandHandler("rss", show_url, pass_args=True)
# # ADD_URL_HANDLER = CommandHandler("addrss", add_url, pass_args=True)
# # REMOVE_URL_HANDLER = CommandHandler("removerss", remove_url, pass_args=True)
# # LIST_URLS_HANDLER = CommandHandler("listrss", list_urls)

# # dispatcher.add_handler(SHOW_URL_HANDLER)
# # dispatcher.add_handler(ADD_URL_HANDLER)
# # dispatcher.add_handler(REMOVE_URL_HANDLER)
# # dispatcher.add_handler(LIST_URLS_HANDLER)
