import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
import datetime
import time
import requests
import os
import logging
from CurrencyBotConfig import API_TOKEN


logging.getLogger('telebot').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.basicConfig(filename = "CurrencyBot.log", level = logging.DEBUG, format = '%(asctime)s - %(message)s')


bot = telebot.TeleBot(API_TOKEN)

hideboard = ReplyKeyboardRemove()


def listener(messages):
    for m in messages:
        logging.info(f"THIS IS LISTENER!\n@{m.chat.username}, Name: {m.chat.first_name} ||| {datetime.datetime.today() : '%c'}, type:{m.content_type}, Message:\n{m.text}")


bot.set_update_listener(listener)



valuess = list()
message_symbol_cnnection = dict()
user_steps = dict()
user_data = dict()


commands = {

    "start"     :       "start the bot", #(default redirects to the mainpage)
    "help"      :       "show help menu",
    
}






def CryptoPrice(SYMBOL, exchange, cid):    
    
    if exchange == "NOBITEX":
        if SYMBOL[-4:] == "USDT" or SYMBOL[-3:] == "IRT":
            nobitexResponse = requests.get(f'https://api.nobitex.ir/v3/orderbook/{SYMBOL}')
            CurrencyPrice = float(nobitexResponse.json()["lastTradePrice"])
            now = datetime.datetime.today()
            if SYMBOL[-4:] == "USDT":
                #bot.send_message(cid, f"{SYMBOL} Price: {CurrencyPrice}💲")
                logging.info(f"Got Price from {exchange}, SYMBOL: {SYMBOL}, Price: {CurrencyPrice} ||| Success!")
                return CurrencyPrice
            else:
                #bot.send_message(cid, f"{SYMBOL} Price: {CurrencyPrice} Riyal")
                logging.error(f"Couldn't get price from {exchange}, SYMBOL: {SYMBOL}, possible error: {CurrencyPrice} ||| Failure!")
                return CurrencyPrice
        else:
            logging.error(f"{cid} - Couldn't get price from {exchange}, SYMBOL: {SYMBOL}, possible error: currency not available in this exchange ||| Failure!")
            return "We couldn't recognise your desired cryptocurrency, may not be available on exchange or you entered invalid symbol of currency."
    
    
    elif exchange == "KUCOIN":
        currency = SYMBOL[:-4] + "-" + SYMBOL[-4:]
        kucoinResponse = requests.get(f'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={currency.upper()}')
        CurrencyPrice = float(kucoinResponse.json()["data"]["price"])
        now = datetime.datetime.today()
        if SYMBOL[-4:] == "USDT":
            #bot.send_message(cid, f"{SYMBOL} Price: {CurrencyPrice}💲")
            logging.info(f"Got Price from {exchange}, SYMBOL: {SYMBOL}, Price: {CurrencyPrice} ||| Success!")
            return CurrencyPrice
        else:
            #bot.send_message(cid, "We couldn't recognise your desired cryptocurrency, may not be available on exchange or you entered invalid symbol of currency.")
            logging.error(f"Couldn't get price from {exchange}, SYMBOL: {SYMBOL}, possible error: {CurrencyPrice} ||| Failure!")
            return "Currency is not available in this exchange"
    

    else:
        logging.error(f"Exchange {exchange} not found in options. available ones: Nobitex & Kucoin.")
        return "Wrong exchange!"

def CurrencyByCurrency(SYMBOL, SYMBOL2, exchange, cid):
    
    SYMBOLPrice = CryptoPrice(SYMBOL, exchange, cid)   
    SYMBOL2Price = CryptoPrice(SYMBOL2, exchange, cid)   
    logging.debug(f"SYMBOL1 price: {SYMBOLPrice} & SYMBOL2 price: {SYMBOL2Price}")
    PriceSymToSym2 = SYMBOLPrice / SYMBOL2Price
    logging.debug(f"SYMBOL1 to SYMBOL2 price: {PriceSymToSym2:.4f}")
    return PriceSymToSym2
    
