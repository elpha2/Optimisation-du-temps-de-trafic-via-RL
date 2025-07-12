import gymnasium as gym
import numpy as np
import traci
import sumolib
import os


class SumoEnvironment(gym.Env):
    """
    Classe définissant l'environnement SUMO pour l'apprentissage par renforcement,
    conformément à l'interface de Gymnasium.
    """

    # On ajoute 'binary' comme argument avec 'sumo' comme valeur par défaut
    def __init__(self, sumocfg_file, tls_id, detector_ids, num_phases, binary='sumo'):
        super().__init__()

        self.sumocfg_file = sumocfg_file
        self.tls_id = tls_id
        self.detector_ids = detector_ids
        self.num_phases = num_phases
        self.traci_is_active = False
        # La classe utilise maintenant l'argument 'binary' pour choisir le bon exécutable
        self.SUMO_BINARY = sumolib.checkBinary(binary)

        self.action_space = gym.spaces.Discrete(2)
        num_detectors = len(self.detector_ids)
        self.observation_space = gym.spaces.Box(
            low=0,
            high=np.inf,
            shape=(num_detectors + 1,),
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        if self.traci_is_active:
            traci.close()
            self.traci_is_active = False

        # Utilise la variable SUMO_BINARY définie dans __init__
        sumo_cmd = [self.SUMO_BINARY, "-c", self.sumocfg_file, "--no-warnings", "true", "--time-to-teleport", "-1"]

        traci.start(sumo_cmd)
        self.traci_is_active = True

        initial_state = self._get_state()
        return initial_state, {}

    def step(self, action):
        if action == 1:
            current_phase_index = traci.trafficlight.getPhase(self.tls_id)
            next_phase_index = (current_phase_index + 2) % (self.num_phases * 2)
            traci.trafficlight.setPhase(self.tls_id, next_phase_index)

        for _ in range(5):
            traci.simulationStep()

        current_state = self._get_state()
        reward = self._calculate_reward()

        terminated = traci.simulation.getMinExpectedNumber() == 0
        truncated = False

        return current_state, reward, terminated, truncated, {}

    def _get_state(self):
        state = []
        for det_id in self.detector_ids:
            lane_id = traci.inductionloop.getLaneID(det_id)
            halting_vehicles = traci.lane.getLastStepHaltingNumber(lane_id)
            state.append(halting_vehicles)

        current_phase_index = traci.trafficlight.getPhase(self.tls_id)
        state.append(current_phase_index // 2)

        return np.array(state, dtype=np.float32)

    def _calculate_reward(self):
        total_waiting_time = 0
        for lane_id in self._get_controlled_lanes():
            total_waiting_time += traci.lane.getWaitingTime(lane_id)

        return -total_waiting_time

    def _get_controlled_lanes(self):
        return list(set(traci.trafficlight.getControlledLanes(self.tls_id)))

    def close(self):
        if self.traci_is_active:
            traci.close()
            self.traci_is_active = False
