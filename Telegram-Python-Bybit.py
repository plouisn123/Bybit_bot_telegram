import requests
import ccxt
import time

##Telegram_bot
exchange = ccxt.bybit({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_API_KEY'
})

bot_token = 'YOUR_BOT_TOKEN'
channel_id = '@YOUR_CHANEL'


##Take message from Telegram
last_update_id = 0
dico  = {}
while True:
    response = requests.get(f"https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates?offset={last_update_id+1}&allowed_updates=[\"channel_post\"]").json()
    updates = response["result"]
    for update in updates:
        if "channel_post" in update and "text" in update["channel_post"]:
            message = update["channel_post"]["text"]
            text = message
            last_update_id = update["update_id"]
        else:
            text = ''
        
        ##Extraction of data
        if "TEXT_CONDITION_TO_BE_SURE_THAT'S_A_ORDER" in text and exchange.fetch_balance()['USDT']['free'] > 10: #condition to deteminate values
            
            PE1 = 'ENTRY PRICE NUMBER 1' #float
            PE2 = 'ENTRY PRICE NUMBER 2' #float
            SL = 'STOP LOSS' #float
            TP = 'TAKE PROFIT' #float
            PAIRE = 'BTCUSDT' 
            leverage = '50' 
            
            
            #Entry Price
            last_price = exchange.fetch_ticker(symbol)['last'] # take the last price 
            nb_decimals = len(str(last_price)) - str(last_price).index('.') - 1 #find the number of decimals for the entry price
            index = str(last_price).find('.')
            if PE1 < last_price < PE2:
                if index == -1: #finding if the coin has decimals
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

            #Leverage
            lev_max = exchange.fetch_market_leverage_tiers(symbol)[0]['maxLeverage'] #Take the maximum leverage 
            if leverage > lev_max:
                leverage = lev_max
               
            print('Levier',levier)
            
            ##ORDERS
            if all(var in globals() for var in ['BorS', 'PE', 'close', 'TPs', 'SL', 'levier']):
                info_leviers=exchange.fetch_positions(symbol) #get informations on the pair
                #leviers
                if len(info_leviers) == 1:
                    levier_LS = info_leviers[0]['leverage']
                else:
                    levier_long = info_leviers[0]['leverage'] 
                    levier_short = info_leviers[1]['leverage'] 
                try: 
                    if levier_LS not in globals():
                        if levier != levier_LS:
                            exchange.set_leverage(symbol=symbol, leverage=levier)
                except: 
                    if BorS == 'Buy':
                        if levier != levier_long:
                            exchange.set_leverage(symbol=symbol, leverage=levier)
                    else:
                        if levier != levier_short:
                            exchange.set_leverage(symbol=symbol, leverage=levier)
                           
                #Quantity
                size = info_leviers[0]['info']['size'] #number of decimals for the trade size
                if "." in size:
                    decimals = size.split(".")[1]
                    nb_decimals = decimals.count("0")
                    quantity = round(100*levier/last_price,nb_decimals) #100 is the USDT quantity use from your wallet 
                    if quantity == 0:
                        quantity = 1/10**nb_decimals
                else:
                    quantity = round(100*levier/last_price) #100 is the USDT quantity use from your wallet
                print('Quantity',quantity)
                
                ## Ordres
                #Entry
                orderPE = exchange.create_limit_order(symbol=symbol, side=BorS, amount=quantity, price=PE)
    
                #TP
                orderTP = exchange.create_order(symbol=symbol, type='limit', side=close, amount=quantity, price=TPs[2])                    
                #SL
                if BorS == 'Buy':
                    orderSL = exchange.create_limit_order(symbol=symbol, side=close, amount=quantity, price=SL, params={'stopLossPrice': SL}) #Close long
                else:
                    orderSL = exchange.create_limit_buy_order(symbol=symbol, amount=quantity, price=SL, params = {'stopPrice': SL}) #Open long
        
                #stock orders id
                dico[symbol]=[]
                dico[symbol].append(orderPE['id']), dico[symbol].append(orderTP['id']), dico[symbol].append(orderSL['id'])

                time.sleep(5)
          
    ## Orders check
    order_book = exchange.fetch_derivatives_open_orders() #wainting orders
    if len(order_book) != 0:
        symb = []
        for i in range(len(order_book)):
            symb.append(order_book[i]['info']['symbol']) #name of pair from wainting orders

        # number of orders for one pair
        dico_actif = {}
        for item in symb:
            if item in dico_actif:
                dico_actif[item] += 1
            else:
                dico_actif[item] = 1
        liste_actif = list(dico_actif.items())
        #print(liste_actif)

        #take the pair of open trade
        trade_actif = exchange.fetch_derivatives_positions()
        paire_active = []
        if len(trade_actif) != 0:
            paire_active = []
            for i in range(len(trade_actif)):
                paire_active.append(trade_actif[i]['info']['symbol'])
        
        # close useless trades and remove pair from dico
        for i in range(len(dico)):
            if liste_actif[i][1] == 2: # check if the trade hasn't been closed or liquidated
                #take statut order
                fpe = exchange.fetch_order_status(id = dico[list(dico.keys())[i]][0], symbol=list(dico.keys())[i])
                ftp = exchange.fetch_order_status(id = dico[list(dico.keys())[i]][1], symbol=list(dico.keys())[i])
                fsl = exchange.fetch_order_status(id = dico[list(dico.keys())[i]][2], symbol=list(dico.keys())[i])
                #print('222',fpe, ftp, fsl)
                if list(dico.keys())[i] not in paire_active: #pair in the dico not in pair of open trade?
                    if fpe != 'open':
                        exchange.cancel_derivatives_order(id= dico[list(dico.keys())[i]][1], symbol=list(dico.keys())[i])
                        exchange.cancel_derivatives_order(id= dico[list(dico.keys())[i]][2], symbol=list(dico.keys())[i])
                        del dico[list(dico.keys())[i]]
                        print(dico)
                    elif ftp != 'open':
                        exchange.cancel_derivatives_order(id= dico[list(dico.keys())[i]][0], symbol=list(dico.keys())[i])
                        exchange.cancel_derivatives_order(id= dico[list(dico.keys())[i]][2], symbol=list(dico.keys())[i])
                        del dico[list(dico.keys())[i]]
                    elif fsl != 'open':
                        exchange.cancel_derivatives_order(id= dico[list(dico.keys())[i]][0], symbol=list(dico.keys())[i])
                        exchange.cancel_derivatives_order(id= dico[list(dico.keys())[i]][1], symbol=list(dico.keys())[i])
                        del dico[list(dico.keys())[i]]
                
            if liste_actif[i][1] == 1: # check if the trade hasn't been closed or liquidated 
                #quel ordre est fermé ? 
                fpe = exchange.fetch_order_status(id = dico[list(dico.keys())[i]][0], symbol=list(dico.keys())[i])
                ftp = exchange.fetch_order_status(id = dico[list(dico.keys())[i]][1], symbol=list(dico.keys())[i])
                fsl = exchange.fetch_order_status(id = dico[list(dico.keys())[i]][2], symbol=list(dico.keys())[i])
                #print('111',fpe, ftp, fsl)
                if (fpe == 'closed' or fpe == 'canceled') and (ftp == 'closed' or ftp =='canceled'):
                    exchange.cancel_derivatives_order(id= dico[list(dico.keys())[i]][2], symbol=list(dico.keys())[i])
                    del dico[list(dico.keys())[i]]
                elif (fsl == 'closed' or fsl == 'canceled') and (fpe == 'closed' or fpe =='canceled'):
                    exchange.cancel_derivatives_order(id= dico[list(dico.keys())[i]][1], symbol=list(dico.keys())[i])
                    del dico[list(dico.keys())[i]]
                elif (fsl == 'closed' or fsl == 'canceled') and (ftp == 'closed' or ftp =='canceled'):
                    exchange.cancel_derivatives_order(id= dico[list(dico.keys())[i]][0], symbol=list(dico.keys())[i])
                    del dico[list(dico.keys())[i]]
        time.sleep(4)
  



    

                
                


 


        
            