def GetCryptoHistoryFile(SYMBOL,exchange, Filename, duration, period, cid, mid):


    timestamp = time.time()
    nextRefresh = timestamp + int(duration)
    now = time.time()
    os.makedirs(os.path.join("Data", str(cid), f"ReportOf{SYMBOL}"), exist_ok= True)
    logging.debug(f"Directory folder /''{os.path.join('Data', str(cid), f'ReportOf{SYMBOL} ')}''\\ created")
    dotcount = 0
    while now <= nextRefresh:
        bot.edit_message_text("Making your report ready" + dotcount * ".", cid, mid)
        if dotcount == 6:
            dotcount = 0
        
        dotcount +=2
        now = time.time()
        logging.debug(f"Sleep for {period} seconds")
        time.sleep(int(period))
        formatednowtime = datetime.datetime.fromtimestamp(now + int(period))
        currencyprice = CryptoPrice(SYMBOL, exchange, cid)
        
        logging.info(f"Successfully got the {SYMBOL} price from {exchange} price: {currencyprice}")
        
        content = f"{formatednowtime: %Y-%m-%d %H:%M:%S}     /''{SYMBOL}''\\   Price: {currencyprice}$\n"
        
        logging.info(f"Content: {content}")

        with open(os.path.join("Data", str(cid), f"ReportOf{SYMBOL}", f"{Filename}.txt"), 'a') as f:
            f.write(content)
            logging.info(f"Wrote content in file {Filename} successfully.")

    with open(os.path.join("Data", str(cid), f"ReportOf{SYMBOL}", f"{Filename}.txt"), 'r') as f:
        bot.send_document(cid, f, caption= "Here is your report")
        logging.info(f"Successfully sent document to user:{cid}")
    bot.edit_message_text("Done on making your report!", cid, mid)
    logging.info(f"Success on getting crypto history file")




