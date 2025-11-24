import random
import pickle
import os
import math

class Agent:
    def choose_action(self, state):
        raise NotImplementedError

    def _choose_weighted_random_action(self):
        """Choose an action randomly but with weights to reduce frequency of jumps/crafting"""
        weights = []
        for action in self.actions:
            if "jump" in action:
                weights.append(0.00) # Very low probability for jump (5%)
            elif "craft" in action:
                weights.append(0.05) # Very low probability for crafting
            elif "pitch" in action:
                weights.append(0.2)  # Low probability for looking up/down
            else:
                weights.append(1.0)  # Normal probability for move/turn/attack
        return random.choices(self.actions, weights=weights, k=1)[0]

    def learn(self, state, action, reward, next_state, done=False):
        pass
    
    def start_episode(self):
        pass
        
    def end_episode(self):
        pass

    def save_model(self, path):
        """Base implementation: saves a minimal model file."""
        with open(path, 'wb') as f:
            pickle.dump({'type': self.__class__.__name__, 'epsilon': getattr(self, 'epsilon', 1.0)}, f)

    def load_model(self, path):
        """Base implementation: loads a minimal model file."""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
                if 'epsilon' in data and hasattr(self, 'epsilon'):
                    self.epsilon = data['epsilon']

class RandomAgent(Agent):
    def __init__(self, actions):
        self.actions = actions
        self.epsilon = 1.0 # Just for logging compatibility

    def choose_action(self, state):
        return self._choose_weighted_random_action()

class QLearningAgent(Agent):
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.q_table = {}

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return self._choose_weighted_random_action()
        
        q_values = [self.get_q(state, a) for a in self.actions]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(self.actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state, done=False):
        current_q = self.get_q(state, action)
        max_next_q = max([self.get_q(next_state, a) for a in self.actions]) if not done else 0
        
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(state, action)] = new_q

    def end_episode(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def save_model(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load_model(self, path):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.q_table = pickle.load(f)

class SarsaAgent(QLearningAgent):
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        super().__init__(actions, alpha, gamma, epsilon, epsilon_decay, min_epsilon)
        self.next_action = None

    def choose_action(self, state):
        # In SARSA, we might need to choose the action for the next step ahead of time
        # But typically in a loop: choose A, take A, observe R, S', choose A', update Q(S,A) using Q(S',A')
        # So standard choose_action is fine, but learn needs the next action.
        # We will modify learn to take next_action as an argument or handle it differently.
        # For simplicity in the main loop compatibility, we'll stick to the standard choose_action
        # and let the learn method handle the logic if passed next_action, OR
        # we assume the main loop calls choose_action for S' before calling learn.
        # However, to keep the main loop generic, we can store the next action if needed, 
        # but standard SARSA requires A' to be chosen by the policy.
        return super().choose_action(state)

    def learn(self, state, action, reward, next_state, next_action=None, done=False):
        # This signature differs slightly from Q-Learning if we want true SARSA
        # If next_action is not provided, we must choose it here (but not execute it yet? No, that breaks the loop)
        # The calling loop should provide next_action for SARSA.
        # If next_action is None, we can't do SARSA update properly without picking it.
        if next_action is None and not done:
            next_action = self.choose_action(next_state)
            
        current_q = self.get_q(state, action)
        next_q = self.get_q(next_state, next_action) if not done else 0
        
        new_q = current_q + self.alpha * (reward + self.gamma * next_q - current_q)
        self.q_table[(state, action)] = new_q
        return next_action # Return it so the loop can use it if it wants

class ExpectedSarsaAgent(QLearningAgent):
    def learn(self, state, action, reward, next_state, done=False):
        current_q = self.get_q(state, action)
        
        if done:
            expected_next_q = 0
        else:
            # Calculate expected value over all actions
            q_values = [self.get_q(next_state, a) for a in self.actions]
            max_q = max(q_values)
            greedy_actions = [a for a, q in zip(self.actions, q_values) if q == max_q]
            non_greedy_prob = self.epsilon / len(self.actions)
            greedy_prob = ((1 - self.epsilon) / len(greedy_actions)) + non_greedy_prob
            
            expected_next_q = 0
            for a in self.actions:
                prob = greedy_prob if a in greedy_actions else non_greedy_prob
                expected_next_q += prob * self.get_q(next_state, a)

        new_q = current_q + self.alpha * (reward + self.gamma * expected_next_q - current_q)
        self.q_table[(state, action)] = new_q

class DoubleQLearningAgent(Agent):
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.q1_table = {}
        self.q2_table = {}

    def get_q(self, state, action, table=1):
        if table == 1:
            return self.q1_table.get((state, action), 0.0)
        else:
            return self.q2_table.get((state, action), 0.0)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return self._choose_weighted_random_action()
        
        # Use sum of Q1 and Q2
        q_values = [self.get_q(state, a, 1) + self.get_q(state, a, 2) for a in self.actions]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(self.actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state, done=False):
        if random.random() < 0.5:
            # Update Q1
            current_q1 = self.get_q(state, action, 1)
            if done:
                max_next_q2 = 0
            else:
                # Argmax Q1
                q1_next_values = [self.get_q(next_state, a, 1) for a in self.actions]
                max_q1 = max(q1_next_values)
                best_actions = [a for a, q in zip(self.actions, q1_next_values) if q == max_q1]
                best_action = random.choice(best_actions)
                # Value from Q2
                max_next_q2 = self.get_q(next_state, best_action, 2)
            
            new_q1 = current_q1 + self.alpha * (reward + self.gamma * max_next_q2 - current_q1)
            self.q1_table[(state, action)] = new_q1
        else:
            # Update Q2
            current_q2 = self.get_q(state, action, 2)
            if done:
                max_next_q1 = 0
            else:
                # Argmax Q2
                q2_next_values = [self.get_q(next_state, a, 2) for a in self.actions]
                max_q2 = max(q2_next_values)
                best_actions = [a for a, q in zip(self.actions, q2_next_values) if q == max_q2]
                best_action = random.choice(best_actions)
                # Value from Q1
                max_next_q1 = self.get_q(next_state, best_action, 1)
            
            new_q2 = current_q2 + self.alpha * (reward + self.gamma * max_next_q1 - current_q2)
            self.q2_table[(state, action)] = new_q2

    def end_episode(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def save_model(self, path):
        with open(path, 'wb') as f:
            pickle.dump((self.q1_table, self.q2_table), f)

    def load_model(self, path):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.q1_table, self.q2_table = pickle.load(f)

class MonteCarloAgent(Agent):
    def __init__(self, actions, gamma=0.9, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        self.actions = actions
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.q_table = {}
        self.returns = {} # (state, action) -> [returns]
        self.episode_memory = [] # (state, action, reward)

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return self._choose_weighted_random_action()
        
        q_values = [self.get_q(state, a) for a in self.actions]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(self.actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state, done=False):
        # Store experience
        self.episode_memory.append((state, action, reward))

    def end_episode(self):
        G = 0
        # Iterate backwards
        for state, action, reward in reversed(self.episode_memory):
            G = self.gamma * G + reward
            
            # First-visit MC (simplified: we just update every time for now or check if first visit)
            # For true first-visit, we need to check if (state, action) appeared earlier in this episode
            # Here we'll do every-visit for simplicity or just append
            if (state, action) not in self.returns:
                self.returns[(state, action)] = []
            self.returns[(state, action)].append(G)
            
            # Update Q as average of returns
            self.q_table[(state, action)] = sum(self.returns[(state, action)]) / len(self.returns[(state, action)])

        self.episode_memory = []
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def save_model(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load_model(self, path):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.q_table = pickle.load(f)
