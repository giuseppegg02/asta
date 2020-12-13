from enum import Enum
from typing import Dict

from emoji import emojize
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Chat, Message, Photo, CallbackQuery

import Database
from Auction import Auction, auctions


class CreationStatus(Enum):
    MAIN = 1
    NAME_CHANGE = 3
    DESCRIPTION = 4
    PRICE_RAISE = 5
    MAX_OFFERS = 6
    BUY_NW = 7
    TIME = 8
    MINIMUM_PRICE = 9


class AuctionCreator:
    chat: Chat = None

    def __init__(self, chat: Chat, app: Client):
        creatingAuctions.update({chat.id: self})
        self.app = app
        self.name: str = "None"
        self.description: str = "None"
        self.priceRaise: float = 10
        self.offerMaxNumber: int = 0
        self.minimumPrice = 0
        self.buyout = 100
        self.chat = chat
        self.creationStatus: CreationStatus = CreationStatus.MAIN
        self.time = 50
        self.actualMessage: Message = None
        self._redirectToMainMenu()

    def _redirectToMainMenu(self):
        if self.actualMessage is not None:
            self.actualMessage.delete()
        self.creationStatus = CreationStatus.MAIN
        keyboard = [
            [InlineKeyboardButton(emojize(":pencil:", use_aliases=True) + "Nome", callback_data="Nome"),
             InlineKeyboardButton(emojize(":clipboard:", use_aliases=True) + "Informazioni",
                                  callback_data="Informazioni")],
            [InlineKeyboardButton(emojize(":money_with_wings:", use_aliases=True) + "Rilancio",
                                  callback_data="Rilancio"),
             InlineKeyboardButton(emojize(":telephone:", use_aliases=True) + "Numero puntate",
                                  callback_data="Numero puntate"),
             InlineKeyboardButton(emojize(":money_bag:", use_aliases=True) + "Compra subito",
                                  callback_data="Compra subito")],
            [InlineKeyboardButton(emojize(":alarm_clock:", use_aliases=True) + "Tempo", callback_data="Tempo"),
             InlineKeyboardButton(emojize(":dollar:", use_aliases=True) + "Prezzo minimo",
                                  callback_data="Prezzo minimo")],
            [InlineKeyboardButton(emojize(":white_heavy_check_mark:", use_aliases=True) + "Crea",
                                  callback_data="Crea")],
            [InlineKeyboardButton(emojize(":cross_mark:", use_aliases=True) + "Annulla", callback_data="Annulla")]]
        self.actualMessage = self.app.send_message(self.chat.id, "Modifica la nuova asta!\n"
                                                                 f"{emojize(':pencil:',use_aliases=True)} {self.name}\n"
                                                                 f"{emojize(':clipboard:', use_aliases=True)} {self.description}",
                                                   reply_markup=InlineKeyboardMarkup(keyboard))

    def _redirectToPriceRaiseMenu(self):
        self.actualMessage.delete()
        self.creationStatus = CreationStatus.PRICE_RAISE
        keyboard = [
            [InlineKeyboardButton("-1€", callback_data="raiseMenuRemove1"),
             InlineKeyboardButton("-10€", callback_data="raiseMenuRemove"),
             InlineKeyboardButton(self.priceRaise.__str__() + '€', callback_data="price"),
             InlineKeyboardButton("+10€", callback_data="raiseMenuAdd"),
             InlineKeyboardButton("+1€", callback_data="raiseMenuAdd1"), ],
            [InlineKeyboardButton("Back", callback_data="Main")]
        ]
        self.actualMessage = self.app.send_message(self.chat.id, "Modifica il rilancio!",
                                                   reply_markup=InlineKeyboardMarkup(keyboard))

    def _redirectToMaxOffersMenu(self):
        self.actualMessage.delete()
        self.creationStatus = CreationStatus.MAX_OFFERS
        keyboard = [
            [InlineKeyboardButton("-", callback_data="maxOffersMenuRemove"),
             InlineKeyboardButton(self.offerMaxNumber.__str__(), callback_data="maxOffers"),
             InlineKeyboardButton("+", callback_data="maxOffersMenuAdd")],
            [InlineKeyboardButton("Back", callback_data="Main")]
        ]
        self.actualMessage = self.app.send_message(self.chat.id, "Imposta un numero massimo di rilanci!",
                                                   reply_markup=InlineKeyboardMarkup(keyboard))

    def _redirectToTimeMenu(self):
        self.actualMessage.delete()
        self.creationStatus = CreationStatus.TIME
        keyboard = [
            [InlineKeyboardButton("-1'", callback_data="timeMenuRemove1"),
             InlineKeyboardButton("-10'", callback_data="timeMenuRemove"),
             InlineKeyboardButton(self.time.__str__() + "'", callback_data="time"),
             InlineKeyboardButton("+10'", callback_data="timeMenuAdd"),
             InlineKeyboardButton("+1'", callback_data="timeMenuAdd1"), ],
            [InlineKeyboardButton("Back", callback_data="Main")]
        ]
        self.actualMessage = self.app.send_message(self.chat.id, "Scegli il tempo",
                                                   reply_markup=InlineKeyboardMarkup(keyboard))

    def _redirectToBuyOutMenu(self):
        self.actualMessage.delete()
        self.creationStatus = CreationStatus.BUY_NW
        keyboard = [
            [InlineKeyboardButton("-1€", callback_data="buyOutMenuRemove1"),
             InlineKeyboardButton("-10€", callback_data="buyOutMenuRemove"),
             InlineKeyboardButton(self.buyout.__str__() + '€', callback_data="buyout"),
             InlineKeyboardButton("+10€", callback_data="buyOutMenuAdd"),
             InlineKeyboardButton("+1€", callback_data="buyOutMenuAdd1")],
            [InlineKeyboardButton("Back", callback_data="Main")]
        ]
        self.actualMessage = self.app.send_message(self.chat.id, "Modifica il prezzo del compra subito!",
                                                   reply_markup=InlineKeyboardMarkup(keyboard))

    def _redirectToPriceMinimumMenu(self):
        self.actualMessage.delete()
        self.creationStatus = CreationStatus.MINIMUM_PRICE
        keyboard = [
            [InlineKeyboardButton("-1€", callback_data="minimumPriceRemove1"),
             InlineKeyboardButton("-10€", callback_data="minimumPriceRemove"),
             InlineKeyboardButton(self.minimumPrice.__str__() + '€', callback_data="minimumPrice"),
             InlineKeyboardButton("+10€", callback_data="minimumPriceAdd"),
             InlineKeyboardButton("+1€", callback_data="minimumPriceAdd1")],
            [InlineKeyboardButton("Back", callback_data="Main")]
        ]
        self.actualMessage = self.app.send_message(self.chat.id, "Modifica il prezzo minimo!",
                                                   reply_markup=InlineKeyboardMarkup(keyboard))

    def on_private_message(self, client: Client, message: Message):
        message.delete()
        if self.creationStatus == CreationStatus.NAME_CHANGE:
            name = message.text
            self.name = name
        elif self.creationStatus == CreationStatus.DESCRIPTION:
            description = message.text
            self.description = description
        self._redirectToMainMenu()

    def onButtonPress(self, client: Client, callbackQuery: CallbackQuery):
        data = callbackQuery.data
        print("qui arriva")
        if data == "Nome":
            self.app.send_message(self.chat.id, "Inserisci il nome del prodotto!")
            self.creationStatus = CreationStatus.NAME_CHANGE
        elif data == "Immagine":
            self.app.send_message(self.chat.id, "Inserisci l'immagine del prodotto!")
            self.creationStatus = CreationStatus.WAITING_FOR_IMAGE
        elif data == "Informazioni":
            self.app.send_message(self.chat.id, "Inserisci una descrizione del prodotto!")
            self.creationStatus = CreationStatus.DESCRIPTION
        elif data == "Rilancio":
            self.creationStatus = CreationStatus.PRICE_RAISE
            self._redirectToPriceRaiseMenu()
        elif data == "Numero puntate":
            self.creationStatus = CreationStatus.MAX_OFFERS
            self._redirectToMaxOffersMenu()
        elif data == "Compra subito":
            self.creationStatus = CreationStatus.BUY_NW
            self._redirectToBuyOutMenu()
        elif data == "Tempo":
            self.creationStatus = CreationStatus.TIME
            self._redirectToTimeMenu()
        elif data == "Main":
            self.creationStatus = CreationStatus.MAIN
            self._redirectToMainMenu()
        elif data == "Prezzo minimo":
            self.creationStatus = CreationStatus.MINIMUM_PRICE
            self._redirectToPriceMinimumMenu()
        elif data == "Crea":
            auction = self._create()
            self.app.send_message(self.chat.id, "Asta creata!")
            del self
        elif data == "Annulla":
            self.actualMessage.delete()
            self.app.send_message(self.chat.id, "Asta annullata!")
            del self
        elif data == "raiseMenuRemove":
            if self.priceRaise < 2:
                self.priceRaise = 1
            else:
                self.priceRaise -= 10
            self._redirectToPriceRaiseMenu()
        elif data == "raiseMenuAdd":
            self.priceRaise += 10
            self._redirectToPriceRaiseMenu()
        elif data == "raiseMenuRemove1":
            if self.priceRaise < 2:
                self.priceRaise = 1
            else:
                self.priceRaise -= 1
            self._redirectToPriceRaiseMenu()
        elif data == "raiseMenuAdd1":
            self.priceRaise += 1
            self._redirectToPriceRaiseMenu()
        elif data == "maxOffersMenuRemove":
            if self.offerMaxNumber < 0:
                self.offerMaxNumber = 0
            else:
                self.offerMaxNumber -= 1
            self._redirectToMaxOffersMenu()
        elif data == "maxOffersMenuAdd":
            self.offerMaxNumber += 1
            self._redirectToMaxOffersMenu()
        elif data == "timeMenuRemove":
            if self.time < 10:
                self.time = 1
            else:
                self.time -= 10
            self._redirectToTimeMenu()
        elif data == "timeMenuAdd":
            self.time += 10
            self._redirectToTimeMenu()
        elif data == "timeMenuRemove1":
            if self.time < 2:
                self.time = 1
            else:
                self.time -= 1
            self._redirectToTimeMenu()
        elif data == "timeMenuAdd1":
            self.time += 1
            self._redirectToTimeMenu()
        elif data == "buyOutMenuRemove":
            if self.buyout < 10:
                self.buyout = 0
            else:
                self.buyout -= 10
            self._redirectToBuyOutMenu()
        elif data == "buyOutMenuAdd":
            self.buyout += 10
            self._redirectToBuyOutMenu()
        elif data == "buyOutMenuRemove1":
            if self.buyout < 1:
                self.buyout = 0
            else:
                self.buyout -= 1
            self._redirectToBuyOutMenu()
        elif data == "buyOutMenuAdd1":
            self.buyout += 1
            self._redirectToBuyOutMenu()
        elif data == "minimumPriceRemove":
            if self.minimumPrice < 10:
                self.minimumPrice = 0
            else:
                self.minimumPrice -= 10
            self._redirectToPriceMinimumMenu()
        elif data == "minimumPriceAdd":
            self.minimumPrice += 10
            self._redirectToPriceMinimumMenu()
        elif data == "minimumPriceRemove1":
            if self.minimumPrice < 1:
                self.minimumPrice = 0
            else:
                self.minimumPrice -= 1
            self._redirectToPriceMinimumMenu()
        elif data == "minimumPriceAdd1":
            self.minimumPrice += 1
            self._redirectToPriceMinimumMenu()

    def _create(self) -> Auction:
        self.actualMessage.delete()
        auction = Auction(self.name, self.description, self.priceRaise, self.offerMaxNumber, self.time, self.buyout, self.minimumPrice,
                          self.app)
        Database.storeAuction(auction)
        auctions.append(auction)
        return auction


creatingAuctions: Dict[int, AuctionCreator] = {}