@bot.callback_query_handler(func = lambda call: True)
def callback_handler(call):
    call_id = call.id
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data
    logging.info(f"Call info: call_id: {call_id} ||| cid: {cid} ||| mid: {mid} ||| data: {data}")
    
    if data.split("_")[0] == "backto":
        if data.split("_")[-1] == "mainpage":
            bot.delete_message(cid, mid)
            logging.info(f"Deleted message ID {mid} for user {cid}")
            mainpage(call.message)
        elif data.split("_")[-1] == "keep":
            logging.info(f"User {cid} kept updater and returned to the mainpage. message: {mid}")
            mainpage(call.message)
        
                #  InlineKeyboardButton("NOT-USDT", callback_data= "symbol2_NOTUSDT_userstep_C"))
                # keyboard.add(InlineKeyboardButton("BTC-USDT", callback_data= "symbol_BTCUSDT_userstep_D"),
    
    elif data.split("_")[-1] == "fastaccess":
        if data.split("_")[0] == "symbol":
            
            user_data[cid]['symbol'] = data.split("_")[1]
            logging.info(f"Symbol for userdata {cid} is {data.split("_")[1]}")

            user_steps[cid] = data.split("_")[-2]

            if user_steps[cid] == "A":
                logging.info(f"Userstep {cid} is: {user_steps[cid]}")
                user_step_A_Getprice_handler(call.message)

            elif user_steps.get(cid) == "B":
                logging.info(f"Userstep {cid} is: {user_steps[cid]}")
                user_step_B_GetPriceByCurr_handler(call.message)

            elif user_steps.get(cid) == "D":
                    logging.info(f"Userstep {cid} is: {user_steps[cid]}")
                    user_data[cid]["symbol"] = data.split("_")[1]
                    bot.send_message(cid, "Please enter your file name, only use letters and numbers! ")
                    user_steps[cid] = "E"

        elif data.split("_")[0] == "symbol2":
            
            SYMBOL2 = data.split("_")[1]
            logging.info(f"Second symbol for curr by curr is: {SYMBOL2}")
            user_data[cid]['symbol2'] = SYMBOL2
            user_steps[cid] = data.split("_")[-2]
            user_step_C_GetPriceByCurr_handler(call.message)

    elif data.split("_")[0] == "exchange":

        
        if data.split("_")[1] == "nobitex":
            bot.answer_callback_query(call_id, "Nobitex is not available right now")
            logging.info(f"User {cid} chose exchange nobitex which is not available.")
            return
            exchange = "NOBITEX"
            SYMBOL = user_data.get(cid, {}).get("symbol")
            CryptoPrice(SYMBOL, exchange, cid)
            mainpage(call.message)

        elif data.split("_")[1] == "kucoin":
            exchange = "KUCOIN"
            
                                #userdata[cid]['symbol]
            message_symbol_cnnection.setdefault(cid, {}).get(mid)
            # attempted_SYMBOL = message_symbol_cnnection.get(cid, {}).get(mid)    #message_symbol_cnnection[cid][mid] 
            
            # print(attempted_SYMBOL)
            # print(attempted_SYMBOL)
            

            if message_symbol_cnnection[cid].get(mid) is None:
                SYMBOL = user_data.get(cid, {}).get("symbol")      
                logging.info(f"SYMBOL {SYMBOL} for message ID {mid} and {cid} was not set. set: ''{message_symbol_cnnection[cid].get(mid)}''")

            else:
                SYMBOL = message_symbol_cnnection[cid][mid]
                logging.info(f"SYMBOL {SYMBOL} for message ID {mid} and {cid} was set before. set: ''{message_symbol_cnnection[cid][mid]}")
            
            logging.info(f"User {cid} chose kucoin exchange, SYMBOL: {SYMBOL}")
 

            try:

                CryptoPriceAnswer = CryptoPrice(SYMBOL, exchange, cid)

            except TypeError:
                logging.error(f"Faced with TypeError! the returned value of CryptoPriceAnswer is: ")
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("Back", callback_data= "backto_mainpage"))
                bot.edit_message_text( "You entered wrong currency symbol or currency not available in this exchange, click on Back button to reach the mainpage",cid, mid, reply_markup= keyboard)
                
                user_data.pop(cid)
                user_steps.pop(cid)
                logging.info(f"Removed data and steps of user: {cid}")
            else:
                logging.info(f"Sueccessfully got {SYMBOL} price from {exchange} for {cid} ")
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton(f"Get {SYMBOL} price again", callback_data= f"exchange_kucoin_{SYMBOL}" ))
                keyboard.add(InlineKeyboardButton("Back to mainpage and keep this updater", callback_data= "backto_mainpage_keep"))
                keyboard.add(InlineKeyboardButton("Back to mainpage", callback_data= "backto_mainpage"))




                if type(CryptoPriceAnswer) == float:
                    

                        for key, value in message_symbol_cnnection[cid].items():
                            valuess.append(value)
                            
                        if SYMBOL in valuess:
                            for k, v in message_symbol_cnnection[cid].items():

                                if SYMBOL == v:
                                    mid = k
                                    SYMBOL = v
                                    
                                    break
                                else:
                                    logging.error(f"For user {cid} something went wrong. Message: {k}, Symbol: {v}, LINE: around 250")
                                
                            
                            bot.edit_message_text(f"{SYMBOL} Price: {CryptoPriceAnswer}💲, update: {datetime.datetime.today(): '%H:%M:%S'}", cid, mid, reply_markup= keyboard)
                            logging.info(f"Edited message {mid} by {SYMBOL} for user {cid}")
                        elif SYMBOL not in valuess:
                            bot.edit_message_text(f"{SYMBOL} Price: {CryptoPriceAnswer}💲, update: {datetime.datetime.today(): '%H:%M:%S'}", cid, mid, reply_markup= keyboard)
                            logging.info(f"Edited message {mid} by {SYMBOL} for user {cid}, first time to use this SYMBOL")
                            message_symbol_cnnection[cid][mid] = SYMBOL
                            logging.info(f"user {cid} added {SYMBOL} to their symbol connection: {message_symbol_cnnection[cid]}")
                            
                                

                else:
                    logging.error(f"Something happened! possible error: {CryptoPriceAnswer}, while writing code's possible idea: Crypto answer is NOT floated!")
                    bot.edit_message_text(CryptoPriceAnswer)
                    user_data.pop(cid)
                    user_steps.pop(cid)
                    logging.info(f"Popped data and steps of user {cid}")

    elif data.split("_")[0] == "CurrByCurr":
        if data.split("_")[2] == "nobitex":
            bot.answer_callback_query(call_id, "Nobitex is not available right now")
            logging.info(f"User {cid} chose exchange nobitex which is not available.")
            return
            exchange = "NOBITEX"
            SYMBOL = data.split("_")[-2]
            SYMBOL2 = data.split("_")[-1]
            CurrencyByCurrency(SYMBOL,SYMBOL2, exchange, cid)
            mainpage(call.message)

        elif data.split("_")[2] == "kucoin":
            exchange = "KUCOIN"
            SYMBOL = data.split("_")[-2]
            SYMBOL2 = data.split("_")[-1]
            logging.info(f"user {cid} is using CurrByCurr with Symbol1:{SYMBOL} & Symbol2:{SYMBOL2}")
            try:
                CryptoPriceAnswer = CurrencyByCurrency(SYMBOL,SYMBOL2, exchange, cid)
            except TypeError:
                logging.error(f"user {cid} Faced with TypeError! the returned value of CryptoPriceAnswer is: {CryptoPriceAnswer}")
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("Back", callback_data= "backto_mainpage"))
                bot.edit_message_text( "You entered wrong currency symbol or currency not available in this exchange, click on Back button to reach the mainpage",cid, mid, reply_markup= keyboard)
            else:
                logging.info(f"user {cid} successfully got the CryptoPrice SymToSym")
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton(f"Get {SYMBOL[:-4]}/{SYMBOL2[:-4]} price again", callback_data= f"CurrByCurr_exchange_kucoin_{SYMBOL}_{SYMBOL2}" ))
                keyboard.add(InlineKeyboardButton("Back to mainpage and keep this updater", callback_data= "backto_mainpage_keep"))
                keyboard.add(InlineKeyboardButton("Back to mainpage", callback_data= "backto_mainpage"))
                
                if type(CryptoPriceAnswer) == float:
                    bot.edit_message_text(f"{SYMBOL[:-4]}/{SYMBOL2[:-4]} Price: {CryptoPriceAnswer:.4f}💲, update: {datetime.datetime.today(): '%H:%M:%S'}", cid, mid, reply_markup= keyboard)
                    logging.info(f"Successfully sent price of {SYMBOL[:-4]}/{SYMBOL2[:-4]} on mid {mid} and cid {cid}")
                
                else:
                    logging.error(f"user {cid} Faced with ValueError! the returned value of CryptoPriceAnswer is: {CryptoPriceAnswer}")
                    bot.edit_message_text(CryptoPriceAnswer)
                    


    elif data.split("_")[0] == "HistoryFile":
        if data.split("_")[2] == "nobitex":
            bot.answer_callback_query(call_id, "Nobitex is not available right now")      
            logging.info(f"User {cid} chose exchange nobitex which is not available.")
            return      
            exchange = "NOBITEX"
            SYMBOL = user_data[cid]['symbol']
            Filename = user_data[cid]['Filename']
            duration = user_data[cid]['duration']
            period = user_data[cid]['period']
            GetCryptoHistoryFile(SYMBOL,exchange, Filename, duration, period, cid, mid)
            mainpage(call.message)


        elif data.split("_")[2] == "kucoin":
            exchange = "KUCOIN"
            logging.info(f"user {cid} entered historyfile section.")
            SYMBOL = user_data[cid]['symbol']
            Filename = user_data[cid]['Filename']
            duration = user_data[cid]['duration']
            period = user_data[cid]['period']
            logging.info(f"SYMBOL : {SYMBOL}, filename: {Filename}, duration: {duration}, period: {period}, cid: {cid}")
            GetCryptoHistoryFile(SYMBOL,exchange, Filename, duration, period, cid, mid)
            user_steps.pop(cid)
            user_data.pop(cid)
            logging.info(f"Popped user data and steps {cid}")
            logging.debug(f"Successfully done GetCryptoHistoryFile for {cid}")
            mainpage(call.message)
   



    




