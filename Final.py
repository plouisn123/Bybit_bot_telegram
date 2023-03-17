import requests
import ccxt

exchange = ccxt.bybit({
    'apiKey': '6Z1bOetRqDSjvKUI5G',
    'secret': 'hLWFjqtpYquGwJBmVL8Zh8NlWxbE2UjqhLbn',
})

bot_token = '5704355843:AAHk0C4706h3Kn3X8KvF0ZQah-DmkqSB6o4'
channel_id = '@ceinturionskatana'

last_update_id = 0

#Récupère le message dans le canal télégram

while True:
    response = requests.get(f"https://api.telegram.org/bot5704355843:AAHk0C4706h3Kn3X8KvF0ZQah-DmkqSB6o4/getUpdates?offset={last_update_id+1}&allowed_updates=[\"channel_post\"]").json()
    updates = response["result"]
    for update in updates:
        message = update["channel_post"]["text"]
        #message = update["channel_post"]["text"]
        last_update_id = update["update_id"] 
        
        #Extraction et traitement des données
        text = message
        
        print(text)
        
        if "TP :" in text and "SL :" in text and "Prix" in text:
            
            #LONG or SHORT
            start = text.find("(")
            end = text.find(")", start)
            if start != -1 and end != -1:
                L_S = text[start+1:end]
                BorS = 'Buy' if L_S == 'LONG' else 'Sell'
                close = 'Buy' if BorS == 'Sell' else 'Sell'
                print('Side:',BorS)
                #print(type(BorS))
                #print(type(close))
                
            #Paire    
            start = text.find(" ")
            end = text.find("(", start)
            if start != -1 and end != -1:
                crypto = text[start-3:end-1]
                symbol = crypto+'USDT'
                print('Paire:',symbol)
                #print(type(symbol))
                #print(type(crypto))

            #Prix entrée n°1    
            start = text.find("entré")
            end = text.find("-", start)
            if start != -1 and end != -1:
                PE11 = text[start+8:end]
                PE1 = float(PE11.replace(",", "."))
                #print('Prix Entrée 1:',PE1)

            #Prix d'entrée n°2  
            start = text.find("-")
            end = text.find(" ", start)
            if start != -1 and end != -1:
                PE22 = text[start+1:end-3]
                PE2 = float(PE22.replace(",", "."))
                #print('Prix Entrée 2:',PE2)
                #print(type(PE2))

            #TP n°i    
            start = text.find("TP")
            end = text.find(" SL", start)
            if start != -1 and end != -1:
                TP = text[start+6:end-3]        
                TPs = TP.split("\n")
                TPs[1] = float(TPs[1].replace(",", "."))
                print('Take Profit:',TPs[1])
                #print(type(TPs[1]))

            #SL    
            start = text.find("SL")
            end = text.find("Chaque", start)
            if start != -1 and end != -1:
                SLL = text[start+5:end-2]
                SL = float(SLL.replace(",", "."))
                print('StopLoss:',SL)
                #print(type(SL))
                
            #Prix d'entrée
            ticker = exchange.fetch_ticker(symbol)
            last_price = ticker['last']
            nb_decimals = len(str(last_price)) - str(last_price).index('.') - 1
            index = str(last_price).find('.')
            #print('last price: ',last_price)
            if PE1 < last_price < PE2:
                if index == -1: #est ce que le prix de la crypto à une virgule ?
                    PE = round(last_price*1.001)
                    print('PE:',PE)
                else:
                    nb_decimals = len(str(last_price)) - index - 1 
                    PE = round(last_price*1.001,nb_decimals)
                    print('PE:',PE)
                    
            if last_price > PE2:
                PE = PE2
                print('PE:',PE)
            if last_price < PE1:
                PE = PE1
                print('PE:',PE)

            #choix levier
            ticker = exchange.fetch_ticker(symbol)
            last_price = ticker['last']
            
            if 0.1 < last_price < 100:
                levier = 20
            if last_price <= 0.1:
                levier = 15
            if 100 <= last_price < 500:
                levier = 25
            if last_price >= 500:
                levier = 35
            print('Levier',levier)

            #Passage des ordres
            if symbol is not None and BorS is not None and PE is not None and close is not None and TPs[1] is not None and SL is not None and levier is not None:
                info_leviers=exchange.fetch_positions(symbol)#récupère le gros tas d'info sur la paire
                size = info_leviers[0]['info']['size']
                #leviers
                if len(info_leviers) == 1:
                    levier_LS = info_leviers[0]['leverage']
                else:
                    levier_long = info_leviers[0]['leverage']
                    levier_short = info_leviers[1]['leverage']
                if levier_LS is not None:
                    if levier != levier_LS:
                        exchange.set_leverage(symbol=symbol, leverage=levier)
                else:
                    if BorS == 'Buy':
                        if levier != levier_long:
                            exchange.set_leverage(symbol=symbol, leverage=levier)
                    else:
                        if levier != levier_short:
                            exchange.set_leverage(symbol=symbol, leverage=levier)
                            
                #calcul quantity
                if "." in size:
                    decimals = size.split(".")[1]
                    nb_decimals = decimals.count("0")
                    ticker = exchange.fetch_ticker(symbol)
                    last_price = ticker['last']
                    quantity = round(1*levier/last_price,nb_decimals)
                    if quantity == 0:
                        quantity = 1/10**nb_decimals
                else:
                    quantity = round(1*levier/last_price)
                print('Quantity',quantity)
                
                #ordres
                exchange.create_order(symbol=symbol, type='Limit', side=BorS, amount=quantity, price=PE)            #Entry
                exchange.create_order(symbol=symbol, type='Limit', side=close, amount=quantity, price=TPs[1])       #TP 
                if BorS == 'Buy':
                    exchange.create_stop_limit_order(symbol=symbol,side=close, amount=quantity, price=SL, stopPrice=SL)   #SL (long)
                else:
                    exchange.create_limit_buy_order(symbol=symbol, amount=quantity, price=SL, params = {'stopPrice': SL}) #SL (short)
                    
 
#si liquidation avant SL, SL considéré comme un short

        
               
        
