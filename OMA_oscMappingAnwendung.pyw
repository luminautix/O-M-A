import argparse
from socketserver import BaseRequestHandler, UDPServer
from threading import Thread
from queue import Queue, Empty
from tkinter import Tk, Menu, Label, Frame, filedialog, messagebox, Checkbutton, StringVar
from xml.etree import ElementTree as ET
from pythonosc import osc_message_builder
from pythonosc import udp_client

class SensorUDPServer(UDPServer):

    def __init__(self, server_address, RequestHandlerClass, queue, bind_and_activate=True):
        UDPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate=True)
        self.queue = queue

class SensorUdpHandler(BaseRequestHandler):

    def handle(self):
        self.data = self.request[0].strip()
        self.dataTuple = (self.client_address[0], self.client_address[1], self.data.decode())
        self.server.queue.put(self.dataTuple)

class mainWindow(Frame):
    def __init__(self, queue_1, server_1, master=None):
        super(mainWindow, self).__init__(master)
        self.master.protocol('WM_DELETE_WINDOW', self.beenden)
        self.master.title("Programmtitel")
        self.addMenu()
        self.pack()
        self.queue_1 = queue_1
        self.server_1 = server_1
        self.send_osc_to_sound = StringVar()
        self.send_osc_to_light = StringVar()
        self.send_osc_to_video = StringVar()
        self.addButton()
        self.addSensorLabel()
        self.updateLabelData()

    def addMenu(self):
        self.menueleiste = Menu(self.master)
        self.master.configure(menu=self.menueleiste)
        self.dateimenue = Menu(self.menueleiste)
        self.dateimenue.add_command(label='Öffnen', command= self.load_xml)
        self.dateimenue.add_command(label='Beenden', command=self.beenden)
        self.menueleiste.add_cascade(label='Datei', menu=self.dateimenue)

    def load_xml(self):
        self.datei = filedialog.askopenfilename()
        try:
            self.tree = ET.parse(self.datei)
            self.root = self.tree.getroot()
            if self.root.get('show'):
                self.master.title(self.root.get('show'))
            else:
                self.master.title(self.datei)
        except:
            messagebox.showerror('Fehler', 'Konnte Datei nicht öffnen! Möglicherweise ist das kein XML-Dokument?')

    def addButton(self):
        self.frame_button = Frame(master=self.master, relief="ridge", bd=2)
        self.frame_button.pack(padx=20, ipadx=10, side='left')
        self.button_sound = Checkbutton(master=self.frame_button, justify='left', text="sende OSC an Ton", variable=self.send_osc_to_sound)
        self.button_sound.pack()
        self.button_sound.select()
        self.button_light = Checkbutton(master=self.frame_button, justify='left', text="sende OSC an Licht", variable=self.send_osc_to_light)
        self.button_light.pack()
        self.button_light.select()
        self.button_video = Checkbutton(master=self.frame_button, justify='right',text="sende OSC an Video", variable=self.send_osc_to_video)
        self.button_video.pack()
        self.button_video.select()

    def addSensorLabel(self):
        self.frame_sensor_1 = Frame(master=self.master, relief="ridge", bd=2)
        self.frame_sensor_1.pack(padx=20, pady=10, ipadx=10, side='right')
        self.sensor_1_label_data = Label(master=self.frame_sensor_1, text="Sensor Daten: keine Daten")
        self.sensor_1_label_data.pack()
        self.sensor_1_label_ip = Label(master=self.frame_sensor_1, text="Sensor IP: keine Daten")
        self.sensor_1_label_ip.pack()
        self.sensor_1_label_port = Label(master=self.frame_sensor_1, text="Sensor Port: keine Daten")
        self.sensor_1_label_port.pack()

    def updateLabelData(self):
        try:
            self.message = self.queue_1.get_nowait()
            self.sensor_1_label_data["text"] = "Sensor Daten: " + str(self.message[2])
            self.sensor_1_label_ip["text"] = "Sensor IP: " + str(self.message[0])
            self.sensor_1_label_port["text"] = "Sensor Port: " + str(self.message[1])
        except(Empty):
            pass ## muss noch bearbeitet werden
        self.after(1, self.updateLabelData)

    def beenden(self):
        if messagebox.askyesno('Beenden', 'Wollen Sie das Programm jetzt beenden'):
            self.server_1.shutdown()
            self.master.destroy()

if __name__ == "__main__":

    queue_server_1 = Queue()

# Serverstart für Sensoren oder Externen Input über Netzwerk als eigener Thread ------------------------------------
    HOST, PORT = "", 51456
    server_1 = SensorUDPServer((HOST, PORT), SensorUdpHandler, queue_server_1)
    serverThread_1 = Thread(target=server_1.serve_forever)
    serverThread_1.start()
# Ende

# Starte Fenster ----------------------------------------------------
    root = Tk()
    fenster = mainWindow(queue_server_1, server_1, master=root)
    fenster.mainloop()
# Ende Start Fenster