import math
import random

class ProbabilitySpace:
    def __init__(self, omega_samples):
        self.omega = omega_samples

    def probability(self, event_condition):
        favorable = sum(1 for w in self.omega if event_condition(w))
        return favorable / len(self.omega) if self.omega else 0.0

    def expectation(self, random_variable):
        if not self.omega:
            return 0.0
        return sum(random_variable(w) for w in self.omega) / len(self.omega)

class ResonanceProbability:
    def __init__(self, theta=0.82, entropy_s=0.5):
        self.theta = theta
        self.s = entropy_s

    def energy_functional(self, x):
        return (x - self.theta) ** 2

    def density(self, x):
        return math.exp(-self.s * self.energy_functional(x))

    def sample_resonant(self):
        return random.gauss(self.theta, 0.5)

class GlyphMarkovChain:
    def __init__(self):
        self.states = [0, 1, 2, 3]
        self.transition_matrix = {
            i: {j: 0.25 for j in self.states} for i in self.states
        }
        self.current_state = random.choice(self.states)

    def step(self):
        probs = self.transition_matrix[self.current_state]
        r = random.random()
        acc = 0.0
        next_s = self.current_state
        for s, p in probs.items():
            acc += p
            if r <= acc:
                next_s = s
                break

        self.transition_matrix[self.current_state][next_s] += 0.05
        row_sum = sum(self.transition_matrix[self.current_state].values())
        for s in self.states:
            self.transition_matrix[self.current_state][s] /= row_sum

        self.current_state = next_s
        return self.current_state

class EvolutionaryMeasure:
    def __init__(self, initial_theta=0.82):
        self.theta = initial_theta

    def update_measure(self, fact, prediction):
        err = fact - prediction
        self.theta += 0.02 * err
        return self.theta

if __name__ == "__main__":
    print("--- Инициализация Малыша: Операторное стохастическое ядро R10 ---")
    omega = [random.uniform(0.0, 10.0) for _ in range(100)]
    p_space = ProbabilitySpace(omega)

    res_prob = ResonanceProbability(theta=0.82, entropy_s=0.4)
    glyph_mc = GlyphMarkovChain()
    evo = EvolutionaryMeasure(initial_theta=0.82)

    current_pred = 5.0

    for step_i in range(1, 6):
        fact = res_prob.sample_resonant()
        new_theta = evo.update_measure(fact, current_pred)
        res_prob.theta = new_theta
        glyph = glyph_mc.step()
        exp_val = p_space.expectation(lambda w: w * new_theta)

        print(f"Шаг {step_i} | Факт: {fact:.2f} | Theta: {new_theta:.3f} | Глиф (Σ): {glyph} | E[X]: {exp_val:.2f}")
        current_pred = fact
