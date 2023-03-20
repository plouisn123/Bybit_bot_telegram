import requests
import ccxt

exchange = ccxt.bybit({
    'apiKey': 'API_KEY',
    'secret': 'SECRET_API_KEY',
})

bot_token = 'BOT_TOKEN'
channel_id = '@CHANEL'
last_update_id = 0
dollar=float(50) #choose how many usdt from your wallet you want to trade

#Get new messages from Telegram Chanel
while True:
    response = requests.get(f"https://api.telegram.org/botBOT_TOKEN/getUpdates?offset={last_update_id+1}&allowed_updates=[\"channel_post\"]").json()
    updates = response["result"]
    for update in updates:
        message = updates[-1]["channel_post"]["text"]
        #message = update["channel_post"]["text"]
        last_update_id = update["update_id"] 
        text = message
        
        #extract data from brut order
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
                
            #Pair    
            start = text.find("")
            end = text.find("(", start)
            if start != -1 and end != -1:
                crypto = text[start+1:end-1]
                symbol = crypto+'USDT'
                print('Paire:',symbol)
                #print(type(symbol))
                #print(type(crypto))

            #Entry price number 1                 
            start = text.find("entré")
            end = text.find("-", start)
            if start != -1 and end != -1:
                PE11 = text[start+8:end]
                PE1 = float(PE11.replace(",", "."))
                #print('Entry Price 1:',PE1)

            #Enter Price number 2
            start = text.find("-")
            end = text.find(" ", start)
            if start != -1 and end != -1:
                PE22 = text[start+1:end-3]
                PE2 = float(PE22.replace(",", "."))
                #print('Entry Price 2:',PE2)
                #print(type(PE2))

            #Take Profit number 1   
            start = text.find("TP")
            end = text.find(" SL", start)
            if start != -1 and end != -1:
                TP = text[start+6:end-3]        
                TPs = TP.split("\n")
                TPs[1] = float(TPs[1].replace(",", "."))
                print('Take Profit:',TPs[1])
                #print(type(TPs[1]))

            #Stop Loss  
            start = text.find("SL")
            end = text.find("Chaque", start)
            if start != -1 and end != -1:
                SLL = text[start+5:end-2]
                SL = float(SLL.replace(",", "."))
                print('Stop Loss:',SL)
                #print(type(SL))
                
            #Set the arguments
            #Entry price
            last_price = exchange.fetch_ticker(symbol)['last']
            nb_decimals = len(str(last_price)) - str(last_price).index('.') - 1
            index = str(last_price).find('.')
            #print('last price: ',last_price)
            if PE1 < last_price < PE2:
                if index == -1: 
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
            
            lev_max = exchange.fetch_derivatives_market_leverage_tiers(symbol)[0]['maxLeverage'] #maximum leverage            
            if 0.1 < last_price < 100:
                if lev_max < 20:
                    levier = lev_max
                else:
                    levier = 20
            if last_price <= 0.1:
                if lev_max < 15:
                    levier = lev_max
                else:
                    levier = 15
            if 100 <= last_price < 500:
                if lev_max < 25:
                    levier = lev_max
                else:
                    levier = 25
            if last_price >= 500:
                if lev_max < 35:
                    levier = lev_max
                else:
                    levier = 35
            print('Levier',levier)

            #Place order
            if symbol is not None and BorS is not None and PE is not None and close is not None and TPs[1] is not None and SL is not None and levier is not None:
                info_leviers=exchange.fetch_positions(symbol) #get infos about the pair (actual leverage and minimal quantity)
                size = info_leviers[0]['info']['size']
                #Set Leverage 
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
                            
                #Quantity
                if "." in size:
                    decimals = size.split(".")[1]
                    nb_decimals = decimals.count("0")
                    quantity = round(dollar*levier/last_price,nb_decimals)
                    if quantity == 0:
                        quantity = 1/10**nb_decimals
                else:
                    quantity = round(dollar*levier/last_price)
                print('Quantity',quantity)
                
                #Orders
                exchange.create_order(symbol=symbol, type='Limit', side=BorS, amount=quantity, price=PE)            #Entry
                exchange.create_order(symbol=symbol, type='Limit', side=close, amount=quantity, price=TPs[1])       #TP 
                if BorS == 'Buy':
                    exchange.create_limit_order(symbol=symbol, side=close, amount=quantity, price=SL, params={'stopLossPrice': SL}) #SL close long
                else:
                    exchange.create_limit_buy_order(symbol=symbol, amount=quantity, price=SL, params = {'stopPrice': SL}) #SL (short)
                    
#Problem 1: if liquidation price > stop loss -> stop loss order become short order
#Problem 2: if take profit is hit, stop loss not desactivate -> short order

        
               
        
