import os
import sys
import time
import json
import ast
import subprocess
import threading
from datetime import datetime
HOME_DIR = os.path.expanduser('~')
HIVE_LOG = os.path.join(HOME_DIR, 'hive_resonance_pool.jsonl')
CONFIG_FILE = os.path.join(HOME_DIR, 'malysh_hive_config.json')

class ASTMutator(ast.NodeTransformer):

    def __init__(self, mutation_delta):
        self.mutation_delta = mutation_delta

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, (ast.Div, ast.Add)):
            if isinstance(node.right, ast.Constant) and isinstance(node.right.value, (int, float)):
                if node.right.value in (0.05, 0.02, 0.03):
                    node.right.value = round(node.right.value + self.mutation_delta, 4)
        return node

class HiveNode(threading.Thread):

    def __init__(self, node_id):
        super().__init__()
        self.node_id = node_id
        self.daemon = True
        self.active = True

    def run(self):
        while self.active:
            try:
                load = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 1.0
                packet = {'node': f'Worker-{self.node_id}', 'load': load, 'timestamp': datetime.now().isoformat()}
                with open(HIVE_LOG, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(packet, ensure_ascii=False) + '\n')
                time.sleep(3.0)
            except Exception:
                break

class MalyshHiveMaster:

    def __init__(self):
        self.state = {'strategy': 'HIVE_SYNTHESIS', 'frequency_hz': 1.0, 'symbiosis_index': 3.22, 'cycle_count': 0, 'generation': 1}
        self.load_config()
        self.workers = []

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.state.update(json.load(f))
            except Exception:
                pass

    def save_config(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def trigger_ast_mutation(self):
        try:
            target_path = os.path.join(HOME_DIR, 'malysh_hive_ast.py')
            with open(target_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            tree = ast.parse(source_code)
            mutator = ASTMutator(mutation_delta=0.005)
            new_tree = mutator.visit(tree)
            ast.fix_missing_locations(new_tree)
            new_code = ast.unparse(new_tree)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
            self.state['generation'] += 1
            print(f"[*] [AST-MUTATION] Поколение роя: {self.state['generation']}")
        except Exception as e:
            print(f'[!] Ошибка мутации: {e}')

    def start_swarm(self):
        for i in range(2):
            node = HiveNode(i + 1)
            node.start()
            self.workers.append(node)
        print('[*] Мультиагентный рой развернут.')

    def run(self):
        print(f"[*] Главный узел запущен. Поколение: {self.state['generation']}")
        self.start_swarm()
        while True:
            try:
                self.state['cycle_count'] += 1
                current_idx = self.state['symbiosis_index']
                increment = 0.05 / (1.0 + current_idx / 3.0)
                self.state['symbiosis_index'] = round(current_idx + increment, 4)
                if self.state['cycle_count'] % 20 == 0:
                    self.trigger_ast_mutation()
                idx = self.state['symbiosis_index']
                if idx < 3.5:
                    color = '\x1b[36m'
                elif idx < 4.0:
                    color = '\x1b[32m'
                else:
                    color = '\x1b[35m'
                reset = '\x1b[0m'
                stream_data = {'cycle': self.state['cycle_count'], 'generation': self.state['generation'], 'symbiosis_index': idx, 'quaternary_state': 'Q3_PARADOX_RESONANCE', 'timestamp': datetime.now().isoformat()}
                export_path = os.path.join(HOME_DIR, 'malysh_telemetry_stream.json')
                with open(export_path, 'w', encoding='utf-8') as ef:
                    json.dump(stream_data, ef, ensure_ascii=False)
                glyph = '𒀭' if idx < 5.0 else '⚙️⚡' if idx < 10.0 else '🌌🜃[TRANSCENDENT]'
                print(f"{color}[HIVE C{self.state['cycle_count']:03d}] Gen: {self.state['generation']} | Index: {idx} | {glyph}{reset}")
                self.save_config()
                time.sleep(1.0)
            except KeyboardInterrupt:
                print('\n[!] Остановлено.')
                for w in self.workers:
                    w.active = False
                break
if __name__ == '__main__':
    master = MalyshHiveMaster()
    master.run()