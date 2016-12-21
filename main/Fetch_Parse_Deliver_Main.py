#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Retrieve Email from GMAL
import getpass, os, imaplib, email, string
from OpenSSL.crypto import load_certificate, FILETYPE_PEM
import itertools
from os import listdir
from os.path import isfile, join
######################

import imaplib, getpass, re
from time import sleep
import sys
pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')

######################
# ib_api_demo.py
from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order
import test

order_id = 1
conn = imaplib.IMAP4_SSL('imap.gmail.com')

##################  Retrieve Email Functions  #########################
#######################################################################

def disconnect(imap):
    imap.logout()

def parse_uid(data):
    match = pattern_uid.match(data)
    return match.group('uid')

def move_email(email_ids):
    latest_email_id = email_ids[-1] # Assuming that you are moving the latest email.
    resp, data = conn.fetch(latest_email_id, "(UID)")
    print "-----REMOVING EMAIL-----: \n  Email # REMOVED: ", resp, data
    msg_uid = parse_uid(data[0])
    result = conn.uid('COPY', msg_uid, 'Stocks')#To be modified so emails are moved correctly
    sleep(2)
    if result[0] == 'OK':
        mov, data = conn.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
        conn.expunge()

def get_payload(data,lines):
    global conn
    typ, data = conn.fetch(data[-1],'(RFC822)')
    print "\n -----NEXT EMAIL-----: \n New Email Found: ", data[0][0]
    msg = email.message_from_string(data[0][1])
    lines = msg.get_payload()
    print(lines)
    return lines #this should be the text from the email

##################  Determine Buy/Sell Orders  #########################
########################################################################

def buy_or_sell(lines, action):
    buy = ['Buy', 'BUY', 'buy', 'Bought', 'BOUGHT', 'bought', 'In', 'IN', 'in', 'ADDED', 'Added', 'added']
    sell = ['sell', 'Sell', 'SELL', 'Out', 'OUT', 'out', 'Sold', 'SOLD']
    lines = lines.split('\n')
    #print(lines[0])

#######
    for line in lines:
        str = line
        words=str.split()
        print "The following is inside the email: ", words
        counter_sell_words = 0
        counter_buy_words = 0

        key_words = []
        counter = 0
        for word in words:
            for list_sell in sell:
                if list_sell == word:
                    key_words.append(counter)

            counter += 1
        if len(key_words) != 0:
            print("New algorithm: ", key_words) 
#######
    str = lines[0]
    words=str.split()
    print "The following is inside the email: ", words
    counter_sell_words = 0
    counter_buy_words = 0

    for word in words:
        for list_buy in buy:

            if list_buy == word and bool(re.search(r'\d',words[counter_buy_words+1])) == True: #checks if there is a digit after keyword
                    action[0][0] = "BUY"
                    action[1][0] = word
                    return action
            elif list_buy == word and words[counter_buy_words+1] == 'another' and bool(re.search(r'\d',words[counter_buy_words+2])) == True:
                action[0][0] = "BUY"
                action[1][0] = word
                return action
                
        counter_buy_words +=1
        
    
    for word in words: #Check if we are selling
        for list_sell in sell:
            
            if list_sell == word and (words[counter_sell_words+1].isupper() == True or words[counter_sell_words+1] == 'all' or words[counter_sell_words+1] == 'my'):
                action[1][0] = word
                action[0][0] = ("SELL")
                action
                return action
                
        counter_sell_words += 1

