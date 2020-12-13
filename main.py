from threading import Thread
from typing import List

from pyrogram import Client, filters
from pyrogram.types import Chat, Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, User, Photo, Update

import Database
from Auction import runningAuctions, RunningAuction, auctions, _timeOut
from AuctionCreator import creatingAuctions, AuctionCreator

Database.createAllFiles()

app = Client(
    "my_account",
    api_id= "",
    api_hash="")

Database.loadEveryAuction(app)


#  pip install pyrogram
# pip install tgcrypto


@app.on_message(filters=filters.photo)
def on_private_message(client: Client, message: Message) -> None:
    message.delete()
    photo: Photo = message.photo


@app.on_message(filters=filters.command("aste") & filters.private)
def auctionCommand(client: Client, message: Message) -> None:
    message.delete()
    user = message.from_user
    if not Database.isUserRegistered(user):
        message.reply_text("Usa il comando /register <Password> per registrarti!")
    for auction in auctions:
        message.reply_text(auction.__str__(),reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Elimina", callback_data=auction.name + "_del")]]))


@app.on_message(filters=filters.command("register") & filters.private)
def register(client: Client, message: Message) -> None:
    message.delete()
    user = message.from_user
    if Database.isUserRegistered(user):
        message.reply_text("Sei già registrato!")
        return
    messageWords: List[str] = message.text.split(' ')
    if len(messageWords) != 2:
        message.reply_text("Comando errato! \n Usa il comando /register <Password> per registrarti!")
        return
    if Database.isPasswordCorrect(messageWords[1]):
        message.reply_text("Correttamente registrato!")
        Database.registerUser(user)
    else:
        message.reply_text("Password errata!")


@app.on_message(filters=filters.command("new") & filters.private)
def newAuction(client: Client, message: Message) -> None:
    message.delete()
    user = message.from_user
    if not Database.isUserRegistered(user):
        message.reply_text("Usa il comando /register <Password> per registrarti!")
        return
    chat: Chat = message.chat
    AuctionCreator(chat, app)


@app.on_message(filters=filters.command("startauction") & filters.group)
def startAuction(client: Client, message: Message) -> None:
    if bool(runningAuctions):
        return
    sender: User = message.from_user
    group = message.chat
    administrators = [admin.user.id for admin in group.iter_members(filter="administrators")]
    cond1 = sender.id not in administrators
    cond2 = client.get_me().id not in administrators
    if cond1 or cond2:
        return
    message.delete()
    messageWords: List[str] = message.text.split(' ')
    if len(messageWords) != 2:
        return
    for auction in auctions:
        if auction.name == messageWords[1]:
            runningAuction = auction.start(group)
            _timeOut(runningAuction)
            break


##############################################################################################################

waitingToBeAcceptedGroups: List[Chat] = []


@app.on_message(filters=filters.new_chat_members)
def onBotJoinChat(client: Client, message: Message) -> None:
    if client.get_me() not in message.new_chat_members:  # Todo -> If the bot not in new chat members
        return
    group: Chat = message.chat
    waitingToBeAcceptedGroups.append(group)
    for user_id in Database.getRegisteredUsers():
        client.send_message(user_id, "The bot has joined a new chat : " + group.title,
                            reply_markup=_getGroupAcceptKeyboard(group))


def _getGroupAcceptKeyboard(addedGroup: Chat):
    keyboard = [
        [InlineKeyboardButton("Accetta", callback_data=addedGroup.id.__str__() + " _accept"),
         InlineKeyboardButton("Ignora", callback_data=addedGroup.id.__str__() + " _refuse")]
    ]
    return InlineKeyboardMarkup(keyboard)


##########################################################################

@app.on_callback_query()
def onButtonPress(client: Client, callbackQuery: CallbackQuery):
    if callbackQuery.message is None:
        return
    chatId = callbackQuery.message.chat.id
    for key in creatingAuctions:
        if chatId == key:
            creatingAuction: AuctionCreator = creatingAuctions.get(key)
            creatingAuction.onButtonPress(client, callbackQuery)
    for key in runningAuctions:
        if chatId == key:
            creatingAuction: RunningAuction = runningAuctions.get(key)
            creatingAuction.onButtonPress(client, callbackQuery)
    data = callbackQuery.data
    chat: Chat = callbackQuery.message.chat
    if data.endswith("_accept"):
        groupId = data.split("_")[0].rstrip(' ')
        for group in waitingToBeAcceptedGroups:
            if group.id.__str__() == groupId:
                waitingToBeAcceptedGroups.remove(group)
                Database.addAuthorizedGroup(group)
                client.send_message(chat.id, "Gruppo accettato!")
                break
    elif data.endswith("_refuse"):
        groupId = data.split("_")[0].rstrip(' ')
        for group in waitingToBeAcceptedGroups:
            if group.id.__str__() == groupId:
                waitingToBeAcceptedGroups.remove(group)
                client.send_message(chat.id, "Gruppo ignorato!")
                break
    elif data.endswith("_del"):
        auctionName = data.split("_")[0].rstrip(' ')
        for auction in auctions:
            if auction.name == auctionName:
                Database.removeAuction(auction)
                client.send_message(chat.id, auction.name + " eliminata!")
                break


@app.on_message(filters=filters.private)
def on_private_message(client: Client, message: Message) -> None:
    user = message.from_user
    chat = message.chat
    if not Database.isUserRegistered(user):
        message.reply_text("Usa il comando /register <Password> per registrarti!")
        return
    chatId = chat.id
    for key in creatingAuctions:
        if chatId == key:
            creatingAuction: AuctionCreator = creatingAuctions.get(key)
            creatingAuction.on_private_message(client, message)


app.run()
