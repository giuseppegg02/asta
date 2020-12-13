import types

from pyrogram import Client
from pyrogram.types import User, Chat, List

import yaml

import re
from Auction import Auction, auctions


def isUserRegistered(user: User) -> bool:
    with open("registeredUsers.txt", "r") as file:
        registered_users = yaml.load(file, Loader=yaml.FullLoader)
    return user.id in registered_users if registered_users is not None else False


def getRegisteredUsers():
    with open("registeredUsers.txt", "r") as file:
        registered_users = yaml.load(file, Loader=yaml.FullLoader)
    return registered_users


def registerUser(user: User) -> None:
    with open("registeredUsers.txt", "r") as file:
        registered_users = yaml.load(file, Loader=yaml.FullLoader)
    if registered_users is None:
        registered_users = []
    registered_users.append(user.id)
    with open("registeredUsers.txt", "w") as file:
        yaml.dump(registered_users, file)


def isPasswordCorrect(password: str) -> bool:
    with open("password.txt", "r") as file:
        correct_Password: str = yaml.load(file, Loader=yaml.FullLoader)
    print(correct_Password)
    return password == correct_Password


def createAllFiles():
    with open("password.txt", "a"):
        pass
    with open("registeredUsers.txt", "a"):
        pass
    with open("auctions.txt", "a"):
        pass
    with open("autorizedGroups.txt", "a"):
        pass


def loadEveryAuction(app: Client):
    with open("auctions.txt", "r") as file:
        auctionList = yaml.load(file, Loader=yaml.FullLoader)
    if auctionList is not None:
        for auction in auctionList:
            regex = (
                'Name: (?P<_0>.+)\nDesc: (?P<_1>.+)\nOfferN: (?P<_2>\d+)\nTime: (?P<_3>\d+)\nBuyout: (?P<_4>\d+)\nPriceRaise: (?P<_5>\d+)\nMinimumPrice: (?P<_6>\d+)')
            match = re.match(regex, auction).groupdict()
            auctions.append(Auction(name=match["_0"], description=match["_1"], offerMaxNumber=int(match["_2"])
                                    , time=int(match["_3"]), buyout=int(match["_4"]), priceRaise=int(match["_5"]),
                                    minimumPrice=int(match["_6"]), app=app))


def storeAuction(auction: Auction):
    auctionString: str = f"Name: {auction.name}\nDesc: {auction.description}\nOfferN: {auction.offerMaxNumber}" \
                         f"\nTime: {auction.time}\nBuyout: {auction.buyout}\nPriceRaise: {auction.priceRaise}" \
                         f"\nMinimumPrice: {auction.minimumPrice}"
    with open("auctions.txt", "r") as file:
        auctionList = yaml.load(file, Loader=yaml.FullLoader)
    if auctionList is not None:
        auctionList.append(auctionString)
    else:
        auctionList = [auctionString]
    with open("auctions.txt", "w") as file:
        yaml.dump(auctionList, file)


def removeAuction(delAuction: Auction):
    auctions.remove(delAuction)
    auctionStrings = []
    for auction in auctions:
        auctionStrings.append(f"Name: {auction.name}\nDesc: {auction.description}\nOfferN: {auction.offerMaxNumber}"
                              f"\nTime: {auction.time}\nBuyout: {auction.buyout}\nPriceRaise: {auction.priceRaise}"
                              f"\nMinimumPrice: {auction.minimumPrice}")
    with open("auctions.txt", "w") as file:
        yaml.dump(auctionStrings, file)


def addAuthorizedGroup(group: Chat):
    with open("autorizedGroups.txt", "r") as file:
        groups = yaml.load(file, Loader=yaml.FullLoader)
    if groups is not None and isinstance(groups, list):
        groups.append(group.id)
    else:
        groups = [group.id]
    with open("autorizedGroups.txt", "w") as file:
        yaml.dump(groups, file)


def getAuthorizedGroups():
    with open("autorizedGroups.txt", "r") as file:
        groups = yaml.load(file, Loader=yaml.FullLoader)
    return groups