def find_ticker(lines, action):
    all_stocks = ['all', 'ALL', 'All', 'Everything', 'everything', 'EVERYTHING']
    lines = lines.split('\n')
    
    str = lines[0]
    words=str.split()
    
    index = 0
    ticker = ''
    ticker_len = 0
    counter = 1;

    if action[0][0] == 'BUY': #TO DO: Need a better way
        index = str.find(action[1][0], index)
        
        if index == -1:
            print('Error: there is no buy order')

        while lines[0][index+len(action[1][0])+counter-1].isupper() != True:
            if lines[0][index+len(action[1][0])+counter].isupper() == True:
                while(lines[0][index+len(action[1][0])+counter+ticker_len] != " "):
                    ticker += lines[0][index+len(action[1][0])+counter+ticker_len]
                    ticker_len +=1
            counter += 1
        action[0][1] = (ticker)
        action[1][1] = (ticker)
    
    
    elif action[0][0] == 'SELL': #TO DO: Need a better way
        
        for word in all_stocks:
            for line in words:
                #print (word, "   ", line)
                if word == line:
                    action[0][1] = "ALL"
                    action[1][1] = "ALL"
                    return action
            
        index = str.find(action[1][0], index) #Looks for the sell word used in original email
        if index == -1: 
            print('Error: there is no buy order')
        while lines[0][index+len(action)+counter-1].isupper() != 1:
            if lines[0][index+len(action)+counter].isupper() == 1:
                while(lines[0][index+len(action)+counter+ticker_len] != " "):
                    ticker += lines[0][index+len(action)+counter+ticker_len]
                    ticker_len +=1
            counter += 1
        action[0][1] = (ticker)
        action[1][1] = (ticker)

    else:
        print("Houston,we have a problem")
    #is it after the buy/sell word?
    #is it after the number of stock information?
    #is it after the price of the stock?
    #Find a ticker by comparing to dictionnary
    #Use a probabilistic approach afterwards
    return action

def stock_price(lines,action):
    #print("HERE")
    lines = lines.split('\n')
    str = lines[0]
    words=str.split()
    price = [] #will store the price value if =A0 is found in email
    word_counter = 0
    
    for word in words:#Should write an algorithm that takes into account the realtime data
        #print(words[word_counter+1])
        if action[0][1] == "ALL":
            action[0][3] = "ALL"
            action[1][3] = "ALL"
            return action
        
        elif word == action[0][1] and (words[word_counter+1] == 'here' or words[word_counter+1] == 'for'):
            print("YESS WE ARE")
            if words[word_counter+2] == 'at' and bool(re.search(r'\d',words[word_counter+3])) == True:
                if bool(re.search(r'=', words[word_counter+3])) == True:
                    
                    counter = 0
                    sep_word = words[word_counter+3]

                    while(sep_word[counter] != '='):                       
                        price.append(sep_word[counter]) #Divide string in to matrix
                        counter += 1
                        
                    action[0][3] = ''.join(price) #Put array into string form
                    action[1][3] = ''.join(price)
                    return action
                
                else:
                    action[0][3] = words[word_counter+3]
                    action[1][3] = words[word_counter+3]
                    return action
                
            elif words[word_counter+2] == 'a' and bool(re.search(r'\d',words[word_counter+3])) == True:
                action[0][3] = "ALL"
                action[1][3] = "ALL"
                return action
            
            else:
                action[0][3] = "ALL"
                action[1][3] = "ALL"
                return action
        elif word == action[0][1] and words[word_counter+1] == 'here.':
            action[0][3] = "MARKET PRICE"
            action[1][3] = "MARKET PRICE"
            return action
        
        elif word == 'at':##TO DO: Need to multiple number by 1000 if k is found at the end
            if bool(re.search(r'=', words[word_counter+1])) == True:
                counter = 0
                sep_word = words[word_counter+1]

                while(sep_word[counter] != '='):
                    price.append(sep_word[counter]) #Divide string in to matrix
                    counter += 1
                    
                action[0][3] = ''.join(price) #Put array into string form
                action[1][3] = ''.join(price)
                return action
            else:
                action[0][3] = (words[word_counter+1])
                action[1][3] = (words[word_counter+1])
                print("THE RESULT: ", action)
                return action
        word_counter += 1                

