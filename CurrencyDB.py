import requests
import datetime
import time
import mysql.connector
import logging
from CurrencyBotConfig import *
 

logging.basicConfig(filename = "CurrencyDB.log", level = logging.DEBUG, format = '%(asctime)s - %(message)s')

#DATABASE_CT
def create_n_drop():
    connection = mysql.connector.connect(user=config['user'], password=config['password'], host=config['host'])
    cur = connection.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {DATABASE};")
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE};")
    connection.commit()
    cur.close()
    connection.close()
    logging.debug(f'database {DATABASE} created successfully')


#DDL
def ct_EXCHANGE():
    connection = mysql.connector.connect(**config)
    cur = connection.cursor()
    cur.execute("""
    CREATE TABLE EXCHANGE (
    ID                  MEDIUMINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    NAME                VARCHAR(10) NOT NULL UNIQUE,
    EXCHANGE_RESERVE    VARCHAR(100) NOT NULL,
    USERS               INT NOT NULL,
    REGISTER_DATE       DATETIME DEFAULT CURRENT_TIMESTAMP,
    LAST_UPDATE         TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
    """)
    logging.debug(f'table EXCHANGE created successfully')

def ct_GET_CURRENCY_PRICE():
    connection = mysql.connector.connect(**config)
    cur = connection.cursor()
    cur.execute("""
    CREATE TABLE SAVE_CURRENCY_PRICE (
    ID       MEDIUMINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    NAME     VARCHAR(10) NOT NULL,
    PRICE    VARCHAR(50) NOT NULL ,
    EXCHANGE    VARCHAR(15) NOT NULL,
    REGISTER_DATE   DATETIME DEFAULT CURRENT_TIMESTAMP,
    LAST_UPDATE     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
    """)
    logging.debug(f'table SAVE_CURRENCY_PRICE created successfully')