@bot.message_handler(commands = ["start"])
def mainpage(message):
    cid = message.chat.id
    keyboard = ReplyKeyboardMarkup()
    keyboard.add("Get Crypto Price 💲", "Get Price of a currency by another currency 💱")
    keyboard.add("Get crypto history report in a .txt file 📁", "Help 💡")
    bot.send_message(cid, "Welcome to our bot, please choose one of the options to continue", reply_markup = keyboard)


@bot.message_handler(commands = ['help'])
def show_help_menu(message):
    cid = message.chat.id
    text = ""
    for command, desc in commands.items():
        text += f"/{command} : {desc}\n"
    bot.send_message(cid, text)



@bot.message_handler(func = lambda message: message.text == "Get Crypto Price 💲")
def button_Get_Crypto_Price_handler(message):
    cid = message.chat.id
    user_data.setdefault(cid, {'symbol' : None, 'exchange' : None})
    if user_data.get(cid)['symbol'] is not None:
        user_data[cid]['symbol'] = None
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("BTC-USDT", callback_data= "symbol_BTCUSDT_userstep_A_fastaccess"),
                 InlineKeyboardButton("ETH-USDT", callback_data= "symbol_ETHUSDT_userstep_A_fastaccess"),
                 InlineKeyboardButton("NOT-USDT", callback_data= "symbol_NOTUSDT_userstep_A_fastaccess"))
    
    bot.send_message(cid, "Please enter the symbol of currency\n(Example: BTCUSDT -- BTCIRT -- ETHIRT -- ETHUSDT)\nUse buttons for fast access ", reply_markup=keyboard)  
    user_steps[cid] = "A"
    

