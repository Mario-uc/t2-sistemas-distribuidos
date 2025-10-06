from accion import accion, escribir_logs

class Nodo:
    def __init__(self, id_nodo: str):
        self.id = id_nodo
        self.is_active = True

class Nodo_aceptante(Nodo):
    def __init__(self, id_nodo: str):
        super().__init__(id_nodo)
        self.acciones_aceptadas = []
        self.mayor_n = 0

    def votar(self, id_propuesta):
        if self.mayor_n == 0:
            self.mayor_n = id_propuesta
            return True
        elif self.mayor_n > id_propuesta:
            return False
        elif self.mayor_n < id_propuesta:
            self.mayor_n = id_propuesta
            if self.acciones_aceptadas:
                return [True, self.acciones_aceptadas[-1][0], self.acciones_aceptadas[-1][1]]
            return True

    def recibir_accion(self, accion_str, id_propuesta):
        if id_propuesta >= self.mayor_n:
            self.acciones_aceptadas.append([accion_str, id_propuesta])

    def stop(self):
        self.is_active = False

    def start(self):
        self.is_active = True


class Nodo_proponente(Nodo):
    def __init__(self, id_nodo: str):
        super().__init__(id_nodo)
        self.propuestas_aceptadas = []
        self.acciones_previas = []

    def proponer(self, aceptantes, id_propuesta):
        votos = 0
        for nodo in aceptantes:
            if nodo.is_active:
                voto = nodo.votar(id_propuesta)
                if isinstance(voto, bool) and voto:
                    votos += 1
                elif isinstance(voto, list):
                    votos += 1
                    self.acciones_previas.append([voto[1], voto[2]])
        if votos > len(aceptantes)//2:
            self.propuestas_aceptadas.append(id_propuesta)

    def aceptar(self, aceptantes, id_propuesta, accion_str):
        if id_propuesta in self.propuestas_aceptadas:
            if not self.acciones_previas:
                for nodo in aceptantes:
                    if nodo.is_active:
                        nodo.recibir_accion(accion_str, id_propuesta)
            else:
                mayor = max(self.acciones_previas, key=lambda x: x[1])
                for nodo in aceptantes:
                    if nodo.is_active:
                        nodo.recibir_accion(mayor[0], id_propuesta)
        self.acciones_previas = []


def paxos(path):
    bd = {}
    logs = []

    with open(path, encoding="utf-8") as f:
        lineas = f.readlines()
        nodos_aceptantes = [Nodo_aceptante(id.strip()) 
                            for id in lineas[0].split("#",1)[0].split(";")]
        nodos_proponentes = [Nodo_proponente(id.strip()) 
                             for id in lineas[1].split("#",1)[0].split(";")]

        for linea in lineas[2:]:
            linea = linea.split("#",1)[0].strip()
            if not linea:
                continue
            partes = linea.split(";")
            comando = partes[0]

            if comando == "Prepare":
                for nodo in nodos_proponentes:
                    if nodo.id == partes[1]:
                        nodo.proponer(nodos_aceptantes, int(partes[2]))
            elif comando == "Accept":
                for nodo in nodos_proponentes:
                    if nodo.id == partes[1].strip():
                        nodo.aceptar(nodos_aceptantes, int(partes[2]), partes[3])
            elif comando == "Learn":
                acciones = [nodo.acciones_aceptadas for nodo in nodos_aceptantes]
                contador = {}
                for acciones_por_nodo in acciones:
                    acciones_unicas = set(tuple(a) for a in acciones_por_nodo)
                    for accion1 in acciones_unicas:
                        contador[accion1] = contador.get(accion1,0)+1
                recurrentes = [list(a) 
                               for a, veces in contador.items() 
                               if veces > len(nodos_aceptantes)/2]
                if recurrentes:
                    bd = accion(recurrentes[-1][0], bd)
                for nodo in nodos_aceptantes:
                    if nodo.is_active:
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

    escribir_logs(path, bd, logs, "Paxos")