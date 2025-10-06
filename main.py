import sys
from paxos import paxos
from raft import raft

if __name__ == "__main__":
    algoritmo = sys.argv[1]  # Paxos o Raft
    path = sys.argv[2]

    if algoritmo == "Paxos":
        paxos(path)
    elif algoritmo == "Raft":
        raft(path)
    else:
        print("Algoritmo no reconocido")
        exit(1)