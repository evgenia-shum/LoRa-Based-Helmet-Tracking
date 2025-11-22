import customtkinter
from tkintermapview import TkinterMapView
import picket
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import scrolledtext
from tkinter import filedialog
import serial.tools.list_ports
from serial import Serial
import threading
import time
from time import strftime
import datetime
from openpyxl import Workbook
from typing import List
import os
from PIL import Image, ImageTk

customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):

    APP_NAME = "Smart Helmet"
    BACK_COLOR = 'EBEBEB'
    FONT = 'Bahnschrift SemiLight'
    SIZE_FONT = 14
    WIDTH = 900
    HEIGHT = 600
    BG_COLOR = '#37474f'
    FG_COLOR = 'white'
    COLOR_H = '#00897b'
    COLOR_M = '#4A8FE7'
    COLOR_S = '#8e24aa'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(App.APP_NAME)
        #self['background'] = App.BACK_COLOR
        #self.font = ('{App.FONT}', App.SIZE_FONT)
        #self.font = customtkinter.CTkFont(family='{App.FONT}', size=App.SIZE_FONT)

        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)
        self.resizable(True, True)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)
        
        self.marker_list = []
        self.Big_buf = []
        self.input = []
        self.result1 = 0
        self.result2 = 0
        self.prevlat = 0
        self.but = 0 
        self.lat = 0
        self.lng = 0
        self.alt = 0
        self.id_record:int = 1
        self.ax = 0
        self.ay= 0
        self.az = 0
        self.gx = 0
        self.gy = 0
        self.gz = 0
        self.ff = 0
        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(self, width=150, corner_radius=0, fg_color=App.BG_COLOR)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(self, corner_radius=0,fg_color=App.BG_COLOR)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(2, weight=1)

        self.port_combobox_label = customtkinter.CTkLabel(self.frame_left, 
                                                          text="Select Port:", anchor="w", 
                                                          font=('Bahnschrift SemiLight', 18), 
                                                          text_color='white')
        self.port_combobox_label.grid(row=0, column=0, padx=(20, 20), pady=(50, 0))

        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combobox = customtkinter.CTkOptionMenu(self.frame_left, values=ports, state="readonly")
        self.port_combobox.set("COM14")
        self.port_combobox.grid(row=1, column=0, padx=(20, 20), pady=(10, 0))

        self.baud_combobox_label = customtkinter.CTkLabel(self.frame_left, 
                                                          text="Select Baude Rate:", 
                                                          font=('Bahnschrift SemiLight', 18), 
                                                          text_color='white')
        self.baud_combobox_label.grid(row=2, column=0, padx=(5, 0), pady=(0, 0))

        self.baud_combobox = customtkinter.CTkOptionMenu(self.frame_left, values=["9600", "19200", "115200"], state="readonly")
        self.baud_combobox.grid(row=2, column=0, padx=(20, 20), pady=(100, 0))
        self.baud_combobox.set("115200")

        self.connect_button = customtkinter.CTkButton(self.frame_left,
                                                text="Connect",
                                                command=self.connect)
        self.connect_button.grid(pady=(200, 0), padx=(20, 20), row=2, column=0)

        self.disconnect_button = customtkinter.CTkButton(self.frame_left,
                                                text="Disconnect",
                                                command=self.disconnect,
                                                state=tk.DISABLED)
        self.disconnect_button.grid(pady=(300, 0), padx=(20, 20), row=2, column=0)

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", 
                                                anchor="w", 
                                                font=('Bahnschrift SemiLight', 18), 
                                                text_color='white')
        self.map_label.grid(row=8, column=0, padx=(20, 20), pady=(20, 0))

        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal", "Google satellite"],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=9, column=0, padx=(20, 20), pady=(10, 20))


        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))
        
        self.start_button = customtkinter.CTkButton(self.frame_right,
                                                text="Start",
                                                command=self.start,
                                                state=tk.DISABLED)
        self.start_button.grid(pady=(10, 10), padx=(50, 0), row=0, column=0)

        
        self.label_h = customtkinter.CTkLabel(self.frame_right, 
                                              width=30, height=30,
                                              font=('Bahnschrift SemiLight', 24), 
                                              bg_color=App.BG_COLOR, 
                                              text_color=App.FG_COLOR)
        self.label_h.grid(pady=(5, 5), padx=(0, 30), row=0, column=1)
        
        self.label_m= customtkinter.CTkLabel(self.frame_right, 
                                              width=30, height=30,
                                              font=('Bahnschrift SemiLight', 24), 
                                              bg_color=App.BG_COLOR, 
                                              text_color=App.FG_COLOR)
        self.label_m.grid(pady=(5, 5), padx=(35, 0), row=0, column=1)

        self.label_s = customtkinter.CTkLabel(self.frame_right, 
                                              width=30, height=30,
                                              font=('Bahnschrift SemiLight', 24), 
                                              bg_color=App.BG_COLOR, 
                                              text_color=App.FG_COLOR)
        self.label_s.grid(pady=(5, 5), padx=(95, 0), row=0, column=1)
        

        self.label_sos = customtkinter.CTkLabel(self.frame_right, 
                                              width=60, height=30,
                                              font=('Bahnschrift SemiLight', 24), 
                                              bg_color="gray40", 
                                              text_color="white",
                                              text = "SOS")
        self.label_sos.grid(pady=(5, 5), padx=(200, 0), row=0, column=1)
        self.resizable(True, True)
        self.update_time()
        
        

        self.event_right()
        self.event_left()
        current_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        self.circle = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "circ2.png")).resize((20, 20)))
        
        # Set default values
        self.map_widget.set_position(56.4565238654865, 84.96570561359384) 
        self.map_widget.set_zoom(17)
        self.create_polygon()
        self.map_option_menu.set("OpenStreetMap")
    
    def update_sos(self):
        if (self.but==1 or self.ff):
             self.label_sos.configure(bg_color="red")
        else:
             self.label_sos.configure(bg_color="gray40")
    
    def update_time(self):
        h = strftime('%H')
        m = strftime('%M')
        s = strftime('%S')

        self.label_h.configure(text='{}'.format(h)+":")
        self.label_m.configure(text='{}'.format(m)+":")
        self.label_s.configure(text='{}'.format(s))
        self.frame_right.after(1000, self.update_time)

    def start(self):
        #self.add_marker_event((self.lat, self.lng))
        self.start_button.configure(state='disabled')
        self.workbook = Workbook()
        self.sheet = self.workbook.active
        # Записываем заголовок
        self.sheet.append(["№", "Время", "lat", "lng", "alt", "ax", "ay", "az", "gx", "gy", "gz", "SOS", "freefall"])
        #self.id_record = 1
        try:
            self.thread = threading.Thread(target=self.read_from_port)
            self.thread.start()
            
           
        except Exception as e:
            print(e)

    def event_right(self):
        self.map_widget.add_right_click_menu_command(label="Add Marker",
                                                    command=self.add_marker_event,
                                                    pass_coords=True)        

    def event_left(self):
        self.map_widget.add_left_click_map_command(self.clear_marker_event)

    def add_marker_event(self, coords):
        #self.marker_list.clear()
        #self.marker_list.append(coords)
        #print(self.marker_list)
        self.check_coord(coords)
        if (self.result1==1) and (self.result2==0):
                        marker = self.map_widget.set_marker(coords[0], coords[1], text=None,
                                            icon = self.circle)
                        self.serialSend("f;".encode("utf-8"))
                        self.serialSend("f;".encode("utf-8"))
                        self.serialSend("f;".encode("utf-8"))
                        self.serialSend("f;".encode("utf-8"))
                        self.serialSend("f;".encode("utf-8"))
                        self.serialSend("f;".encode("utf-8"))
                        self.serialSend("f;".encode("utf-8"))
                        print("f")
               
        if (self.result1==1) and (self.result2==1):
                        marker = self.map_widget.set_marker(coords[0], coords[1], text="Нельзя!",
                                      icon = self.circle, 
                                       text_color = '#FF007F',
                                    font = ('Bahnschrift SemiBold', 14))
        
                        self.serialSend("b;".encode("utf-8"))
                        #self.serialSend(';'.encode("utf-8"))
                        print("b")
        
        if (self.result1==0) and (self.result2==0):
                        marker = self.map_widget.set_marker(coords[0], coords[1], text="Нельзя!",
                                       icon = self.circle, 
                                       text_color = '#FF007F',
                                    font = ('Bahnschrift SemiBold', 14))
                        self.serialSend("a;".encode("utf-8"))
                        #self.serialSend(';'.encode("utf-8"))
                        print("a")
        
    def clear_marker_event(self, marker):
        self.map_widget.delete_all_marker()
        
    def check_coord(self, coord):
        self.result1 = 0
        self.result2 = 0
        self.my_fence1 = picket.Fence()	
        self.my_fence1.add_point((56.455298, 84.962561))
        self.my_fence1.add_point((56.455298, 84.967565))
        self.my_fence1.add_point((56.457034, 84.967565))
        self.my_fence1.add_point((56.457034, 84.962561))

        self.my_fence2 = picket.Fence()	
        self.my_fence2.add_point((56.456752, 84.963074))
        self.my_fence2.add_point((56.456767, 84.964156))
        self.my_fence2.add_point((56.455958, 84.964161))
        self.my_fence2.add_point((56.455934, 84.963852))
        self.my_fence2.add_point((56.45583, 84.963786))
        self.my_fence2.add_point((56.455826, 84.963075))
        self.my_fence2.add_point((56.456752, 84.963074))


        #56.45653065476002, 84.96056396279722
        #56.45650879839481, 84.9657321610276
        if self.my_fence1.check_point(coord):
            self.result1 = 1
            
            

        if self.my_fence2.check_point(coord):
            self.result2 = 1
        
            
        '''
        if (result1==1) and (result2==0):
            self.map_widget.set_marker(coord[0], coord[1], text=None,
                                            marker_color_circle="blue",
                                            marker_color_outside="gray40", 
                                            font=("Helvetica Bold", 14))
               
        if (result1==1) and (result2==1):
            self.map_widget.set_marker(coord[0], coord[1], text="Нельзя!",
                                       marker_color_circle="blue",
                                       marker_color_outside="gray40", 
                                       font=("Helvetica Bold", 14))
        
            self.serialSend("a;".encode("utf-8"))
            #self.serialSend(';'.encode("utf-8"))
            print("a")
        
        if (result1==0) and (result2==0):
            self.map_widget.set_marker(coord[0], coord[1], text="Нельзя!",
                                       marker_color_circle="blue",
                                       marker_color_outside="gray40", 
                                       font=("Helvetica Bold", 14))
            self.serialSend("a;".encode("utf-8"))
            #self.serialSend(';'.encode("utf-8"))
            print("a")
        '''

    def create_polygon(self):
        self.list1 = [(56.457034, 84.962561),
                      (56.457029, 84.967565),
                      (56.455217, 84.967565),
                      (56.455298, 84.962548),
                      (56.457034, 84.962561)]
        self.list2 = [(56.456752, 84.963074),
                      (56.456767, 84.964156),
                      (56.455958, 84.964161),
                      (56.45583, 84.963786),
                      (56.45583, 84.963786),
                      (56.455826, 84.963075),
                      (56.456752, 84.963074)]
        
       
        
        self.polygon1 = self.map_widget.set_polygon([(self.list1[0]),
                                    (self.list1[1]), 
                                    (self.list1[2]),
                                    (self.list1[3]), 
                                    (self.list1[4])],

                                    fill_color="blue",
                                    outline_color='blue',
                                    border_width=1,
                                    name="house_polygon")
        
        self.polygon2 = self.map_widget.set_polygon([(self.list2[0]),
                                    (self.list2[1]), 
                                    (self.list2[2]),
                                    (self.list2[3]), 
                                    (self.list2[4]),
                                    (self.list2[5]), 
                                    (self.list2[6])],

                                    fill_color="red",
                                    outline_color='red',
                                    border_width=1,
                                    name="house_polygon")
    
    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def on_closing(self, event=0):
        # Сохраняем файл
        #self.workbook.save(f"serial_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")
        self.destroy()

    def connect(self):
        port = self.port_combobox.get()
        baud = int(self.baud_combobox.get())
        #try:
        self.gps = Serial(port, baud, timeout =1)
        self.disconnect_button.configure(state='normal')
        self.connect_button.configure(state='disabled')
        self.start_button.configure(state='normal')

            #self.thread = threading.Thread(target=self.read_from_port)
            #self.thread.start()
        #except Exception as e:
          #  print(e)

    def disconnect(self):
        self.gps.close()
        # Сохраняем файл
        self.workbook.save(f"serial_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")
        self.id_record = 1
        self.disconnect_button.configure(state='disabled')
        self.connect_button.configure(state='normal')
        self.start_button.configure(state='disabled')


    def read_from_port(self):
        
        while True:
            line = self.gps.readline().decode("utf-8")
            #self.Big_buf.append(self.gps.readline().decode("utf-8"))
            self.parts = line.split(",")
            #print(line)
            if(len(self.parts)>1):
                self.lat = float(self.parts[0])
                print("latitude: ",self.lat)
                self.lng = float(self.parts[1])
                print("longitude: ",self.lng)
                self.alt = float(self.parts[2])
                print("altitude: ",self.alt)

                self.hour = int(self.parts[3])
                print("hour: ",self.hour+7)
                self.min = int(self.parts[4])
                print("minutes: ",self.min)
                self.sec = (self.parts[5])
                print("seconds: ",self.sec)

                self.ax = int(self.parts[6])
                print("ax: ",self.ax)
                self.ay = int(self.parts[7])
                print("ay: ",self.ay)
                self.az = int(self.parts[8])
                print("az: ",self.az)

                self.gx = int(self.parts[9])
                print("gx: ",self.gx)
                self.gy = int(self.parts[10])
                print("gy: ",self.gy)
                self.gz = int(self.parts[11])
                print("gz: ",self.gz)

                self.but = int(self.parts[12])
                self.ff = int(self.parts[13])
                print("flag_SOS: ",self.but)
                print("flag_freefall: ",self.ff)
                self.update_sos()
                
                self.check_coord((self.lat, self.lng))
             
            else:
                print(self.parts[0])
            # Получаем текущее время 
            current_time = strftime('%H:%M:%S')
            # Записываем данные в ячейки
            self.sheet.append([self.id_record, current_time, float(self.lat), float(self.alt), 
                               float(self.lng), int(self.ax), int(self.ay), int(self.az), 
                               int(self.gx), int(self.gy), int(self.gz), int(self.but), 
                               int(self.ff)])
            # Увеличиваем ID
            self.id_record += 1
            

            if (self.lat!=self.prevlat):
                #marker1 = self.map_widget.set_marker(self.lat, self.lng)
                self.prevlat = self.lat
                self.map_widget.delete_all_marker()
                if (self.result1==1) and (self.result2==0):
                        marker1 = self.map_widget.set_marker(self.lat, self.lng, text="1",
                                                             text_color = '#FF007F',
                                                             font = ('Humnst777 Blk BT', 14),
                                                             icon = self.circle)
                        self.serialSend("f;".encode("utf-8"))
                        self.serialSend("f;".encode("utf-8"))
                        self.serialSend("f;".encode("utf-8"))
                        self.serialSend("f;".encode("utf-8"))
                        

                        print("f")

                if (self.result1==1) and (self.result2==1):
                        marker1 = self.map_widget.set_marker(self.lat, self.lng, text="Нельзя!",
                                       icon = self.circle, 
                                       text_color = '#FF007F',
                                    font = ('Bahnschrift SemiBold', 14))
        
                        self.serialSend("b;".encode("utf-8"))
                        print("b")
        
                if (self.result1==0) and (self.result2==0):
                        marker1 = self.map_widget.set_marker(self.lat, self.lng, text="Вне зон",
                                                             icon = self.circle, 
                                       text_color = '#FF007F',
                                    font = ('Bahnschrift SemiBold', 14))
                                       
                        self.serialSend("a;".encode("utf-8"))
                        print("a")
                
                

    def serialSend(self, command):
        self.gps.write(command)


if __name__ == "__main__":
    app = App()
    app.mainloop()