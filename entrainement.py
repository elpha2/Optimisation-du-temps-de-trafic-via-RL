from environnement_rl import SumoEnvironment
from stable_baselines3 import DQN
import os

# --- CONFIGURATION DU PROJET ---

# 1. Nom de votre fichier de configuration SUMO
SUMOCFG_FILE = "map.sumo.cfg"

# 2. ID du feu tricolore à contrôler
#    (Vérifié à partir de votre capture d'écran netedit)
TLS_ID = "1130788693" 

# 3. Liste des ID de vos détecteurs (CORRIGÉE pour correspondre aux voies existantes)
DETECTOR_IDS = [
    "det_1106620641_2_0",
    "det_1106620641_2_1",
    "det_248378000_9_0",
    "det_248378000_9_1",
    "det_315929406_3_0",    # La voie _1 a été supprimée car elle n'existe pas
    "det_420659193_1_0",
    "det_420659193_1_1",
    "det_neg215666786_0_0" # La voie _1 a été supprimée car elle n'existe pas
]

# 4. Nombre de phases VERTES distinctes de votre feu

NUM_PHASES = 10


# --- SCRIPT D'ENTRAÎNEMENT ---

if __name__ == '__main__':
    # Création de l'environnement
    env = SumoEnvironment(
        sumocfg_file=SUMOCFG_FILE, 
        tls_id=TLS_ID, 
        detector_ids=DETECTOR_IDS,
        num_phases=NUM_PHASES
    )

    # Création du modèle d'agent RL (Deep Q-Network)
    # "MlpPolicy" signifie que l'agent utilisera un réseau de neurones standard.
    model = DQN(
        "MlpPolicy", 
        env, 
        verbose=1,
        learning_rate=0.0005,
        buffer_size=50000,
        learning_starts=1000,
        train_freq=(1, "step"),
    )

    # Lancement de l'entraînement
    # L'agent va interagir avec la simulation pendant 20 000 pas de temps.
    # Pour un vrai projet, ce nombre devrait être beaucoup plus élevé.
    model.learn(total_timesteps=20000)

    # Sauvegarde du modèle entraîné
    model.save("dqn_sumo_model")

    print("\n--- Entraînement terminé et modèle sauvegardé sous 'dqn_sumo_model.zip' ---")

    env.close()
