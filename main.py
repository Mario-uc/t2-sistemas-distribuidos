from __future__ import annotations  # Solo lo dejo por si lo necesitan. Lo pueden eliminar
from sys import argv

# Librerías adicionales por si las necesitan
# No son obligatorias y no tampoco tienen que usarlas todas
# No pueden agregar ningun otro import que no esté en esta lista
import os
import typing
import collections
import itertools
import dataclasses
import enum

# Recuerda que no se permite importar otros módulos/librerías a excepción de los creados
# por ustedes o las ya incluidas en este main.py


# La función accion recibe una línea del archivo .txt y la base de datos bd
# y modifica la base de datos según el comando (SET, ADD, DEL)

def accion(linea, bd):

    #para eliminar el comentario al final de la línea
    linea = linea.split("#", 1)[0].strip()
    if not linea:
        return


    divisiones = linea.split("-", 2)
    comando = divisiones[0]

    if comando == "SET" and len(divisiones) == 3:
        variable = divisiones[1]
        valor = divisiones[2]

        bd[variable] = valor

    elif comando == "ADD" and len(divisiones) == 3:
        variable = divisiones[1]
        valor = divisiones[2]

        if variable not in bd:
            bd[variable] = valor

        else:
            valor_actual = str(bd[variable])
            # usar try-except para verificar si es entero o no
            # referencia:
            # https://www.geeksforgeeks.org/python/check-if-string-is-integer-in-python/
            try:
                nuevo_valor = str(int(valor_actual) + int(valor))
                bd[variable] = nuevo_valor
            except ValueError:
                nuevo_valor = str(valor_actual) + str(valor)
                bd[variable] = nuevo_valor



    elif comando == "DEL" and len(divisiones) == 2:
        variable = divisiones[1]
        if variable in bd:
            bd.pop(variable, None)



def paxos(path):
    bd = {}
    propuestas = {}
    aceptadas = {}
    logs = []  



    with open(path, encoding="utf-8") as f:
        for linea in f:

            #esto para eliminar el comentario al final de la línea
            linea = linea.split("#", 1)[0].strip()
            if not linea:
                continue

            partes = linea.split(";")

            comando = partes[0]


            # TODO: Completar con la lógica de cada comando

            if comando == "Prepare":
                pass

            elif comando == "Accept":
                pass

            elif comando == "Learn":
                pass

            elif comando == "Log":
                pass

            elif comando == "Start":
                pass
            
            elif comando == "Stop":
                pass

            else:
                pass


    # Acá se escribe el archivo de logs
    archivo = os.path.basename(path)
    salida = os.path.join("logs", f"Paxos_{archivo}")
    
    ruta_salida = os.path.dirname(salida)

    with open(salida, "w", encoding="utf-8") as f:
        f.write("LOGS\n")
        if logs:
            for linea in logs:
                f.write(linea + "\n")
        else:
            f.write("No hubo logs\n")
        
        f.write("BASE DE DATOS\n")
        if bd:
            for k, v in bd.items():
                f.write(f"{k}={v}\n")
        else:
            f.write("No hay datos\n")




            

def raft(path):
    bd = {}    
    logs = []    

    with open(path, encoding="utf-8") as f:
        for linea in f:

            linea = linea.split("#", 1)[0].strip()
            if not linea:
                continue

            partes = linea.split(";")
            comando = partes[0]

            # TODO: Completar con la lógica de cada comando
            if comando == "Send":
                pass

            elif comando == "Spread":
                pass

            elif comando == "Log":
                pass

            elif comando == "Start":
                pass

            elif comando == "Stop":
                pass

            else:
                pass

    # --- Guardar logs en archivo ---
    archivo = os.path.basename(path)
    salida = os.path.join("logs", f"Raft_{archivo}")

    os.makedirs("logs", exist_ok=True)

    with open(salida, "w", encoding="utf-8") as f:
        # LOGS
        f.write("LOGS\n")
        if logs:
            for linea in logs:
                f.write(linea + "\n")
        else:
            f.write("No hubo logs\n")

        # BASE DE DATOS
        f.write("BASE DE DATOS\n")
        if bd:
            for k, v in bd.items():
                f.write(f"{k}={v}\n")
        else:
            f.write("No hay datos\n")




if __name__ == "__main__":
    # Completar con tu implementación o crea más archivos y funciones
    print(argv)

    algoritmo = argv[1]  #Paxos o Raft
    path = argv[2] 


    if algoritmo == "Paxos":
        paxos(path)

    elif algoritmo == "Raft":
        raft(path)

    else:
        print("Algoritmo no reconocido")
        exit(1)
        