import time
from environnement_rl import SumoEnvironment
from stable_baselines3 import DQN

# --- CONFIGURATION DE L'ÉVALUATION ---

# 1. Nom de votre fichier de configuration SUMO
SUMOCFG_FILE = "map.sumo.cfg"

# 2. ID du feu tricolore que vous contrôlez
TLS_ID = "1130788693"

# 3. Liste complète des ID de vos détecteurs
DETECTOR_IDS = [
    "det_1106620641_2_0",
    "det_1106620641_2_1",
    "det_248378000_9_0",
    "det_248378000_9_1",
    "det_315929406_3_0",
    "det_420659193_1_0",
    "det_420659193_1_1",
    "det_neg215666786_0_0"
]

# 4. Nombre de phases VERTES distinctes de votre feu
NUM_PHASES = 10

# 5. Chemin vers votre modèle sauvegardé
MODEL_PATH = "dqn_sumo_model.zip"

# --- SCRIPT D'ÉVALUATION ---

if __name__ == '__main__':
    # Création de l'environnement, en lui spécifiant de se lancer avec la GUI
    env = SumoEnvironment(
        sumocfg_file=SUMOCFG_FILE,
        tls_id=TLS_ID,
        detector_ids=DETECTOR_IDS,
        num_phases=NUM_PHASES,
        binary='sumo-gui'  # Cet argument est maintenant correctement géré par la classe SumoEnvironment
    )

    # Chargement du modèle que vous avez entraîné
    model = DQN.load(MODEL_PATH)

    print("--- Lancement de l'évaluation avec le modèle entraîné (avec GUI) ---")

    # Réinitialisation de l'environnement pour une nouvelle simulation
    obs, _ = env.reset()
    done = False
    total_reward = 0

    # Boucle de simulation
    while not done:
        # L'agent choisit la meilleure action possible (deterministic=True)
        # Il n'explore plus, il exploite ce qu'il a appris.
        action, _states = model.predict(obs, deterministic=True)

        # L'environnement exécute l'action et retourne le nouvel état et la récompense
        obs, reward, terminated, truncated, info = env.step(action)

        total_reward += reward
        done = terminated or truncated

        # Petite pause pour pouvoir suivre la simulation visuellement
        time.sleep(0.05)

    print(f"--- Évaluation terminée ---")
    print(f"Récompense totale obtenue par l'agent : {total_reward:.2f}")

    # Fermeture propre de l'environnement
    env.close()
