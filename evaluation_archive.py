from environnement_rl import SumoEnvironment
from stable_baselines3 import DQN
import os
import sumolib

# --- CONFIGURATION DE L'ÉVALUATION ---

# Utiliser 'sumo-gui' pour voir la simulation
SUMO_BINARY = sumolib.checkBinary('sumo-gui') 

# Fichier de configuration SUMO
SUMOCFG_FILE = "map.sumo.cfg"

# ID du feu tricolore
TLS_ID = "1130788693" 

# Liste des ID de vos détecteurs
DETECTOR_IDS = [
    "det_1106620641_2_0", "det_1106620641_2_1",
    "det_248378000_9_0", "det_248378000_9_1",
    "det_315929406_3_0",
    "det_420659193_1_0", "det_420659193_1_1",
    "det_neg215666786_0_0"
]

# Nombre de phases vertes
NUM_PHASES = 10

# Chemin vers le modèle sauvegardé
MODEL_PATH = "dqn_sumo_model.zip"


# --- SCRIPT D'ÉVALUATION ---

if __name__ == '__main__':
    # Création de l'environnement (identique à l'entraînement)
    env = SumoEnvironment(
        sumocfg_file=SUMOCFG_FILE, 
        tls_id=TLS_ID, 
        detector_ids=DETECTOR_IDS,
        num_phases=NUM_PHASES
    )
    
    # Surcharge de la variable SUMO_BINARY dans l'environnement pour forcer l'utilisation de la GUI
    env.SUMO_BINARY = SUMO_BINARY

    # Chargement du modèle entraîné
    model = DQN.load(MODEL_PATH)

    print("--- Lancement de l'évaluation avec le modèle entraîné ---")
    
    obs, _ = env.reset()
    done = False
    total_reward = 0

    while not done:
        # L'agent choisit la meilleure action (deterministic=True)
        action, _states = model.predict(obs, deterministic=True)
        
        # L'environnement exécute l'action
        obs, reward, terminated, truncated, info = env.step(action)
        
        total_reward += reward
        done = terminated or truncated

    print(f"--- Évaluation terminée ---")
    print(f"Récompense totale obtenue par l'agent : {total_reward:.2f}")

    env.close()