def ct_GET_CRYPTO_HISTORY():
    connection = mysql.connector.connect(**config)
    cur = connection.cursor()
    cur.execute(f"DROP TABLE IF EXISTS GET_CRYPTO_HISTORY;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS GET_CRYPTO_HISTORY (
    ID       MEDIUMINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
    NAME     VARCHAR(10) NOT NULL,
    PRICE    VARCHAR(50) NOT NULL,
    EXCHANGE VARCHAR(20) NOT NULL,
    DATE     DATETIME DEFAULT CURRENT_TIMESTAMP,
    REGISTER_DATE   DATETIME DEFAULT CURRENT_TIMESTAMP,
    LAST_UPDATE     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
    """)
    logging.debug(f'table GET_CRYPTO_HISTORY created successfully')




#DML
def insert_EXCHANGE_data(name, exchange_reserve, users):
    connection = mysql.connector.connection.MySQLConnection(**config)
    cur = connection.cursor()
    SQL_Query = "INSERT INTO EXCHANGE (NAME, EXCHANGE_RESERVE, USERS) VALUES (%s, %s, %s);"
    cur.execute(SQL_Query, (name, exchange_reserve, users))
    exc_id = cur.lastrowid
    connection.commit()
    cur.close()
    connection.close()
    logging.debug(f'Exchange data id: {exc_id} inserted successfully')


def insert_CURRENCY_PRICE_data(SYMBOL, exchange):
    connection = mysql.connector.connection.MySQLConnection(**config)
    cur = connection.cursor()
    SQL_Query = "INSERT INTO SAVE_CURRENCY_PRICE (NAME, PRICE, EXCHANGE) VALUES (%s, %s, %s);"

    price = CryptoPrice(SYMBOL, exchange)
    
    cur.execute(SQL_Query, (SYMBOL, price, exchange))
    curr_id = cur.lastrowid
    connection.commit()
    cur.close()
    connection.close()
    logging.debug(f'Currency data id: {curr_id} inserted successfully')


def insert_CRYPTO_HISTORY(SYMBOL, currencyprice,exchange, date=None):
    connection = mysql.connector.connection.MySQLConnection(**config)
    cur = connection.cursor()
    if date is None:
        SQL_Query = SQL_Query = "INSERT INTO GET_CRYPTO_HISTORY (NAME,PRICE,EXCHANGE) VALUES (%s, %s, %s);"
        values = (SYMBOL, currencyprice, exchange)
    else:
        SQL_Query = "INSERT INTO GET_CRYPTO_HISTORY (NAME,PRICE,EXCHANGE,DATE) VALUES (%s, %s, %s, %s);"
        values = (SYMBOL, currencyprice, exchange, date)
  
    cur.execute(SQL_Query, values)
    CryptoHistory_id = cur.lastrowid
    connection.commit()
    cur.close()
    connection.close()
    print(f'CryptoHistory data id: {CryptoHistory_id} inserted successfully')



###CRYPTOSECTION
def CryptoPrice(SYMBOL, exchange):    
    
    if exchange == "NOBITEX":
        
        if SYMBOL[-4:] == "USDT" or SYMBOL[-3:] == "IRT":
            nobitexResponse = requests.get(f'https://api.nobitex.ir/v3/orderbook/{SYMBOL}')
            CurrencyPrice = float(nobitexResponse.json()["lastTradePrice"])
            now = datetime.datetime.today()
            if SYMBOL[-4:] == "USDT":
                logging.info(f"{now : %c} ''{SYMBOL}'' Price: {CurrencyPrice}$")
                print(f"{now : %c} ''{SYMBOL}'' Price: {CurrencyPrice}$")
                return CurrencyPrice
            else:
                logging.info(f"{now : %c} ''{SYMBOL}'' Price: {CurrencyPrice} Riyal")
                print(f"{now : %c} ''{SYMBOL}'' Price: {CurrencyPrice} Riyal")
                return CurrencyPrice
        else:

            print("We couldn't recognise your desired cryptocurrency, may not be available on exchange or you entered invalid symbol of currency.")
    
    
    elif exchange == "KUCOIN":
        currency = SYMBOL[:-4] + "-" + SYMBOL[-4:]
        kucoinResponse = requests.get(f'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={currency.upper()}')
        CurrencyPrice = float(kucoinResponse.json()["data"]["price"])
        now = datetime.datetime.today()
        if SYMBOL[-4:] == "USDT":
            logging.info(f"{now : %c} ''{currency.upper()}'' Price: {CurrencyPrice}$")
            print(f"{now : %c} ''{currency.upper()}'' Price: {CurrencyPrice}$")
            return CurrencyPrice
        else:
            print("We couldn't recognise your desired cryptocurrency, may not be available on exchange or you entered invalid symbol of currency.")
    
    

    else:
        "Wrong exchange!"


def DefinedTimeCryptoPrice(seconds,SYMBOL, exchange):
    timestamp = time.time()
    nextRefresh = timestamp + seconds
    FormatedNextRefresh = datetime.datetime.fromtimestamp(nextRefresh)
    print(f"You will get the price of {SYMBOL} in {seconds} seconds, on: {FormatedNextRefresh : '%c'}")

    # while True:
    #     now = time.time()
    #     if now >= nextRefresh:
    #        CryptoPrice(SYMBOL)
    #        break
    
    
    time.sleep(seconds)
    CryptoPrice(SYMBOL, exchange)
    choice = input(f"Do you want to get the price of {SYMBOL} in {seconds} seconds again are not? you can change the price and SYMBOL in ''yes'' section(y/n): ")
    if choice == "y":
        print(choice)
        SYMBOLChange = input("Do you want to change the SYMBOL and time(y/n)? ")
        
        if SYMBOLChange == "y" or "Y" or "yes":
            try:
                SYMBOL = input("Please enter the symbol of currency you want to get price of (Example: BTCUSDT -- BTCIRT -- ETHIRT -- ETHUSDT): ").upper()
                seconds = int(input(f"Please enter the time in seconds which you want to continously get price of {SYMBOL}: "))
                trytimes = int(input(f"Please enter the times you want to get price of {SYMBOL} in number(enter 1 if you want it only once): "))
            
            except ValueError:
                print("Please enter only numbers!")
                logging.error("Wrong input for one of inputs seconds or trytimes")
            else:
                print(f"You are going to get price of {SYMBOL} every {seconds} seconds for {trytimes} times.")
                for i in range(trytimes):
                    time.sleep(seconds)
                    CryptoPrice(SYMBOL, exchange)
        elif SYMBOLChange == "n" or "N" or "no":
            print(f"You are going to get price of {SYMBOL} in {seconds} seconds.")
            time.sleep(seconds)
            CryptoPrice(SYMBOL, exchange)
        
        else:
            print("Wrong input. Hope you have a wonderful day!")
            logging.error("Wrong input for one of inputs seconds or trytimes")
            
    elif choice == "n":
        print("We see you want to leave the section. Wish you a wonderful day!")
    

    else:
        print("Wrong input. Hope you have a wonderful day!")
        logging.error("Wrong input for one of inputs seconds or trytimes")


def CurrencyByCurrency(SYMBOL, SYMBOL2, exchange):
    
    SYMBOLPrice = CryptoPrice(SYMBOL, exchange)   
    SYMBOL2Price = CryptoPrice(SYMBOL2, exchange)   

    PriceSymToSym2 = SYMBOLPrice / SYMBOL2Price
    print(f"Here is the price of {SYMBOL[:-4]}/{SYMBOL2[:-4]}: {PriceSymToSym2:.4f}$")
    return PriceSymToSym2


def GetCryptoHistoryFunc(SYMBOL, exchange):

    try:    
        duration = int(input(f"Now enter the duration you want to get price of {SYMBOL} in seconds: "))
        period = int(input(f"Now enter the period you want to get the price currency in seconds(Example: every ''10'' seconds): "))
        choice = input("You want to save this report in: 1- Database only | 2- File only | 3- Database and file: ")
    except ValueError:
        print("Enter only numbers!")
    else:
        if choice == "1":
            timestamp = time.time()
            nextRefresh = timestamp + duration
            ct_GET_CRYPTO_HISTORY()
            now = time.time()
            while now <= nextRefresh:
                now = time.time()
                time.sleep(period)
                currencyprice = CryptoPrice(SYMBOL, exchange)

                insert_CRYPTO_HISTORY(SYMBOL, currencyprice, exchange)
            logging.debug(f"One price imported in database {DATABASE}")




        elif choice == "2":
            FileName = input("Please enter your file name, only use letters and numbers: ")
            timestamp = time.time()
            nextRefresh = timestamp + duration
            now = time.time()
            while now <= nextRefresh:
                now = time.time()
                time.sleep(period)
                formatednowtime = datetime.datetime.fromtimestamp(now + period )
                currencyprice = CryptoPrice(SYMBOL, exchange)
                content = f"{formatednowtime: %Y-%m-%d %H:%M:%S} Price: {currencyprice}$\n"
                
                with open(FileName + ".txt", "a") as f:
                    f.write(content)
            logging.debug(f"One price imported in file {FileName}")



        elif choice == "3":
            FileName = input("Please enter your file name, only use letters and numbers: ")
            timestamp = time.time()
            nextRefresh = timestamp + duration
            ct_GET_CRYPTO_HISTORY()
            now = time.time()
            while now <= nextRefresh:
                now = time.time()
                time.sleep(period)
                currencyprice = CryptoPrice(SYMBOL, exchange)
                insert_CRYPTO_HISTORY(SYMBOL, currencyprice, exchange)
                formatednowtime = datetime.datetime.fromtimestamp(now + period )
                currencyprice = CryptoPrice(SYMBOL, exchange)
                content = f"{formatednowtime: %Y-%m-%d %H:%M:%S} Price: {currencyprice}$\n"
                
                with open(FileName + ".txt", "a") as f:
                    f.write(content)
            logging.debug(f"One price imported in file {FileName} and one price imported in database {DATABASE}")

        else:
            print("Wrong input!")
            logging.error("Wrong input entered in section how to save report")




if __name__ == "__main__":
    while True:
        choice = input("""\nWelcome to my little application all about diffrent actions on cryptocurrencies.
        For getting a cryptocurrency's price enter '1'
        For getting a cryptocurrency's price for in a defined seconds enter '2'
        For getting a cryptocurrency worth of another cryptocurrency enter '3'
        For Signing a cryptocurrency price history in a file enter '4'
        For Signing a exchange info in a database enter '5'
        And for quitting please enter 'q':  """)    
    
        if choice == "q":
            break
        elif choice == "1":
            SYMBOL = input("Please enter the symbol of currency (Example: BTCUSDT -- BTCIRT -- ETHIRT -- ETHUSDT): ").upper()    
            exchange = input(f"Please enter the exchange you want to get price of {SYMBOL} from(Nobitex & KuCoin are available): ").upper()
            CryptoPrice(SYMBOL,exchange)
    
        elif choice == "2":
            try:
                
                SYMBOL = input("Please enter the symbol of currency you want to get price of (Example: BTCUSDT -- BTCIRT -- ETHIRT -- ETHUSDT): ").upper()
                exchange = input(f"Please enter the exchange you want to get price of {SYMBOL} from(Nobitex & KuCoin are available): ").upper()
                seconds = int(input(f"Please enter the time in seconds which you want to continously get price of {SYMBOL}"))

            except ValueError:
                print("Please enter only numbers!")
            
            else:
                DefinedTimeCryptoPrice(seconds, SYMBOL, exchange)


        elif choice == "3":
            SYMBOL = input("Please enter the symbol of currency you want to get price of (Example: BTCUSDT -- BTCIRT -- ETHIRT -- ETHUSDT): ").upper()
            SYMBOL2 = input("Please enter the symbol of the second currency you want to get price of (Example: BTCUSDT -- BTCIRT -- ETHIRT -- ETHUSDT): ").upper()
            exchange = input(f"Please enter the exchange you want to get price of {SYMBOL} & {SYMBOL2} from(Nobitex & KuCoin are available): ").upper()
            CurrencyByCurrency(SYMBOL, SYMBOL2, exchange)    
        
        elif choice == "4":
            SYMBOL = input("Please enter the symbol of currency you want to get price of (Example: BTCUSDT -- BTCIRT -- ETHIRT -- ETHUSDT): ").upper()
            exchange = input(f"Please enter the exchange you want to get price of {SYMBOL} from(Nobitex & KuCoin are available): ").upper()
            GetCryptoHistoryFunc(SYMBOL, exchange)

        elif choice == "5":
            try:
                exchange = input("Please enter the exchange you want their database to be seen in your mysql(Nobitex & KuCoin are available): ").upper()
                create_n_drop()
                ct_EXCHANGE()
                exchange_reserve = int(input("Please enter the exchange reserve amount in dollar: "))
                exusers = int(input("Please enter the users this exchange contains in number: "))
            except ValueError:
                print("Please enter only numbers!")
            else:
                insert_EXCHANGE_data(name= exchange, exchange_reserve = exchange_reserve, users = exusers)
                print(f"Exchange {exchange} inserted successfully")
                choice = input(f"Do you want to add any information to the exchange {exchange}? y/n")
                if choice == "y":

                    SYMBOL = input(f"Please enter the currency name you want to add to the exchange {exchange}: ").upper()
                    insert_CURRENCY_PRICE_data(SYMBOL, exchange)
                    

                elif choice == "n":
                    print("Returning you to the mainpage...")