@bot.message_handler(func = lambda message: message.text == "Get Price of a currency by another currency 💱")
def button_Get_Crypto_Price_CurrByCurrhandler(message):
    cid = message.chat.id
    user_data.setdefault(cid, {'symbol' : None, 'exchange' : None, 'symbol2' : None})
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("BTC-USDT", callback_data= "symbol_BTCUSDT_userstep_B_fastaccess"),
                 InlineKeyboardButton("ETH-USDT", callback_data= "symbol_ETHUSDT_userstep_B_fastaccess"),
                 InlineKeyboardButton("NOT-USDT", callback_data= "symbol_NOTUSDT_userstep_B_fastaccess"))
    bot.send_message(cid, "Please enter the symbol of first currency\n (Example: BTCUSDT -- BTCIRT -- ETHIRT -- ETHUSDT)\n Use buttons for fast access ", reply_markup=keyboard)  
    user_steps[cid] = "B"


@bot.message_handler(func = lambda message: message.text == "Get crypto history report in a .txt file 📁")
def button_Get_Crypto_Price_InReport_handler(message):
    cid = message.chat.id
    user_data.setdefault(cid, {'symbol' : None, 'exchange' : None,'Filename' : None, "period": None, "duration": None})
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("BTC-USDT", callback_data= "symbol_BTCUSDT_userstep_D_fastaccess"),
                 InlineKeyboardButton("ETH-USDT", callback_data= "symbol_ETHUSDT_userstep_D_fastaccess"),
                 InlineKeyboardButton("NOT-USDT", callback_data= "symbol_NOTUSDT_userstep_D_fastaccess"))
    bot.send_message(cid, "Please enter the symbol of currency\n (Example: BTCUSDT -- BTCIRT -- ETHIRT -- ETHUSDT)\n Use buttons for fast access ", reply_markup=keyboard)  
    user_steps[cid] = "D"


@bot.message_handler(func = lambda message: message.text == "Help 💡")
def button_Help_handler(message):
    show_help_menu(message)

    

#--------------------------
#--------------------------
#--------------------------



@bot.message_handler(func = lambda message: user_steps.get(message.chat.id) == "A")
def user_step_A_Getprice_handler(message):   
    cid = message.chat.id 
    if user_data.get(cid)['symbol'] is None:
        SYMBOL = message.text.upper()

        user_data[cid]["symbol"] = SYMBOL
        logging.info(f"user {cid} symbol: {SYMBOL}")



    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Nobitex", callback_data = "exchange_nobitex"),
        InlineKeyboardButton("Kucoin", callback_data = "exchange_kucoin"))
    markup.add(InlineKeyboardButton("Back", callback_data= "backto_mainpage"))

    bot.send_message(cid, "Please choose the exchange you want to get the price of your desired Currency from", reply_markup = markup)


#--------------------------
#--------------------------
#--------------------------



@bot.message_handler(func= lambda message: user_steps.get(message.chat.id) == "B")
def user_step_B_GetPriceByCurr_handler(message):   
    cid = message.chat.id 
    if user_data[cid].get('symbol') is None:
        SYMBOL = message.text.upper()
        user_data[cid]["symbol"] = SYMBOL
    

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("BTC-USDT", callback_data= "symbol2_BTCUSDT_userstep_C_fastaccess"),
                 InlineKeyboardButton("ETH-USDT", callback_data= "symbol2_ETHUSDT_userstep_C_fastaccess"),
                 InlineKeyboardButton("NOT-USDT", callback_data= "symbol2_NOTUSDT_userstep_C_fastaccess"))
    bot.send_message(cid, f"Please enter the symbol of second currency (Example: BTCUSDT -- BTCIRT -- ETHIRT -- ETHUSDT)\n Use buttons for fast access or type the symbol ",reply_markup= keyboard)
    
    user_steps[cid] = "C"

