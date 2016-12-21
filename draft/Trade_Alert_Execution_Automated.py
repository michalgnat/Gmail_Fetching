#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Retrieve Email from GMAL
import getpass, os, imaplib, email
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
    print("All the emails found: ", email_ids)
    latest_email_id = email_ids[-1] # Assuming that you are moving the latest email.
    resp, data = conn.fetch(latest_email_id, "(UID)")
    print("Found email: ", resp, data)
    msg_uid = parse_uid(data[0])
    result = conn.uid('COPY', msg_uid, 'Stocks')#To be modified so emails are moved correctly
    sleep(2)
    if result[0] == 'OK':
        mov, data = conn.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
        conn.expunge()

def get_payload(data,lines):
    global conn
    typ, data = conn.fetch(data[-1],'(RFC822)')
    msg = email.message_from_string(data[0][1])
    lines = msg.get_payload()
    return lines #this should be the text from the email

##################  Determine Buy/Sell Orders  #########################
########################################################################

def buy_or_sell(lines, action):
    buy = ['Buy', 'BUY', 'buy', 'Bought', 'BOUGHT', 'bought', 'In', 'IN', 'in']
    sell = ['sell', 'Sell', 'SELL', 'Out', 'OUT', 'out', 'Sold', 'SOLD']

    str = lines
    print("This is what we are printing: ", str)
    
    for cond in buy: #check if we are buying
        index = 0    #location of letter
        
        while index<len(str): #keep checking until we reach the end of text
            index = str.find(cond, index)   #finds location of key word
            
            if index == -1: #if we don't find a key word we get out
                break
            else:
                print("YOu found it: ", cond)
                num = re.findall(r'[-+]?\d+[\.]?\d*[eE]?[-+]?\d*', str)
                price = num[0]
                if lines[index+len(cond)+1] == price: #TO DO: Might need to harden this
                    action[1][0] = (cond)
                    action[0][0] = 'BUY'
                    return action
                    break #TO DO:MAY NEED TO ADD MORE TICKERS to string incase there are multiple buys
                else:
                    index += len(cond)
    print("This is the problem: ", action)
    for cond in sell: #Check if we are selling
        index = 0

        while index<len(str):
            index = str.find(cond, index)
            if index == -1:
                break
            else:            
                if lines[index+len(cond)+1].isupper() == 1:
                    action[1][0] = (cond)
                    action[0][0] = ("SELL")
                    return action
                    break
                else:
                    index += len(cond)########TO DO, not very redudant!

def find_ticker(lines, action):
    index = 0
    str = lines
    ticker = ''
    ticker_len = 0
    counter = 1;
    print(action)

    if action[0][0] == 'BUY': #TO DO: Need a better way
        index = str.find(action[1][0], index)
        if index == -1:
            print('Error: there is no buy order')
        while lines[index+len(action)+counter-1].isupper() != 1:
            if lines[index+len(action)+counter].isupper() == 1:
                while(lines[index+len(action)+counter+ticker_len] != " "):
                    ticker += lines[index+len(action)+counter+ticker_len]
                    ticker_len +=1
            counter += 1
        action[0][1] = (ticker)
        action[1][1] = (ticker)
    #print("here")
    if action[0][0] == 'SELL': #TO DO: Need a better way
        index = str.find(action[1][0], index) #Looks for the sell word used in original email
        if index == -1:
            print('Error: there is no buy order')
        while lines[index+len(action)+counter-1].isupper() != 1:
            if lines[index+len(action)+counter].isupper() == 1:
                while(lines[index+len(action)+counter+ticker_len] != " "):
                    ticker += lines[index+len(action)+counter+ticker_len]
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
    str1 = lines
    num = re.findall(r'[-+]?\d+[\.]?\d*[eE]?[-+]?\d*', str1)

    price = str(num[0])##TO DO: Need to multiple number by 1000 if k is found at the end
    action[0][3] = (price)
    action[1][3] = (price)
    return action

def stock_quant(lines,action):
    if action[0][0] == "SELL": #find if its buying or selling
        action[0][2] = ("All") #To DO: Look at previous email history to check the trades
        #action[1][2] = ("NEED TO WRITE A SCRIPT TO FIGURE OUT HOW MUCH IS HERE")
        return action
    elif action[0][0] == "BUY":
        num = re.findall(r'[-+]?\d+[\.]?\d*[eE]?[-+]?\d*', lines)
        quant = str(num[0])
        action[0][2] = quant#TO DO: Need to differetiate from below
        action[1][2] = quant
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

    conn.login()
    conn.select('Inbox', readonly = False)              
    
    while True:
        try:
            typ, data = conn.search(None,'(Subject "Trade Alert")') #gathers all the emails and presents them in numbers
            if typ == 'OK':
                email_ids = data[-1].split()
                lines = get_payload(email_ids, lines)
                print("1. Getting payload")
                #sleep(2)
                
                #need to extract info to have "lines" variable
                action = buy_or_sell(lines,action)
                action = find_ticker(lines,action)
                action = stock_price(lines,action)
                action = stock_quant(lines,action)
                print(action)

                #execfile('IB_Py_Execution.py')
                #test.main()
                
                move_email(email_ids)
                sleep(3)#If I take this off then sometimes it doesn't work
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            sleep(2)
            print("No more emails")
            pass
main()
