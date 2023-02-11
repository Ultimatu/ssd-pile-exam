"""module contenant toute les gestions demandées dans la l'exercie."""

import datetime
import math
import threading

# Gestion des Heures


def formatHeure(minutes):
    """Recoit les minutes écoulées depuis minuit en paramètre et retourne en format heure."""
    h = minutes // 60
    m = minutes % 60
    return "{}h{:02d}".format(h, m)


# comparaison des heures
def estAvant(h1, h2):
    """Recoit les heures h1 et h2 en commentaires et dit laquelle est en avance."""
    return h1 < h2


# Gestion des stations
class Station:
    """Gestion des stations."""

    def __init__(self, nom, nb_places, _x=0, _y=0):
        self.nom = nom
        self.places = nb_places
        self.velos = []
        self.x = 0 if not _x else _x
        self.y = 0 if not _y else _y

    def estPleine(self):
        """Verifie si la station est pleine et retourne une valeur booléene."""
        return len(self.velos) == self.places

    def estVide(self):
        """Verifie si la station est Vide et retourne une valeur booléene."""
        return len(self.velos) == 0

    def garer(self, velo):
        """Prends l'identifiant d'un vélo et le gare dans la station courante"""
        if not self.estPleine():
            self.velos.append(velo)
        else:
            raise Exception("Aucun emplacements disponibles.")

    def retirer(self) -> int:
        """Retire le dernier vélo de la station et retourne sa valeur."""
        if not self.estVide():
            return self.velos.pop()
        else:
            raise Exception("La station est vide.")

    def afficher(self) -> str:
        etat = "pleine" if self.estPleine() else "n'est pas encore pleine."
        return f"La station {self.nom} est {etat}."
    
    def afficherVelos(self) -> str:
        """Affiche les vélos disponibles dans la station"""
        if self.estVide():
            return "La station est vide"
        return f"Le nombres de vélos disponibles dans la station {self.nom} est : {len(self.velos)} "
        

    def prochaineNonVide(self, stations) -> str:
        distance_min = float('inf')
        station_non_vide = None
        for station in stations:
            if len(station.velos) > 0 and not station.estVide():
                distance = math.sqrt(
                    (self.x - station.x)**2 + (self.y - station.y)**2)
                if distance < distance_min:
                    distance_min = distance
                    station_non_vide = station.nom
        return str(station_non_vide)

    def prochaineNonPleine(self, stations) -> str:
        distance_min = float('inf')
        station_non_pleine = None
        for station in stations:
            if station.places > 0 and not station.estPleine():
                distance = math.sqrt(
                    (self.x - station.x)**2 + (self.y - station.y)**2)
                if distance < distance_min:
                    distance_min = distance
                    station_non_pleine = station.nom
        return str(station_non_pleine)


# Gestion des deplacements

class Deplacement:
    """Prends les coordonnées du deplacements d'un velo et renvoie le deplacements sous forme de chaines de carracteres.
    """

    def __init__(self, _velo, _station_depart, _h_depart, _station_arrivee, _h_arrivee=None):
        self.velo = _velo
        self.station_depart = _station_depart
        self.h_depart = _h_depart
        self.station_arrivee = _station_arrivee
        self.h_arrivee = _h_depart + 30 if _h_arrivee is None else _h_arrivee
        if self.h_arrivee <= self.h_depart:
            raise ValueError(
                "L'heure de depart ne peut pas etre superieure ou egale a l'heure d'arrive")

    def __str__(self):
        return f"[Velo {self.velo} de {self.station_depart} a {formatHeure(self.h_depart)} pour {self.station_arrivee} a {formatHeure(self.h_arrivee)}]"


# class de file de deplacements
class FileDeplacements:
    def __init__(self):
        self.file = []

    def ajouter(self, deplacement):
        self.file.append(deplacement)
        self.file.sort(key=lambda x: x.h_arrivee)

    def retirer(self):
        if len(self.file) == 0:
            raise Exception("Erreur: file vide")
        return self.file.pop(0)

    def prochain(self):
        if len(self.file) == 0:
            raise Exception("Erreur: file vide")
        return f"Prochain déplacements: {self.file[0]}"

    def afficherFile(self):

        return [str(x) for x in self.file]

    def __len__(self):
        return len(self.file)


