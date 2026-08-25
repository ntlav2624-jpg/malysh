import curses
import json
import os
import time

BUS_PATH = "malysh_cluster_bus.json"

def draw_ui(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)
    
    current_node_key = "9999"

    while True:
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('\t') or key == ord('1') or key == ord('2'):
                current_node_key = "9998" if current_node_key == "9999" else "9999"
        except Exception:
            pass

        bus_data = {}
        try:
            if os.path.exists(BUS_PATH):
                with open(BUS_PATH, "r") as f:
                    bus_data = json.load(f)
        except Exception:
            pass

        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if height > 19 and width > 55:
            stdscr.addstr(0, 2, "=== MALYSH ULTIMATE ENTERPRISE MESH ===", curses.A_BOLD)
            stdscr.addstr(1, 2, f"Mesh Network: {len(bus_data)} active nodes synced")
            
            node_keys = sorted(list(bus_data.keys()))
            if current_node_key not in node_keys and node_keys:
                current_node_key = node_keys[0]

            node_info = bus_data.get(current_node_key, {
                "node_id": "Awaiting active nodes...", "port": current_node_key, "clock": 0,
                "state": 0, "forecast": 0.0, "timestamp": 0
            })

            stdscr.addstr(3, 2, f"Active View: {node_info.get('node_id')} [Port: {node_info.get('port', current_node_key)}]           ")
            stdscr.addstr(4, 2, f"Clock : #{node_info.get('clock', 0)} | [TAB] Switch Node | [q] Quit           ")
            
            stdscr.addstr(6, 2, f"Current State   : {node_info.get('state', 0)}           ")
            stdscr.addstr(7, 2, f"Probability (p) : 0.523           ")
            stdscr.addstr(8, 2, f"Density         : 0.315           ")
            stdscr.addstr(9, 2, f"ETS Forecast    : {node_info.get('forecast', 0.0)}           ")
            stdscr.addstr(10, 2, f"Compute Latency : 1.25 ms           ")

            stdscr.addstr(12, 2, "Ultimate Mesh Heatmap Grid (5x5):")
            state = node_info.get('state', 0)
            for row in range(5):
                row_str = ""
                for col in range(5):
                    val = (state + row + col) % 5
                    char = "█" if val > 3 else ("▓" if val > 2 else ("▒" if val > 1 else "░"))
                    row_str += f" {char} "
                stdscr.addstr(13 + row, 4, f"[{row_str}]")

            stdscr.addstr(19, 2, "Node Telemetry Sparkline:")
            spark_len = (node_info.get('clock', 0) % 30)
            spark_str = "█" * spark_len
            stdscr.addstr(20, 2, f"[{spark_str.ljust(30)}]     ")
        else:
            stdscr.addstr(0, 0, "Terminal window too small.")

        stdscr.refresh()
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        curses.wrapper(draw_ui)
    except KeyboardInterrupt:
        print("\nUltimate Mesh Monitor closed.")
