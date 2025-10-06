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
    return bd

class Nodo():
    def __init__(self, id_nodo: str):
        self.id = id_nodo
        self.is_active = True

class Nodo_aceptante(Nodo):
    def __init__(self, id_nodo: str):
        super().__init__(id_nodo)
        self.acciones_aceptadas = []
        self.mayor_n = 0
    
    def votar(self, id_propuesta):
        # No ha recibido antes un prepare
        if self.mayor_n == 0:
            self.mayor_n = id_propuesta
            return True
        else:
            if self.mayor_n > id_propuesta:
                return False
            if self.mayor_n < id_propuesta:
                self.mayor_n = id_propuesta
                if len(self.acciones_aceptadas) > 0:
                    return [True, self.acciones_aceptadas[-1][0],self.acciones_aceptadas[-1][1]]
                else:
                    return True
                
    def recibir_accion(self,accion, id_propuesta):
        if id_propuesta >= self.mayor_n:
            self.acciones_aceptadas.append([accion, id_propuesta])
    def stop(self):
        self.is_active = False
    def start(self):
        self.is_active = True

class Nodo_proponente(Nodo):
    def __init__(self, id_nodo: str):
        super().__init__(id_nodo)
        self.propuestas_aceptadas = []
        self.acciones_previas = []

    # 1. Hace votar a los nodos aceptantes activos
    # 2. Respuestas posibles : Aceptado, rechazado (no suma en votos) o
    #  acepta pero avisa que ya había aceptado otra accion antes
    # 3. si la mayoria acepta, se guarda la propuesta en propuestas_aceptadas 
    def proponer(self, aceptantes, id_propuesta):
        votos = 0
        for nodo in aceptantes:
            if nodo.is_active:
                voto = nodo.votar(id_propuesta)
                if isinstance(voto,bool):
                    if voto:
                        votos += 1 
                else :
                    votos += 1
                    # CASO ESPECIAL
                    self.acciones_previas.append([voto[1], voto[2]])
        if votos > len(aceptantes)//2:
            
            self.propuestas_aceptadas.append(id_propuesta)
                                    
    def aceptar(self, aceptantes, id_propuesta, accion):
        # Primero verificar que nos aceptaron la propuesta
        if len(self.propuestas_aceptadas) > 0:
            for propuestas in self.propuestas_aceptadas:
                if propuestas == id_propuesta:
                    # Si nadie tenía una acción que compartir, envió la mía
                    if not self.acciones_previas:
                        for nodo in aceptantes:
                                    if nodo.is_active:
                                        nodo.recibir_accion(accion, id_propuesta)
                    else:
                        # enviamos el que tiene mayor id
                        mayor = self.acciones_previas[0]
                        for elemento in self.acciones_previas:
                            if elemento[1] > mayor[1]:
                                mayor = elemento
                        
                        for nodo in aceptantes:
                            if nodo.is_active:
                                nodo.recibir_accion(mayor[0], id_propuesta)
                    
        self.acciones_previas = []


def paxos(path):
    bd = {}
    logs = []

    with open(path, encoding="utf-8") as f:
        lineas = f.readlines()
        
        nodos_aceptantes = [Nodo_aceptante(id.strip()) for id in lineas[0].split("#", 1)[0].split(";")]
        nodos_proponentes = [Nodo_proponente(id.strip()) for id in lineas[1].split("#", 1)[0].split(";")]
        
        

        # COMANDOS
        if lineas[2]:
            for linea in lineas[2:]:
            #esto para eliminar el comentario al final de la línea
                linea = linea.split("#", 1)[0].strip()
                if not linea:
                    continue

                partes = linea.split(";")

                comando = partes[0]


                # TODO: Completar con la lógica de cada comando

               

                if comando == "Prepare":
                    for nodo in nodos_proponentes:
                        if nodo.id == partes[1]:
                            nodo.proponer(nodos_aceptantes, int(partes[2]))

                elif comando == "Accept": 
                    for nodo in nodos_proponentes:
                        if nodo.id.strip() == partes[1].strip():
                            nodo.aceptar(nodos_aceptantes, int(partes[2]), partes[3])

                elif comando == "Learn":
                    acciones = []
                    for nodo in nodos_aceptantes:
                        acciones.append(nodo.acciones_aceptadas)
                    
                    contador = {}
                    
                    if acciones:
                        for acciones_por_nodo in acciones:
                            acciones_unicas = set(tuple(a) for a in acciones_por_nodo)
                            for accion1 in acciones_unicas:
                                if accion1 not in contador:
                                    contador[accion1] = 0
                                contador[accion1] += 1
                        recurrentes = [list(a) for a, veces in contador.items() if veces > len(nodos_aceptantes) / 2]
                        
                        bd = accion(recurrentes[-1][0], bd)
                    for nodo in nodos_aceptantes:
                        if nodo.is_active:
                            nodo.propuestas = []
                            nodo.acciones_aceptadas = []
                            nodo.mayor_n = 0
                    for nodo in nodos_proponentes:
                        if nodo.is_active:
                            nodo.propuestas_aceptadas = []
                            nodo.acciones_previas = []  


                elif comando == "Log":
                    if partes[1] in bd:
                        logs.append(f"{partes[1]}={bd[partes[1]]}")
                    else:
                        logs.append(f"{partes[1]}=Variable no existe")

                elif comando == "Start":
                    for nodo in nodos_aceptantes:
                        if nodo.id == partes[1]:
                            nodo.start()
                
                elif comando == "Stop":
                    for nodo in nodos_aceptantes:
                        if nodo.id == partes[1]:
                            nodo.stop()

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

    # Acá se escribe el archivo de logs
    archivo = os.path.basename(path)
    salida = os.path.join("logs", f"Raft_{archivo}")

    os.makedirs("logs", exist_ok=True)

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
        