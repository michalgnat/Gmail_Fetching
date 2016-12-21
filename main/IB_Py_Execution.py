#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order
from time import sleep
order_id = 1

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
if __name__ == "__main__":
#def main():
    client_id = 200
    #global order_id
    port = 7496
    tws_conn = None

    tws_conn = Connection.create(port=port, clientId=client_id)
    tws_conn.register(save_order_id, 'NextValidId')
    tws_conn.connect()
    sleep(2)
    print("HERE: ", order_id)

    tws_conn.register(error_handler, 'Error')
    tws_conn.registerAll(server_handler)

    aapl_contract = create_contract('AAPL','STK','SMART','SMART','USD')
    aapl_order = create_order('MKT', 100, 'SELL')
    print("About to place order")
    sleep(1)
    tws_conn.placeOrder(order_id, aapl_contract, aapl_order)
    #print("---------Connection is: ", tws_conn.connect())
    if tws_conn is not None:
        tws_conn.disconnect()
