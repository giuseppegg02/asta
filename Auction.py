import asyncio
import datetime
import time
from asyncio import wait
from calendar import calendar

from multiprocessing.connection import Client
from threading import Thread
from time import sleep
from typing import List, Dict

from emoji import emojize
from pyrogram.types import Chat, InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup, User


class Auction:

    def __init__(self, name: str, description: str, priceRaise: float, offerMaxNumber: int, time: int, buyout: float,
                 minimumPrice: int,
                 app: Client):
        self.name: str = name
        self.description: str = description
        self.priceRaise: float = priceRaise
        self.offerMaxNumber: int = offerMaxNumber
        self.time: int = time
        self.buyout: float = buyout
        self.app = app
        self.minimumPrice = minimumPrice

    def start(self, group: Chat):
        return RunningAuction(self, group, self.app)

    def __str__(self):
        return f"Nome: {self.name}\n" \
               f"Descrizione: {self.description}\n" \
               f"Puntata: {self.priceRaise}\n" \
               f"Massime offerte: {self.offerMaxNumber}\n" \
               f"Tempo: {self.time}'\n" \
               f"Compra subito: {self.buyout}\n"


auctions: List[Auction] = []


class RunningAuction:

    def __init__(self, auction: Auction, group: Chat, app: Client):
        runningAuctions.update({group.id: self})
        self.bidders: Dict[int, int] = {}
        self.auction = auction
        self.actualOffer = int(auction.minimumPrice)
        self.lastOfferingUser: User = None
        self.chat = group
        self.app = app
        self.endingTime = time.mktime(datetime.datetime.now().timetuple()) + auction.time * 60
        self.actualMessage = app.send_message(group.id, auction.name + "\n" + auction.description +
                                              f"\n{emojize(':alarm_clock:', use_aliases=True)} Quest'asta finirà tra: " + auction.time.__str__() + " minuti\n",
                                              reply_markup=self._getAuctionKeyboard())

    def _getAuctionKeyboard(self):
        keyboard = [
            [InlineKeyboardButton(
                "Rilancia: " + self.auction.priceRaise.__str__() + emojize(':dollar:', use_aliases=True),
                callback_data="offer"),
                InlineKeyboardButton("Attuale: " + self.actualOffer.__str__() + "€", callback_data="actualf"),
                InlineKeyboardButton(
                    f"Compra " + self.auction.buyout.__str__() + "€ " + emojize(':exclamation:', use_aliases=True),
                    callback_data="buyout")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def onButtonPress(self, client: Client, callbackQuery: CallbackQuery):
        data = callbackQuery.data
        clickingUser = callbackQuery.from_user
        if data == "offer":
            self.lastOfferingUser = clickingUser
            self.actualOffer += self.auction.priceRaise
            self.actualMessage.delete()
            if self.auction.offerMaxNumber == 0:
                self.actualMessage = self.app.send_message(self.chat.id,
                                                           self.lastOfferingUser.username + " ha rilanciato! ")
            else:
                if clickingUser.id not in self.bidders.keys():
                    self.bidders.update({clickingUser.id: self.auction.offerMaxNumber})
                self.bidders.update({clickingUser.id: self.bidders[clickingUser.id] - 1})
                if self.bidders[clickingUser.id] > 0:
                    self.actualMessage = self.app.send_message(self.chat.id,
                                                               self.lastOfferingUser.username + " ha rilanciato!\n"
                                                                                                f"Ha a disposizione altre: {self.bidders[clickingUser]} puntate.")
            self.actualMessage = self.app.send_message(self.chat.id,
                                                       self.auction.name + "\n" + self.auction.description +
                                                       f"\n{emojize(':alarm_clock:', use_aliases=True)} Quest'asta finirà tra: " + str(int((self.endingTime - time.mktime(datetime.datetime.now().timetuple()))/60)) + " minuti\n"
                                                                                                                                                                 f"L'ultimo puntatore è: @{self.lastOfferingUser.username}",
                                                       reply_markup=self._getAuctionKeyboard())

        elif data == "buyout":
            self.lastOfferingUser = clickingUser
            self.actualOffer = self.auction.buyout
            self.actualMessage.delete()
            self.end()

    def end(self):
        if self.lastOfferingUser is not None:
            self.app.send_message(self.chat.id,
                                  f"Asta finita! {emojize('medal', use_aliases=True)} "
                                  f"Il vincitore: è @{self.lastOfferingUser.username} con un'offerta finale di {self.actualOffer}€!\n"
                                  f" Ricorda di contattare l'admin in privato per riscuotere il premio.")
        else:
            self.app.send_message(self.chat.id,
                                  f"Asta finita! Nessuno ha puntato, quindi nessuno ha vinto.")
        sleep(2)
        del runningAuctions[self.chat.id]


async def _timeOut(auction):
    Thread(target=tread, args=(auction,)).start()


async def tread(auction):
    await wait(auction.auction.time * 60)
    auction.end()


runningAuctions: Dict[int, RunningAuction] = dict()
