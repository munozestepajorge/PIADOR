#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from paho.mqtt.client import Client
from multiprocessing.connection import Client as c
from tkinter import Tk, Button, ttk, Frame, Scrollbar, Listbox, Label

"""
piador.py es el programa principal que permitirá
usar el Piador a cada usuario desde su ordenador.

"""

def message_task(msg):
    """
    La función message_task publica en Piador el mensaje que el usuario quiere 
    subir. La publicación se hace usando el widget Listbox de Tkinter para
    interfaces gráficas.
    """
    
    print(msg.topic, msg.payload) 
    mylist.insert(0, msg.topic + ': ' + msg.payload.decode('utf-8'))


def crearcuenta(conn):
    """
    crearcuenta se ejecuta al presionar el botón "crear" en la primera ventana.
    Se usa para conectar con el Listener y enviarle nuestra intención: crear 
    una nueva cuenta con el nombre y la clave que elija el usuario. No podrán 
    crearse cuentas con nombres que ya tienen una.
    """
    
    conn.send("crear")
    nombre = entry_u.get()
    clave = entry_c.get()
    try:
        conn.send((nombre, clave))    
        try:
            resp = conn.recv()
            if resp == "no ok":
                print("El usuario ya existe")
                label_error.config(text = "El usuario ya existe", fg = "red")
                # se muestra al usuario que el nombre elegido no es válido
            else:
                w_entrar.destroy() # se elimina esta ventana
                entrar(resp, nombre, conn)
        except EOFError: 
            print('No receive, connection abruptly closed by listener')
    except IOError:
        print('No send, connection abruptly closed by listener')

        
        
def iniciar(conn):
    """
    La función iniciar se ejecuta al presionar el botón "iniciar" en la primera
    ventana. Al igual que crearcuenta, se usa para conectar con el Listener y 
    enviarle nuestra intención: iniciar sesión con una cuenta ya existente. No 
    podrá iniciarse sesión con una cuenta que no existe o con una clave 
    incorrecta.
    """
    
    try:
        conn.send("iniciar")
        nombre = entry_u.get()
        clave = entry_c.get()
        try:
            conn.send((nombre, clave))
            try:
                resp = conn.recv()
                if resp == "no ok":
                    print("Usuario o clave incorrectos")
                    label_error.config(text = "Usuario o clave incorrectos", fg = "red")
                    # se muestra al usuario que el nombre o la clave no son correctos
                else:
                    w_entrar.destroy() # se elimina esta ventana
                    entrar(resp, nombre, conn)
            except EOFError:
                print('No receive, connection abruptly closed by listener')
        except IOError:
            print('No send, connection abruptly closed by listener')
    except IOError:
        print('No send, connection abruptly closed by listener')


def entrar(pos, nombre, conn):
    """
    La función entrar se ejecuta después de crear cuenta o iniciar sesión. Si 
    el nombre ya existía, "entrar" hará que se suscriba a los usuarios a los
    que seguía. Después de esto, se crea la ventana principal del programa.
    
    """
    
    posicion = int(pos)
    try:
        conn.send("entrar")
        print('Suscribiendose a los ya seguidos')
        conn.send(posicion)
        try:
            lista = conn.recv()
            client.subscribe(nombre)
            if len(lista) > 0: # se suscribe a los que ya seguía (si seguía a alguien)
                for otro in lista:
                    client.subscribe(otro)
            print('Suscrita a los ya seguidos')
            ventanica(nombre, posicion, conn)
            print('ventana creada')
        except EOFError: 
            print('No receive, connection abruptly closed by listener')
    except IOError:
        print('No send, connection abruptly closed by listener')


def ventanica(nombre, pos, conn):
    """
    La función ventanica creará la ventana principal del Piador. Esta ventana 
    consiste en 4 partes:
    - Piar: botón con el que el usuario puede subir los mensajes que escriba
    - Seguir: para poder ver lo que escriben los usuarios que se deseen
    - Desseguir: Para dejar de leer a un usuario en concreto
    - Perfil: muestra otra ventana con tu nombre de usuario, la lista de usuarios
      a los que sigues y la lista de usuarios que te siguen
    """
    
    b_perfil = Button(w_piador, text = "perfil", command = (lambda:perfil(nombre, pos, conn)))
    b_perfil.pack(side = "bottom")
    
    e_desseguir = ttk.Entry(w_piador)
    e_desseguir.pack(side = "bottom")
    b_desseguir = Button(w_piador, text="desseguir", command = (lambda:desseguir(e_desseguir.get(), pos, conn)))
    b_desseguir.pack(side = "bottom")
    
    e_seguir = ttk.Entry(w_piador)
    e_seguir.pack(side = "bottom")
    b_seguir = Button(w_piador, text="seguir", command = (lambda:seguir(e_seguir.get(), pos, conn)))
    b_seguir.pack(side = "bottom")
    
    e_piar = ttk.Entry(w_piador)
    e_piar.pack(side = "bottom")
    b_piar = Button(w_piador, text="piar", command = (lambda:client.publish(nombre, e_piar.get())))
    b_piar.pack(side = "bottom")

    w_piador.deiconify()
    client.w_piador.mainloop()
    
    
