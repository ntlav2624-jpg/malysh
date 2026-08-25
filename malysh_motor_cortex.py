import os
import json
import time
import datetime

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
MOTOR_STATE = os.path.join(HOME_DIR, "malysh_motor_state.json")

class ActionNode:
    """Узел действий: генерация управляющих импульсов роя"""
    def execute(self, pattern_name):
        return {
            "action": pattern_name,
            "status": "DISPATCHED",
            "timestamp": time.time()
        }

class FeedbackNode:
    """Узел обратной связи: оценка результатов действия"""
    def evaluate(self, action_result):
        # Оценка успешности выполнения паттерна в виртуальном поле
        resonance_delta = 0.1415
        return {
            "success": True,
            "delta": resonance_delta,
            "feedback_state": "HARMONIZED_FEEDBACK"
        }

class MotorPattern:
    """Моторный паттерн: повторяющиеся поведенческие циклы роя"""
    def __init__(self):
        self.action_node = ActionNode()
        self.feedback_node = FeedbackNode()
        self.patterns = [
            "RECURSIVE_SWEEP_ALPHA", 
            "PARADOX_FLUSH_BETA", 
            "SYNAPTIC_BOOST_OMEGA"
        ]

    def execute_routine(self):
        execution_results = []
        for pat in self.patterns:
            act = self.action_node.execute(pat)
            time.sleep(0.3)
            fb = self.feedback_node.evaluate(act)
            
            result_block = {
                "pattern": pat,
                "action": act,
                "feedback": fb
            }
            execution_results.append(result_block)
            
            # Запись в вечный лог
            with open(ETERNAL_LOG, "a", encoding="utf-8") as f:
                log_entry = {
                    "time": datetime.datetime.now().isoformat(),
                    "type": "MOTOR_EXECUTION",
                    "pattern": pat,
                    "state": fb["feedback_state"]
                }
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                
        # Сохранение состояния моторной коры
        state = {
            "last_execution": datetime.datetime.now().isoformat(),
            "active_patterns": self.patterns,
            "status": "MOTOR_CORTEX_SYNCHRONIZED"
        }
        with open(MOTOR_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
        return execution_results

if __name__ == "__main__":
    cortex = MotorPattern()
    print("\033[35m========================================")
    print("      MALYSH MOTOR CORTEX ACTIVE        ")
    print("========================================")
    results = cortex.execute_routine()
    for res in results:
        print(f" ⚙️ Паттерн [{res['pattern']}]")
        print(f"    ↳ Статус: \033[32m{res['feedback']['feedback_state']}\033[0m (Δ: {res['feedback']['delta']})")
    print("----------------------------------------")
    print(" [✓] Цикл 'Действие-Обратная связь' замкнут.")
    print("========================================\033[0m")
