# devmind_ai/analyzer.py
import numpy as np
from collections import defaultdict

class MultiAgentSwarmAnalyzer:
    def __init__(self, agent_states):
        self.agent_states = agent_states
        self.agent_clusters = self.cluster_agents()
        self.cluster_metrics = self.analyze_clusters()

    def cluster_agents(self):
        agent_clusters = defaultdict(list)
        for agent_id, state in self.agent_states.items():
            cluster_id = self.assign_cluster(state)
            agent_clusters[cluster_id].append(agent_id)
        return agent_clusters

    def assign_cluster(self, agent_state):
        # Implement clustering algorithm based on agent state
        # e.g., k-means, DBSCAN, etc.
        cluster_id = hash(tuple(agent_state.values())) % 10
        return cluster_id

    def analyze_clusters(self):
        cluster_metrics = {}
        for cluster_id, agent_ids in self.agent_clusters.items():
            cluster_metrics[cluster_id] = {
                'size': len(agent_ids),
                'centroid': self.calculate_centroid(agent_ids),
                'dispersion': self.calculate_dispersion(agent_ids)
            }
        return cluster_metrics

    def calculate_centroid(self, agent_ids):
        states = [self.agent_states[agent_id] for agent_id in agent_ids]
        return np.mean(states, axis=0)

    def calculate_dispersion(self, agent_ids):
        states = [self.agent_states[agent_id] for agent_id in agent_ids]
        return np.std(states, axis=0)

    def get_cluster_metrics(self):
        return self.cluster_metrics