@bot.message_handler(func= lambda message: user_steps.get(message.chat.id) == "C")
def user_step_C_GetPriceByCurr_handler(message):
    cid = message.chat.id
    print(user_data[cid])
    if user_data[cid].get('symbol2') is None:
        SYMBOL2 = message.text.upper()
        user_data[cid]['symbol2'] = SYMBOL2
    markup = InlineKeyboardMarkup()
    markup.add(
    InlineKeyboardButton("Nobitex", callback_data = f"CurrByCurr_exchange_nobitex_{user_data[cid]['symbol']}_{user_data[cid]['symbol2']}"),
    InlineKeyboardButton("Kucoin", callback_data = f"CurrByCurr_exchange_kucoin_{user_data[cid]['symbol']}_{user_data[cid]['symbol2']}"))
    markup.add(InlineKeyboardButton("Back", callback_data= f"backto_mainpage" ))
    bot.send_message(cid, "Please choose the exchange you want to get the price of your desired Currency from", reply_markup = markup)




#--------------------------
#--------------------------
#--------------------------



@bot.message_handler(func= lambda message: user_steps.get(message.chat.id) == "D")
def user_step_D_GetCryptoHistoryFile_handler(message):
    cid = message.chat.id
    if user_data[cid].get('symbol') is None:
        SYMBOL = message.text.upper()
        user_data[cid]["symbol"] = SYMBOL
    bot.send_message(cid, "Please enter your file name, only use letters and numbers! ")
    user_steps[cid] = "E"

@bot.message_handler(func= lambda message: user_steps.get(message.chat.id) == "E")
def user_step_E_GetCryptoHistoryFile_handler(message):
    cid = message.chat.id  
    Filename =  message.text
    for Char in Filename.split():
        if Char in ["/" , "\\" , ">" , "<" , '"' , ":" , "?" , "*" , "|"]:
            bot.send_message(cid, 'You entered invalid characters in your file. (Forbidden characters: / - \\ - > - < - " - : - ? - * - |)', reply_to_message_id= message.message_id)
            logging.error(f"User {cid} entered invalid characters for their filename: {Filename}")
            mainpage(message)
        else:
            user_data[cid]['Filename'] = Filename
            bot.send_message(cid, f"Now enter the duration you want to get price of {user_data[cid]['symbol']} in seconds: ")
            user_steps[cid] = "F"
    
@bot.message_handler(func= lambda message: user_steps.get(message.chat.id) == "F")
def user_step_F_GetCryptoHistoryFile_handler(message):
    cid = message.chat.id   
    duration = message.text
    try:
        user_data[cid]['duration'] = int(duration)
        bot.send_message(cid, f"Now enter the period you want to get the price currency in seconds(Example: every ''10'' seconds): ")
        user_steps[cid] = "G"
    except ValueError:
        logging.error(f"user {cid} Faced with ValueError! the returned value of duration is: {duration}")
        bot.send_message(cid, "You entered wrong duration value, please enter only NUMBERS! Heading you to the mainpage")
        mainpage(message)

@bot.message_handler(func= lambda message: user_steps.get(message.chat.id) == "G")
def user_step_G_GetCryptoHistoryFile_handler(message):
    cid = message.chat.id   
    period = message.text
    try:
        user_data[cid]['period'] = int(period)
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Nobitex", callback_data = f"HistoryFile_exchange_nobitex"),
            InlineKeyboardButton("Kucoin", callback_data = f"HistoryFile_exchange_kucoin"))
        markup.add(InlineKeyboardButton("Back", callback_data= f"backto_mainpage" ))
        bot.send_message(cid, "Please choose the exchange you want to get the price of your desired Currency from", reply_markup = markup)
        
    except ValueError:
        logging.error(f"user {cid} Faced with ValueError! the returned value of period is: {period}")
        bot.send_message(cid, "You entered wrong period value, please enter only NUMBERS! Heading you to the mainpage")
        
        user_steps.pop(cid)
        user_data.pop(cid)
        logging.info(f"Popped user data and steps {cid}")
        mainpage(message)
        










bot.infinity_polling()