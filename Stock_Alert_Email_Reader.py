#!/usr/bin/env python
#in_file = open('out.txt','rt')
import re
import os
from os import listdir
from os.path import isfile, join

##Function to find if buying or selling stocks
##TO DO: PUT IN SINGLE VECTOR WITH 2 Columns so we don't need to duplicat
##TO DO: MAY NEED TO ADD MULTIPLE TICKERS IN ticker string
def buy_or_sell(lines,action):
    #action = [] #array = buy or sell, ticker, number of stocks, price
    #ticker = "" #ticker name TO DO:MIGHT NEED TO BE PUT DOWN THERE
    buy = ['Buy', 'BUY', 'buy', 'Bought', 'BOUGHT', 'bought', 'In', 'IN', 'in']
    sell = ['sell', 'Sell', 'SELL', 'Out', 'OUT', 'out', 'Sold', 'SOLD']

    str = lines
    print(str)
    
    for cond in buy: #check if we are buying
        index = 0    #location of letter
        
        while index<len(str): #keep checking until we reach the end of text
            index = str.find(cond, index)   #finds location of key word
            
            if index == -1: #if we don't find a key word we get out
                break
            else:
                num = re.findall(r'[-+]?\d+[\.]?\d*[eE]?[-+]?\d*', str)
                price = num[0]
                if lines[index+len(cond)+1] == price: #TO DO: Might need to harden this
                    action[1][0] = (cond)
                    action[0][0] = 'Buy'
                    return action
                    break #TO DO:MAY NEED TO ADD MORE TICKERS to string incase there are multiple buys
                else:
                    index += len(cond)

    for cond in sell: #Check if we are selling
        index = 0

        while index<len(str):
            index = str.find(cond, index)
            if index == -1:
                break
            else:            
                if lines[index+len(cond)+1].isupper() == 1:
                    action[0][0] = ("Sell")
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

    if action[0][0] == 'Buy': #TO DO: Need a better way
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
    #is it after the buy/sell word?
    #is it after the number of stock information?
    #is it after the price of the stock?
    #Find a ticker by comparing to dictionnary
    #Use a probabilistic approach afterwards

    return action


##Function to find how many stocks to buy and sell
def stock_quant(lines,action):
    if action[0][0] == "Sell": #find if its buying or selling
        action[0][2]("All")
        return action
    elif action[0][0] == "Buy":
        num = re.findall(r'[-+]?\d+[\.]?\d*[eE]?[-+]?\d*', lines)
        quant = str(num[0])
        action[0][2] = quant#TO DO: Need to differetiate from below
        action[1][2] = quant
    else:
        print("Error, there is no Buy or Sell order.")
    return action
    
##Function to find at what price to buy the stock
def stock_price(lines,action):
    str1 = lines
    num = re.findall(r'[-+]?\d+[\.]?\d*[eE]?[-+]?\d*', str1)

    price = str(num[1])##TO DO: Need to multiple number by 1000 if k is found at the end
    action[0][3] = (price)
    action[1][3] = (price)
    return action

def file_creator(action):
    onlyfiles = [f for f in listdir('/home/mike/Python/Automated_Trader/Trade_Request/') if isfile(join('/home/mike/Python/Automated_Trader/Trade_Request/', f))]
    onlyfiles.sort()
    version = 1;
    filename = 'Trade_Alert1.txt' ##TO DO: WILL NEED TO BE UPDATED

    while True:
        for name in onlyfiles:
            if name == filename:
                version += 1

                filename = list(filename)
                filename[-5] = '%d'%version
                filename = "".join(filename)

        with open(os.path.join('/home/mike/Python/Automated_Trader/Trade_Request/', filename), 'w') as file1:
            #file1.write(str(action))
            for item in action[0]:
                file1.write("%s\n" %item)
            file1.close()
        break

def file_opener():
    lines =[]
    onlyfiles = [f for f in listdir('/home/mike/Python/Automated_Trader/Recieved_Email/') if isfile(join('/home/mike/Python/Automated_Trader/Recieved_Email/', f))]
    onlyfiles.sort(reverse = True)
    print(onlyfiles)
    
    with open('/home/mike/Python/Automated_Trader/Recieved_Email/Email_Trade_Alert1.txt','rt') as in_file:   #Open to read text file
        for line in in_file:                #Save text to array line by line
            lines.append(line.rstrip('='))  #TO DO: what does rstrip() really do?
    return lines

##Main function
def main(argv=None):
    lines = []
    #action = [[],[]]#
    action = [[0 for x in range(4)] for y in range(2)]

    lines = file_opener()

    action = buy_or_sell(lines[0],action) #Call function to find if we are buying or selling
    action = find_ticker(lines[0],action)
    action = stock_price(lines[0],action)
    action = stock_quant(lines[0],action)

    file_creator(action)

    print (action)

##Start of program
main()
