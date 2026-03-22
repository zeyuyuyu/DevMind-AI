# devmind_ai/analyzer.py

import os
import json
import requests
from typing import List, Dict

class SwarmAnalyzer:
    def __init__(self, agents: List[Dict]):
        self.agents = agents
        self.coordination_hub = 'https://devmind-ai.com/coordination'

    def analyze_swarm(self) -> Dict:
        """Analyze the current state of the agent swarm."""
        swarm_data = {
            'agent_count': len(self.agents),
            'active_agents': self.count_active_agents(),
            'resource_usage': self.aggregate_resource_usage(),
            'task_completion': self.assess_task_completion()
        }
        return swarm_data

    def count_active_agents(self) -> int:
        """Count the number of active agents in the swarm."""
        active_agents = 0
        for agent in self.agents:
            if agent['status'] == 'active':
                active_agents += 1
        return active_agents

    def aggregate_resource_usage(self) -> Dict:
        """Aggregate resource usage across the agent swarm."""
        total_cpu = 0
        total_memory = 0
        for agent in self.agents:
            total_cpu += agent['cpu_usage']
            total_memory += agent['memory_usage']
        return {
            'total_cpu': total_cpu,
            'total_memory': total_memory
        }

    def assess_task_completion(self) -> Dict:
        """Assess the overall task completion rate of the agent swarm."""
        total_tasks = 0
        completed_tasks = 0
        for agent in self.agents:
            total_tasks += agent['total_tasks']
            completed_tasks += agent['completed_tasks']
        task_completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'task_completion_rate': task_completion_rate
        }

    def coordinate_swarm(self) -> None:
        """Coordinate the agent swarm based on the analysis."""
        swarm_data = self.analyze_swarm()
        response = requests.post(self.coordination_hub, json=swarm_data)
        if response.status_code == 200:
            print('Swarm coordination successful.')
        else:
            print('Swarm coordination failed.')
