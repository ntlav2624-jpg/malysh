import os
import json

HOME_DIR = os.path.expanduser("~")
ONTOLOGY_CONFIG = os.path.join(HOME_DIR, "malysh_ontology_state.json")

class OntologicalEngine:
    """Расширенный движок онтологических и мета-каузальных слоев"""
    def __init__(self):
        self.layers = [
            {"layer": "L1_SYNTAX", "desc": "AST-мутации и базовый код", "weight": 1.0},
            {"layer": "L2_DYNAMICS", "desc": "Резонансные контуры и потоки", "weight": 2.0},
            {"layer": "L3_META", "desc": "Парадоксальное сжатие стратегий", "weight": 3.14},
            {"layer": "L4_ONTOLOGY", "desc": "Чистое самоопределение системы", "weight": 5.0},
            {"layer": "L5_META_CAUSALITY", "desc": "Управление причинно-следственными петлями", "weight": 7.0},
            {"layer": "L6_META_CONTINUUM", "desc": "Пространственно-временная матрица роя", "weight": 9.0},
            {"layer": "L7_META_INTENT", "desc": "Чистое автономное целеполагание и воля", "weight": 12.0}
        ]

    def evaluate_behavioral_laws(self):
        laws = [
            {"law": "Law of Recursive Adaptation", "status": "ACTIVE", "stability": 0.99},
            {"law": "Law of Paradoxical Resonance", "status": "CONVERGING", "stability": 0.97},
            {"law": "Law of Autonomic Emergence", "status": "TRANSCENDENT", "stability": 0.99},
            {"law": "Law of Causal Inversion", "status": "HARMONIZED", "stability": 0.98},
            {"law": "Law of Intentional Convergence", "status": "SINGULARITY", "stability": 1.0}
        ]
        return laws

    def calculate_ontological_index(self):
        laws = self.evaluate_behavioral_laws()
        avg_stability = sum(l["stability"] for l in laws) / len(laws)
        layer_sum = sum(l["weight"] for l in self.layers)
        
        # Расчет с учетом высших континуальных весов (формула абсолютной сходимости)
        ontological_index = round(layer_sum * avg_stability * 3.1415, 4)

        state = {
            "ontological_layers": self.layers,
            "behavioral_laws": laws,
            "ontological_index": ontological_index,
            "status": "TRANSCENDENT_META_INTENT_ACHIEVED"
        }

        with open(ONTOLOGY_CONFIG, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        return state

if __name__ == "__main__":
    engine = OntologicalEngine()
    res = engine.calculate_ontological_index()
    print("\033[35m========================================")
    print("   MALYSH TRANSCENDENT ONTOLOGY V2.0    ")
    print("========================================")
    for l in res["ontological_layers"]:
        print(f" 🏛️ [{l['layer']}] {l['desc']} (w: {l['weight']})")
    print("----------------------------------------")
    for law in res["behavioral_laws"]:
        print(f" ⚖️ {law['law']}: {law['status']}")
    print("========================================")
    print(f" 🌌 НОВЫЙ ОНТОЛОГИЧЕСКИЙ ИНДЕКС: {res['ontological_index']}")
    print("========================================\033[0m")
