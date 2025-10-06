import os

def accion(linea, bd):
    linea = linea.split("#", 1)[0].strip()
    if not linea:
        return bd

    divisiones = linea.split("-", 2)
    comando = divisiones[0]

    if comando == "SET" and len(divisiones) == 3:
        bd[divisiones[1]] = divisiones[2]

    elif comando == "ADD" and len(divisiones) == 3:
        variable, valor = divisiones[1], divisiones[2]
        if variable not in bd:
            bd[variable] = valor
        else:
            try:
                bd[variable] = str(int(bd[variable]) + int(valor))
            except ValueError:
                bd[variable] = str(bd[variable]) + str(valor)

    elif comando == "DEL" and len(divisiones) == 2:
        bd.pop(divisiones[1], None)

    return bd


def escribir_logs(path, bd, logs, algoritmo):
    os.makedirs("logs", exist_ok=True)
    archivo = os.path.basename(path)
    salida = os.path.join("logs", f"{algoritmo}_{archivo}")
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