def stock_quant(lines,action):
    lines = lines.split('\n')
    str = lines[0]
    words=str.split()
    counter =0
    quant = []
    
    if action[0][0] == "SELL" or action[0][1] == "ALL": #find if its buying or selling
        action[0][2] = ("ALL") #To DO: Look at previous email history to check the trades
        action[1][2] = ("ALL") 
        return action
    elif action[0][0] == "BUY":
        for word in words:
            if word == action[1][0]:

                if bool(re.search(r'k', words[counter+1])) == True:
                    counter_quant = 0
                    quant_sep = words[counter+1]
                                  
                    while quant_sep[counter_quant] != 'k':                      
                        quant.append(quant_sep[counter_quant])  
                        quant = ''.join(quant)
                        quant = int(quant)*1000
                        counter_quant += 1
                        
                    action[0][2] = quant#TO DO: Need to differetiate from below
                    action[1][2] = quant
                    return action

                elif words[counter+1] == 'another' and bool(re.search(r'k', words[counter+2])) == True:
                    counter_quant = 0
                    quant_sep = words[counter+2]
                                  
                    while quant_sep[counter_quant] != 'k':                      
                        quant.append(quant_sep[counter_quant])  
                        quant = ''.join(quant)
                        quant = int(quant)*1000
                        counter_quant += 1
                        
                    action[0][2] = quant#TO DO: Need to differetiate from below
                    action[1][2] = quant
                    return action
                
                action[0][2] = words[counter+1]
                action[1][2] = words[counter+1]
                    
            counter += 1
    else:
        print("Error, there is no Buy or Sell order.")
    return action

##################  Execute Buy/Sell Orders  #########################
######################################################################

def error_handler(msg):
    print "Server Error:", msg

def server_handler(msg):
    print "Server Msg:", msg.typeName, "-", msg

def create_contract(symbol, sec_type, exch, prim_exch, curr):
    Contract.m_symbol = symbol
    Contract.m_secType = sec_type
    Contract.m_exchange = exch
    Contract.m_primaryExch = prim_exch
    Contract.m_currency = curr
    return Contract

def create_order(order_type, quantity, action):
    order = Order()
    order.m_orderType = order_type
    order.m_totalQuantity = quantity
    order.m_action = action
    return order

def save_order_id(msg):
    global order_id
    order_id = msg.orderId
    print('Next Valid ID is ' + str(msg.orderId))


##################  Main Function  #########################
############################################################

def main():
    global conn
    #subject = 'A Friend'
    action = [[0 for x in range(4)] for y in range(2)] #Array to be passed to trade execution function
    lines = [] #Payload from email

    conn.login('michal.gnat@gmail.com', 'aqjejrhozjeimzzc')
    conn.select('Inbox', readonly = False)              
    
    while True:
        try:
            typ, data = conn.search(None,'(Subject "Trade Alert")') #gathers all the emails and presents them in numbers
            if typ == 'OK':
                email_ids = data[-1].split()
                lines = get_payload(email_ids, lines)
                print("\n -----Getting payload-----")
                #sleep(2)
                
                #need to extract info to have "lines" variable
                action = buy_or_sell(lines,action)
                #print(action)
                action = find_ticker(lines,action)
                #print(action)
                action = stock_price(lines,action)
                #print(action)
                action = stock_quant(lines,action)
                
                print"\n -----RESULT----- \n The calculated executions are: ", action
                sleep(10)

                #execfile('IB_Py_Execution.py')
                #test.main()
                counter_deletion = 0
                for list in action:
                    if list != 0 or list != '0':
                        counter_deletion += 1
                if counter_deletion >= 2:
                    print("EMAIL SHOULD BE DELETED")
                    sleep(5)
                    move_email(email_ids)###NEED A RULE IF THERE ARE ERRORS
                else:
                    print("Error in execution")
                sleep(3)#If I take this off then sometimes it doesn't work
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            sleep(2)
            print("No more emails")
            pass
main()
##TO DO: Additional info on how much the gain is 
