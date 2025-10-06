from accion import accion, escribir_logs

class Nodo_Raft:
    def __init__(self, id_nodo: str, e_timeout: int):
        self.id = id_nodo
        self.e_timeout = int(e_timeout)
        self.is_active = True
        self.logs = []
        self.term = 0
        self.term_ultimo_voto = 0

    def consolidar(self, nodos, bd, acciones_consolidadas):
        logs = []
        for nodo in nodos:
            if nodo.is_active and nodo.logs:
                for log in nodo.logs:
                    if tuple(log) not in acciones_consolidadas:
                        logs.append(log)
        contador = {}
        for elemento in logs:
            contador[tuple(elemento)] = contador.get(tuple(elemento),0)+1
        mas_repetido, max_cantidad = None, 0
        for clave, cantidad in contador.items():
            if cantidad >= max_cantidad:
                mas_repetido, max_cantidad = clave, cantidad
        if max_cantidad > len(nodos)//2 and tuple(mas_repetido) not in acciones_consolidadas:
            if list(mas_repetido) in self.logs:
                indice = self.logs.index(list(mas_repetido))
                for log in self.logs[:indice+1]:
                    if tuple(log) not in acciones_consolidadas:
                        bd = accion(list(log)[0], bd)
            else:
                bd = accion(list(mas_repetido)[0], bd)
            return bd, mas_repetido
        return bd, None

    def send(self, evento, nodos, bd, acciones_consolidadas):
        self.term +=1
        self.logs.append([evento, self.term])
        return self.consolidar(nodos, bd, acciones_consolidadas)

    def spread(self, destinatarios, nodos, bd, acciones_consolidadas):
        if destinatarios:
            for destinatario in destinatarios:
                if destinatario != self.id:
                    for nodo in nodos:
                        if destinatario == nodo.id and nodo.is_active:
                            if self.logs:
                                if nodo.logs:
                                    interseccion = [x for x in self.logs if x in nodo.logs]
                                    extras = [x for x in self.logs if x not in nodo.logs]
                                    nodo.logs = interseccion + extras
                                else:
                                    nodo.logs = self.logs.copy()
                                nodo.term = self.term
                            break
        return self.consolidar(nodos, bd, acciones_consolidadas)

    def votar(self, candidato):
        if self.term_ultimo_voto == candidato.term or candidato.term < self.term:
            return False
        elif not self.logs:
            self.term_ultimo_voto = candidato.term
            return True
        else:
            if candidato.logs and candidato.logs[-1][1] >= self.logs[-1][1]:
                return True
            return False

    def stop(self):
        self.is_active = False

    def start(self, nodos):
        self.term = max([n.term for n in nodos]+[self.term])
        self.is_active = True


def votacion(orden_candidatos, nodos, iteracion):
    habemus_lider = False
    candidato = False
    inicio = max(0, iteracion % len(nodos))
    while not candidato:
        for i in range(inicio,len(orden_candidatos)):
            if orden_candidatos[i].is_active:
                candidato = orden_candidatos[i]
                habemus_lider = True
                break
        if habemus_lider:
            break
        inicio = 0
    candidato.term += 1
    votos = 1
    for nodo in nodos:
        if nodo.is_active and nodo.id != candidato.id and nodo.votar(candidato):
            votos += 1
    if votos > len(nodos)//2:
        for nodo in nodos:
            if nodo.term < candidato.term:
                nodo.term = candidato.term
        return candidato
    elif candidato.term > 50:
        return
    return votacion(orden_candidatos, nodos, iteracion+1)


def raft(path):
    bd = {}
    logs = []
    acciones_consolidadas = []

    with open(path, encoding="utf-8") as f:
        lineas = f.readlines()
        nodos = [Nodo_Raft(dato.split(",")[0], dato.split(",")[1])
                 for dato in lineas[0].split("#",1)[0].strip().split(";")]
        orden_candidatos = sorted(nodos, key=lambda x: x.e_timeout)
        lider = votacion(orden_candidatos, nodos, 0)

        for linea in lineas[1:]:
            linea = linea.split("#",1)[0].strip()
            if not linea:
                continue
            partes = linea.split(";")
            comando = partes[0]

            if comando == "Send" and lider:
                bd, consolidada = lider.send(partes[1], nodos, bd, acciones_consolidadas)
                if consolidada:
                    acciones_consolidadas.append(consolidada)
            elif comando == "Spread" and lider:
                bd, consolidada = lider.spread(partes[1], nodos, bd, acciones_consolidadas)
                if consolidada:
                    acciones_consolidadas.append(consolidada)
            elif comando == "Log" and lider:
                if partes[1] in bd:
                    logs.append(f"{partes[1]}={bd[partes[1]]}")
                else:
                    logs.append(f"{partes[1]}=Variable no existe")
            elif comando == "Start":
                for nodo in nodos:
                    if nodo.id == partes[1]:
                        nodo.start(nodos)
                        nodos_activos = sum(1 for n in nodos if n.is_active)
                        if not lider and nodos_activos > len(nodos)//2:
                            lider = votacion(orden_candidatos, nodos, 0)
            elif comando == "Stop":
                for nodo in nodos:
                    if nodo.id == partes[1]:
                        nodo.stop()
                        if lider and nodo.id == lider.id:
                            nodos_activos = sum(1 for n in nodos if n.is_active)
                            if nodos_activos > len(nodos)//2:
                                lider = votacion(orden_candidatos, nodos, 0)
                            else:
                                lider = False

    escribir_logs(path, bd, logs, "Raft")