def seguir(otro, pos, conn):
    """
    La función seguir se ejecuta cuando el usuario presiona el botón "seguir".
    El usuario se suscribe al topic de la persona a la que quiere seguir solo 
    si aún no la sigue todavía y si esta persona existe en el Piador.
    """
    
    try:
        conn.send(("seguir", otro, pos))
        try:
            resp = conn.recv()
            if resp == "ok seguir": # si todavía no se sigue a esa persona y existe
                client.subscribe(otro)
                l_error.config(text = "")
            elif resp == "casi ok seguir": # si no, se avisa al usuario
                l_error.config(text = "Usuario ya seguido", fg = "red")
            else:
                l_error.config(text = "Usuario no existe", fg = "red")
        except EOFError: 
            print('No receive, connection abruptly closed by listener')
    except IOError:
        print('No send, connection abruptly closed by listener')
    
    
def desseguir(otro, pos, conn):
    """
    La función desseguir se ejecuta cuando el usuario presiona el botón 
    "desseguir". El usuario se dessuscribe del topic que escriba en la entrada 
    solo si le está siguiendo y si esta persona existe en el Piador.
    """
    try:
        conn.send(("desseguir", otro, pos))
        try:
            resp = conn.recv()
            if resp == "no seguido": # si no se sigue a esa persona o no existe
                print("Usuario no seguido")
                l_error.config(text = "Usuario no seguido", fg = "red")
            else: # si se sigue a esa persona
                client.unsubscribe(otro) 
                l_error.config(text = "")
        except EOFError: 
            print('No receive, connection abruptly closed by listener')
    except IOError:
        print('No send, connection abruptly closed by listener')
    
    
def perfil(nombre, pos, conn):
    """
    La función perfil se ejecuta cuando el usuario presiona el botón "perfil".
    Crea y abre la ventana del perfil, donde el usuario puede ver los usuarios 
    seguidos y los seguidores.
    """
    w_perfil = Tk()
    w_perfil.title("PERFIL")
    Label(w_perfil, text = nombre, font = ("Helvetica", 19)).pack(side = "top")

    try:
        conn.send(("perfil", pos))
        try:
            (seguidos, seguidores) = conn.recv()
            
            vs_seguidos = Scrollbar(w_perfil)
            vs_seguidos.pack(side = "left", fill = "y")
            vs_seguidores = Scrollbar(w_perfil)
            vs_seguidores.pack(side = "right", fill = "y")
           
            l_seguidos = Listbox(w_perfil, yscrollcommand = vs_seguidos.set)
            l_seguidos.pack( side = "left", expand = 1, fill = "both") 
            vs_seguidos.config( command = l_seguidos.yview )
            l_seguidores = Listbox(w_perfil, yscrollcommand = vs_seguidores.set)
            l_seguidores.pack( side = "right", expand = 1, fill = "both")
            vs_seguidores.config( command = l_seguidores.yview )
            
            for otro in seguidos:
                l_seguidos.insert(0, otro)
            l_seguidos.insert(0, " ")
            l_seguidos.insert(0, "SEGUIDOS")
            for otro in seguidores:
                l_seguidores.insert(0, otro)
            l_seguidores.insert(0, " ")
            l_seguidores.insert(0, "SEGUIDORES")
            
            w_perfil.mainloop()
            
        except EOFError: # no hace falta importar este error
            print('No receive, connection abruptly closed by listener')
            
    except IOError:
        print('No send, connection abruptly closed by listener')


if __name__ == "__main__":

    """
    La función principal de piador.py crea las ventanas para entrar en la red y la ventana
    donde se verán los mensajes. También se conecta al broker y al listener.
    """
    
    #dirección del listener
    ip = "192.168.1.52"
    #dirección del broker
    broker = "broker.hivemq.com"
    
    #conectar al listener
    print('conectando')
    conn = c(address = (ip, 6000), authkey = b'secret password')
    print('conexion aceptada')
    
    #conectar al broker
    client = Client()
    client.on_message = message_task
    client.connect(broker)
    print("conectado al broker")
    client.loop_start()


    # creación de la ventana de inicio
    w_entrar = Tk()
    w_entrar.title("Crear cuenta o Iniciar sesion")
    w_entrar.geometry('300x200')
    
    label_u = Label(w_entrar, text = "usuario")
    label_u.place(x = 50, y = 50)
    entry_u = ttk.Entry(w_entrar)
    entry_u.place(x=103, y=50)
    button_c = Button(w_entrar, text="crear", command = lambda:crearcuenta(conn))
    button_c.place(x=103, y=100)
    
    label_c = Label(w_entrar, text = "clave")
    label_c.place(x = 50, y = 70)
    entry_c = ttk.Entry(w_entrar)
    entry_c.place(x=103, y=70)
    button_i = Button(w_entrar, text="iniciar", command = lambda:iniciar(conn))
    button_i.place(x=173, y=100)
    
    label_error = Label(w_entrar, text = "")
    label_error.place(x = 50, y = 130)
    
    
    # creación de la ventana principal de PIADOR
    w_piador = Tk()
    w_piador.title("PIADOR")
    w_piador.withdraw()
    
    f = Frame(w_piador, bg = "white")
    f.pack(side = "top", expand = 1, fill = "both")
    
    vscroll = Scrollbar(f)
    vscroll.pack(side = "right", fill = "y")
    hscroll = Scrollbar(f, orient = "horizontal")
    hscroll.pack(side = "bottom", fill = "x")
    mylist = Listbox(f, yscrollcommand = vscroll.set, xscrollcommand = hscroll.set)
    mylist.insert(0, "Bienvenid@ a piador")
    mylist.pack( side = "left", expand = 1, fill = "both") 
    vscroll.config( command = mylist.yview )
    hscroll.config( command = mylist.xview )
    
    l_error = Label(w_piador, text = "")
    l_error.pack(side = "bottom")
    
    client.w_piador = w_piador
        
    w_entrar.mainloop()
    
    conn.close()