# Gestion des velibs
class Velib:

    def __init__(self):
        self.stations = {}
        self.plan = FileDeplacements()
        self.encours = FileDeplacements()
        current_time = datetime.datetime.now().time()
        duration_in_seconds = (current_time.hour * 60 +
                               current_time.minute) * 60 + current_time.second
        self.heure_actuelle = int(duration_in_seconds / 60)

    def ajouterDeplacement_encours(self, deplacement):
        self.encours.ajouter(deplacement)

    def ajouterPlan(self, deplacement):
        self.plan.ajouter(deplacement)
        if deplacement.h_depart <= self.heure_actuelle < deplacement.h_arrivee:
            self.ajouterDeplacement_encours(deplacement)

    def arriveeVelo(self, deplacement):
        """Trouve la station d'arrivée d'un vélo et gare le vélo dans cette station.
        :Puis retirer ce deplacement dans les liste de deplacements en cours et deplacements planifier.
        """
        for (id, station) in self.stations.items():
            if id == deplacement.station_arrivee:
                try:
                    station.garer(deplacement.velo)
                    for i in self.encours.file:
                        if i.h_arrivee == deplacement.h_arrivee:
                            inde = self.encours.file.index(i)
                            a = self.encours.file.pop(inde)
                            break
                    for j in self.plan.file:
                        if j.h_arrivee == deplacement.h_arrivee and j.h_depart == deplacement.h_depart:
                            inde = self.plan.file.index(j)
                            b = self.plan.file.pop(inde)
                            break
                    return f"Velo {deplacement.velo} garé à {str(deplacement.station_arrivee)}."
                except Exception as e:
                    return str(e)
        return f"La station d'arrivée {deplacement.station_arrivee} n'a pas été trouvée."

    def __automatiser__(self):
        """Cette fonction s'execute dans un autre thread.
        Elle est appélé de manière recursive par la function et qui se charge de parcourir
        les deux listes `plan et encours` et lorsque l'heure acteulle est superieur à l'heure d'arriver d'un deplacement en cours,
        elle exécute la function `arriveevelo() avec pour argument le deplacement dont l'heure d'arrivee est inferieur à l'heure locale actuelle` et si l'heure de depart d'un deplacement planifier est arrivee, on  l'ajoute direcement dans la liste de deplacement en cours en attendant son heure d'arriver.
        :Voici comment declarer son processus.
        >>> `velib = Velib()` #instancier la classe velib.
        #creer un thread dans lequel sera éxecuter cette la function.
        >>> `t = threading.Thread(target=run_automatiser, args=(velib,))`
        >>> `t.start()` #Executer"""
        current_time = datetime.datetime.now().time()
        duration_in_seconds = (current_time.hour * 60 +
                               current_time.minute) * 60 + current_time.second
        self.heure_actuelle = int(duration_in_seconds / 60)
        while True:
            if len(self.plan) > 0:
                for deplacement in self.plan:
                    if formatHeure(deplacement.h_depart) <= self.heure_actuelle < formatHeure(deplacement.h_arrivee):
                        self.plan.retirer(deplacement)
                        self.ajouterDeplacement_encours(deplacement)
            if len(self.encours) > 0:
                for deplacement in self.encours:
                    if deplacement.h_arrivee == self.heure_actuelle:
                        self.arriveeVelo(deplacement)


def run_automatiser(velib):
    velib.__automatiser__()


