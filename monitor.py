# -*- coding: utf-8 -*-
from Tkinter import *
import Tkinter as tk
import threading
import tkFont
from PIL import ImageTk
import RPi.GPIO as GPIO
import time
import sys
import Adafruit_DHT
import datetime
import os
import boto3
channel =21
sensor=23
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
GPIO.setup(sensor, GPIO.IN)
class MyDb(object):

    def __init__(self, Table_Name='AGRI'):
        self.Table_Name=Table_Name

        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table(Table_Name)

        self.client = boto3.client('dynamodb')

    @property
    def get(self):
        response = self.table.get_item(
            Key={
                'Sensor_Id':"1"
            }
        )

        return response

    def put(self, sensor_id='' , Temperature='', Humidity='',Moisture=0,Intrusion=0):
        self.table.put_item(
            Item={
                'sensor_id':sensor_id,
                'Temperature':Temperature,
                'Humidity' :Humidity,
                'Moisture':Moisture,
                'Intrusion':Intrusion,
            }
        )

    def delete(self,Sensor_Id=''):
        self.table.delete_item(
            Key={
                'Sensor_Id': Sensor_Id
            }
        )

    def describe_table(self):
        response = self.client.describe_table(
            TableName='AGRI'
        )
        return response



root = tk.Tk()

image = PhotoImage(file="background.gif")

background=Label(root, image=image)
background.place(x=0,y=0,relwidth=1, relheight=1)

title = StringVar()
title.set("Agriculture Monitor")

titleLabel = Label(root, fg="white", background="#00dbde", textvariable=title, font=("Helvetica", 40,"bold"))
titleLabel.place(x=400, y=0)

temperature = StringVar()
temperature.set("----"+" °C")		

humidity = StringVar()
humidity.set("----"+" %")		

moisture = StringVar()
moisture.set("----")		

intrusion = StringVar()
intrusion.set("----")		

temperatureLabel = Label(root, fg="white", background="#00dbde", textvariable=temperature, font=("Helvetica", 40,"bold"))
temperatureLabel.place(x=150, y=100)

humidityLabel = Label(root, fg="white", background="#00dbde", textvariable=humidity, font=("Helvetica", 40,"bold"))
humidityLabel.place(x=150, y=200)

moistureLabel = Label(root, fg="white", background="#00dbde", textvariable=moisture, font=("Helvetica", 40,"bold"))
moistureLabel.place(x=150, y=300)

intrusionLabel = Label(root, fg="white", background="#00dbde", textvariable=intrusion, font=("Helvetica", 40,"bold"))
intrusionLabel.place(x=150, y=400) 

root.attributes("-fullscreen",True)
root.bind("<1>",exit)

def exit():
	root.quit()

def readSensor():
        file=open("counter.txt","r");
        if (file.mode == 'r'):
            counter=file.read()
	root.after(2000, readSensor)
	hum,temp = Adafruit_DHT.read_retry(11, 4)
	temperature.set("Temperature:"+str(temp)+" °C")	
	humidity.set("Humidity:"+str(hum)+"  %")
	if GPIO.input(channel)==False:
                intrusion.set("theres intrusion")
        else:
                intrusion.set("theres no intrusion")
        if GPIO.input(sensor)==True:
                moisture.set("watered")
        else:
                moisture.set("Please water")
        obj = MyDb()
        obj.put(sensor_id=str(3), Temperature=str(temp), Humidity=str(hum),Moisture=int(GPIO.input(sensor)),Intrusion=int(GPIO.input(channel)))
        c1=int(counter)
        c1=c1+1
        file=open("counter.txt","w");
        file.write(c1)
        print("Uploaded Sample on Cloud T:{},H{}".format(temp, hum))
root.after(2000, readSensor)
root.mainloop()
