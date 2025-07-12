import traci
import sumolib
import time

# --- Configuration du test ---
SUMOCFG_FILE = "map.sumo.cfg"
SUMO_BINARY = sumolib.checkBinary('sumo-gui')

# --- Lancement du test ---
try:
    print("--- Tentative de lancement de sumo-gui ---")
    
    # Commande pour lancer SUMO avec l'interface graphique
    sumo_cmd = [SUMO_BINARY, "-c", SUMOCFG_FILE]
    
    # Lancement de la simulation
    traci.start(sumo_cmd)
    
    print("--- Connexion à sumo-gui réussie ! ---")
    
    # On laisse la simulation tourner 10 secondes pour observer
    for _ in range(10):
        traci.simulationStep()
        time.sleep(1)

except Exception as e:
    print(f"ERREUR : Impossible de lancer sumo-gui. Voici l'erreur :")
    print(e)

finally:
    # Fermeture de la connexion
    if traci.isEmbedded():
        traci.close()
    print("--- Test terminé ---")

