# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 19:48:29 2021

@author: Meebo
"""

def wait_for_acknowledge(client,response):
    """
    Waiting for this response to be sent from the other party
    """
    amount_received = 0
    amount_expected = len(response)
    
    msg = str()
    while amount_received < amount_expected:
        data = client.recv(1024)
        amount_received += len(data)
        msg += data.decode("utf-8")
        #print(msg)
    return msg