if __name__ == "__main__":
    # Créer un objet Velib pour activer la fonction automatiser
    velib = Velib()
    t = threading.Thread(target=run_automatiser, args=(velib,))
    t.start()
    # Tests pour la classe Station
    station1 = Station("Yop_city", 20)
    station2 = Station("Cocody_Palmeraie", 20, 5, 5)

    print("La station est Pleine?", station1.estPleine())
    print("La station est Vide?", station1.estVide())
    for i in range(20):
        station1.garer(i)
    print("La station est Pleine?", station1.estPleine())
    print("La station est Vide?", station1.estVide())

    try:
        station1.garer(21)
    except Exception as e:
        print(str(e))

    station1.retirer()

    print("Etat de la station: ", station1.afficher())

    station3 = Station("Plateau_Sotra", 20, 3, 3)
    station4 = Station("Koumassi", 20, 4, 4)
    station5 = Station("Adjame", 20, 2, 2)

    stations = [station3, station4, station5]
    print("la station prochaine proche non vide est :",
          station1.prochaineNonVide(stations))
    station3.garer(1)
    print("la station prochaine proche non vide est: ",
          station1.prochaineNonVide(stations))

    station4.garer(1)
    print("la station prochaine proche non pleine est :",
          station1.prochaineNonPleine(stations))
    for i in range(20):
        station5.garer(i)
    print(station5.afficherVelos())
    print("la station prochaine proche non pleine est: ",
          station1.prochaineNonPleine(stations))

    # Test Pour Deplacement
    try:
        deplacement = Deplacement(1, station1.nom, 10, station2.nom, 20)
    except Exception as e:
        print(str(e))
    print(deplacement)
    try:
        deplacement = Deplacement(1, station3.nom, 10, station4.nom)
    except Exception as e:
        print(str(e))
    print(deplacement)

    # Tests Pour FileDeplacements
    fileDeplacements = FileDeplacements()

    try:
        fileDeplacements.retirer()
    except Exception as e:
        print(str(e))

    fileDeplacements.ajouter(deplacement)
    print(
        f"FileDeplacements - Afficher file: {fileDeplacements.afficherFile()}")

    print(f"FileDeplacements - prochain: {fileDeplacements.prochain()}")

    fileDeplacements.retirer()
    print(
        f"FileDeplacements - file avoir retirer le premier élément: {fileDeplacements.afficherFile()}")

    # Tests Pour Velib
    velib = Velib()

    velib.stations = {
        "Station1": Station("Yop_Micao", 20, 1, 1),
        "Station2": Station("Cocody_Palmeraie", 20, 5, 5),
        "Station3": Station("Plateau_Sotra", 20, 3, 3),
        "Station4": Station("Koumassi", 20, 4, 4),
        "Station5": Station("Adjame", 20, 2, 2),
        "Station6": Station("Plateau_Sotra", 20, 6, 6),
        "Station7": Station("Yop_Siporex", 20, 7, 7),
        "Station8": Station("Adjame_Librté", 20, 8, 8),
        "Station9": Station("Plateau_Mairie", 20, 9, 9),
        "Station10": Station("Bingervielle", 20, 10, 10)
    }
    # Test 2: Add a velo to the station
    velos = []
    for id in range(1, 8):
        velos.append(id)
    for velo in velos:
        velib.stations["Station1"].garer(velos[velo-1])
    # Test 4: Ajouter plan de deplacement
    deplacement1 = Deplacement(velos[0], "Station1", 300,  "Station3", 550)
    deplacement2 = Deplacement(velos[1], "Station2", 400,  "Station4", 900)
    deplacement3 = Deplacement(velos[2], "Station2", 300,  "Station6", 400)
    deplacement4 = Deplacement(velos[3], "Station5", 100,  "Station7", 300)
    deplacement5 = Deplacement(velos[4], "Station6", 300,  "Station2", 800)
    deplacement6 = Deplacement(velos[5], "Station3", 500,  "Station1", 1500)
    deplacement7 = Deplacement(velos[6], "Station2", 1200,  "Station7", 3500)

    deplacements = [deplacement1, deplacement2, deplacement3,
                    deplacement4, deplacement5, deplacement6, deplacement7]
    for dep in deplacements:
        velib.ajouterPlan(dep)
        velib.ajouterDeplacement_encours(dep)
        print()
        print(velib.arriveeVelo(dep))
        print()
        print(dep)
        print()
