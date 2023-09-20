# Este archivo implementa la simulacion del algoritmo de 
# difusion de informacion con retroalimentacion (Propagation of Information with Feedback) de A. Segall

import sys
from event import Event
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation

class AlgorithmPI(Model):
    # Esta clase desciende de la clase Model e implementa los metodos
    # "init()" y "receive()", que en la clase madre se definen como abstractos
  
    def init(self):
        # Aqui se definen e inicializan los atributos particulares del algoritmo
        print("Inicio funciones", self.id)
        #se inicializa el arreglo de banderas
        self.ok = {}
        print("Mis vecinos son: ", end=" ")
        for neighbor in self.neighbors:
            #inicialmente en falso==0; verdadero==1
            self.ok[neighbor] = 0
            print(neighbor, end=" ")
        print("\n")
        #print(banderas)

        self.vecinos = self.neighbors
        #visitado indica si el mensaje ya paso por el nodo
        #inicialmente falso -> 0. Verdadero -> 1
        self.visitado = 0
        #padre, el nodo del que se recibe el mensaje por primera vez
        self.father = self.id

    def receive(self, event):
        # Aqui se definen las acciones concretas que deben ejecutarse cuando se
        # recibe un evento
        print("T = ", self.clock, " Nodo [", self.id, "] Recibo :", event.getName(), "desde [", event.getSource(), "]")

        #al recibir INICIA
        if event.getName() == "INICIA":
            #se pone a si mismo como visitado
            self.visitado = 1
            # y para cada vecino
            for neighbor in self.vecinos:
                # envia M a neighbor
                newevent = Event("M", self.clock + 1.0, neighbor, self.id)
                self.transmit(newevent)
        #al recibir M, el mensaje
        elif event.getName() == "M":
            #pone en verdadero la bandera del transmisor
            self.ok.update({event.source: 1})
            print("Nodo [", self.id, "] OK: ", self.ok)
            #y si no ha sido visitado
            if self.visitado == 0:
                #asigna al nodo transmisor como su padre
                self.father = event.getSource()
                #se pone a si mismo como visitado
                self.visitado = 1
                #se elimina el nodo transmisor de la lista de vecinos del receptor
                self.vecinos.remove(event.getSource())
                #y para cada vecino
                for neighbor in self.vecinos:
                        #envia M a neighbor
                        newevent = Event("M", self.clock + 1.0, neighbor, self.id)
                        self.transmit(newevent)
            #si ya ha sido visitado
            #checa si todos sus vecinos le han enviado mensaje
            regresa = all(bandera == 1 for bandera in self.ok.values())
            print("Nodo [", self.id, "] OK: ", regresa)
            #si es cierto que todos sus vecinos le han enviado mensaje,
            if regresa == True:
                #y si no es su propio padre (no es la raiz)
                if self.father != self.id:
                    #envia M a padre
                    newevent = Event("M", self.clock + 1.0, self.father, self.id)
                    self.transmit(newevent)
                #si es la raiz
                else:
                    print("El mensaje ha llegado de regreso a la raiz")
# ----------------------------------------------------------------------------------------
# "main()"
# ----------------------------------------------------------------------------------------
# construye una instancia de la clase Simulation recibiendo como parametros el nombre del 
# archivo que codifica la lista de adyacencias de la grafica y el tiempo max. de simulacion

if len(sys.argv) != 2:
    print("Por favor dame el nombre del archivo con la grafica de comunicaciones")
    raise SystemExit(1)

maxtime= 100
experiment = Simulation(sys.argv[1], maxtime)#filename, maxtime

# imprime lista de nodos que se extraen del archivo
# experiment.graph[indice+1 == nodo] == vecino
print("Lista de nodos: ", experiment.graph)

# asocia un pareja proceso/modelo con cada nodo de la grafica
for i in range(1,len(experiment.graph)+1):
    m = AlgorithmPI()
    experiment.setModel(m, i)

# inserta un evento semilla en la agenda y arranca
seed = Event("INICIA", 0.0, 1, 1)#name, time, target, source
experiment.init(seed)
experiment.run()
