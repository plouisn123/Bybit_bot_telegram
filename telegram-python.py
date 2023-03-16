import requests

bot_token = '6090463556:AAHofa_7MVtGilhwy2_4SlDuMT9WAtwhNdI'
channel_id = '@eeererrerererr'

last_update_id = 0

#Récupère le message dans le canal télégram
while True:
    response = requests.get(f"https://api.telegram.org/bot6090463556:AAHofa_7MVtGilhwy2_4SlDuMT9WAtwhNdI/getUpdates?offset={last_update_id+1}&allowed_updates=[\"channel_post\"]").json()
    updates = response["result"]
    for update in updates:
        message = update["channel_post"] ["text"]
        last_update_id = update["update_id"]
        
#Extraction et traitement des données
        text = message

        #LONG or SHORT
        start = text.find("(")
        end = text.find(")", start)
        if start != -1 and end != -1:
            L_S = text[start+1:end]          
            print('buy or sell:',L_S)
            
        #crypto    
        start = text.find(" ")
        end = text.find("(", start)
        if start != -1 and end != -1:
            crypto = text[start-3:end-1]
            print('pair:',crypto)     

        #Prix entrée n°1    
        start = text.find("entré")
        end = text.find("-", start)
        if start != -1 and end != -1:
            PE1 = text[start+8:end]          
            print('Prix Entrée 1:',PE1)

        #Prix d'entrée n°2  
        start = text.find("-")
        end = text.find(" ", start)
        if start != -1 and end != -1:
            PE2 = text[start+1:end-3]        
            print('Prix Entrée 2:',PE2)

        #TP n°i    
        start = text.find("TP")
        end = text.find(" SL", start)
        if start != -1 and end != -1:
            TP = text[start+6:end-3]        
            TPs = TP.split("\n")
            print('Take Profit n°6:',TPs[6]) 

        #SL    
        start = text.find("SL")
        end = text.find("Chaque", start)
        if start != -1 and end != -1:
            SL = text[start+5:end-2]         
            print('StopLoss:',SL)
        
            
        
            
        
