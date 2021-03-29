# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 19:46:49 2021

@author: Meebo
"""

import socket
from utility import wait_for_acknowledge
import PIL
import skimage.transform
import numpy as np
import imageio
import tensorflow as tf
from tensorflow.keras.models import load_model, save_model, Model



def preprocess(img, size=(150, 101, 3)):
    img = skimage.transform.resize(img, size)
    img = img.astype(np.float32)
    img = (img / 127.5) - 1.
    return img


#initiate connection
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_addr = (socket.gethostname(), 2019)  #change here for sending to another machine in LAN

client.connect(server_addr)
print(f"Connected to server!")

client.settimeout(5) #limit each communication time to 5s
######################################
movie = input('Enter a movie title:')
client.send(bytes(movie, 'utf-8'))
######################################
#listening to server command
print("Client is now waiting for server's command.")
cmd_from_server = wait_for_acknowledge(client,"Start sending image.")

#send an ACK
imgCount_from_server = 0
if cmd_from_server == "Start sending image.":
    print("Command \"Start sending image.\" received.")
    print("Sending ACK...")
    client.sendall(bytes("ACK","utf-8"))
    try:
        print("Client is now waiting for the number of images.")
        imgCount_from_server = int(wait_for_acknowledge(client,str(3)))

    except:
        raise ValueError("Number of images received is buggy.")

if imgCount_from_server > 0:
    print("Number of images to receive: ",imgCount_from_server)
    print("Sending ACK...")
    client.sendall(bytes("ACK","utf-8"))

print(f"Client is now receiving {imgCount_from_server} images.")



for i in range(imgCount_from_server):
    index = i+1
    file = f"./imgfromserver{index}.jpg"
    img = PIL.Image.open(file)
    img = np.asarray(img)
    #img.show()
    # transform to resize image

    # add one more none dimension to fit tensor shape
    img = preprocess(img)
    print(img.shape)

    img = img[np.newaxis is None, :, :, :]

    # Add dimension using np.newaxis
    print(img.shape)

    # model
    model = tf.keras.models.load_model('rating_model')
    print(model.summary())
    pred = model.predict(img)
    indx = np.argmax(pred)

    dict = ['PG-13', 'PG', 'G', 'R', 'Not Rated', 'Unrated', 'Approved']

    print('Max index of the prediction', indx)

    print('Genre', dict[indx])


    try:                                            #check for existing file, will overwrite
        f = open(file, "x")
        f.close()
    except:
        pass
    finally:
        f = open(file, "wb")
    print(f"\tReceiving image {index}")
    imgsize = int(wait_for_acknowledge(client,str(3)))
    print(f"\tImage size of {imgsize}B received by Client")
    print("Sending ACK...")
    client.sendall(bytes("ACK","utf-8"))
    buff = client.recv(imgsize)
    f.write(buff)
    f.close()
    print(f"File {file} received!")
    print("Sending ACK...")
    client.sendall(bytes("ACK","utf-8"))
    #a = wait_for_acknowledge(client,"This is done.")

print("All images received.")
print("Closing connection.")
#img = PIL.Image.open("imgfromserver1.jpg")
#img.show()
client.close()