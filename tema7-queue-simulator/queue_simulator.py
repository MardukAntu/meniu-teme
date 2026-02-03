#!/usr/bin/env python3
import argparse
import heapq
import math
import os
import random
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional, Dict


# -------------------- helpers --------------------
def ensure_reports_dir() -> None:
    os.makedirs("reports", exist_ok=True)


def report_path(prefix: str = "queue_report") -> str:
    ensure_reports_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join("reports", f"{prefix}_{ts}.txt")


def exp_time(rate: float) -> float:
    """Exponential inter-arrival / service time with rate (lambda or mu). Mean = 1/rate."""
    if rate <= 0:
        raise ValueError("Rate must be > 0")
    return random.expovariate(rate)


def pct(values: List[float], p: float) -> float:
    """Percentile p in [0..100] (simple nearest-rank-ish)."""
    if not values:
        return 0.0
    s = sorted(values)
    k = (p / 100.0) * (len(s) - 1)
    lo = int(math.floor(k))
    hi = int(math.ceil(k))
    if lo == hi:
        return s[lo]
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


# -------------------- simulation model --------------------
@dataclass
class Client:
    id: int
    arrival: float
    service_start: float = 0.0
    service_end: float = 0.0

    @property
    def wait(self) -> float:
        return self.service_start - self.arrival

    @property
    def system_time(self) -> float:
        return self.service_end - self.arrival


@dataclass
class SimResult:
    counters: int
    clients: int
    arrival_rate: float
    service_rate: float
    total_time: float
    avg_wait: float
    max_queue: int
    served: int
    utilization: float
    waits: List[float]
    queue_max_times: List[Tuple[float, int]]  # (time, queue_len)


def simulate_queue(
    clients: int,
    arrival_rate: float,
    service_rate: float,
    counters: int = 1,
    viz: bool = False,
    viz_duration: float = 60.0,
) -> SimResult:
    """
    Discrete-event simulation for M/M/c with FCFS queue.
    Events:
      - next arrival time (generated)
      - service completions (one per busy server; we track next completion per server via heap)
    """
    if counters < 1:
        raise ValueError("counters must be >= 1")
    if clients < 1:
        raise ValueError("clients must be >= 1")
    if arrival_rate <= 0 or service_rate <= 0:
        raise ValueError("rates must be > 0")

    # State
    t = 0.0
    next_arrival = exp_time(arrival_rate)

    queue: List[Client] = []
    # heap of (finish_time, server_index)
    busy_heap: List[Tuple[float, int]] = []
    free_servers = list(range(counters))  # indices of free servers

    served = 0
    client_id = 0

    waits: List[float] = []
    max_queue = 0
    queue_max_times: List[Tuple[float, int]] = []

    # Utilization tracking: sum of busy time across all servers / (counters * total_time)
    # We accumulate busy time as we schedule services.
    busy_time_sum = 0.0

    # Optional viz (time-compressed). We display only if user asked.
    viz_start_wall = time.time()

    def viz_print(now: float) -> None:
        nonlocal viz_start_wall
        if not viz:
            return
        # stop viz after duration seconds (wall clock)
        if time.time() - viz_start_wall > viz_duration:
            return
        # queue bar
        qlen = len(queue)
        busy = len(busy_heap)
        bar_q = "█" * min(qlen, 40)
        bar_b = "▓" * min(busy, 40)
        print(f"t={now:7.2f} | queue={qlen:3d} {bar_q:<40} | busy={busy:2d} {bar_b}")

    # Main loop: simulate until we have served all clients
    while served < clients:
        # Next completion event time
        next_completion = busy_heap[0][0] if busy_heap else float("inf")

        # Decide next event
        if next_arrival <= next_completion and client_id < clients:
            # ARRIVAL
            t = next_arrival
            client_id += 1
            c = Client(id=client_id, arrival=t)
            queue.append(c)

            # update max queue
            if len(queue) > max_queue:
                max_queue = len(queue)
                queue_max_times.append((t, max_queue))

            viz_print(t)

            # schedule next arrival
            next_arrival = t + exp_time(arrival_rate)

        else:
            # COMPLETION
            t, server_idx = heapq.heappop(busy_heap)
            served += 1
            free_servers.append(server_idx)
            viz_print(t)

        # After each event: assign service to free servers as long as queue not empty
        while free_servers and queue:
            server_idx = free_servers.pop()
            c = queue.pop(0)
            c.service_start = t
            service_time = exp_time(service_rate)
            c.service_end = t + service_time

            busy_time_sum += service_time
            waits.append(c.wait)

            heapq.heappush(busy_heap, (c.service_end, server_idx))

            viz_print(t)

    total_time = t
    avg_wait = statistics.mean(waits) if waits else 0.0
    utilization = (busy_time_sum / (counters * total_time)) if total_time > 0 else 0.0

    return SimResult(
        counters=counters,
        clients=clients,
        arrival_rate=arrival_rate,
        service_rate=service_rate,
        total_time=total_time,
        avg_wait=avg_wait,
        max_queue=max_queue,
        served=served,
        utilization=utilization,
        waits=waits,
        queue_max_times=queue_max_times,
    )


# -------------------- reporting --------------------
def format_result(res: SimResult) -> str:
    lines = []
    lines.append(f"Simulare completă pentru {res.clients} clienți:")
    lines.append(f"  Ghișee: {res.counters}")
    lines.append(f"  Rată sosire (lambda): {res.arrival_rate}")
    lines.append(f"  Rată servire (mu): {res.service_rate}")
    lines.append(f"  Timp mediu așteptare: {res.avg_wait:.2f} minute")
    lines.append(f"  Congestie maximă: {res.max_queue} clienți în coadă")
    lines.append(f"  Clienți serviți: {res.served}")
    lines.append(f"  Timp total simulare: {res.total_time:.2f} minute")
    lines.append(f"  Eficiență ghișeu (utilization): {100.0*res.utilization:.1f}%")

    if res.waits:
        lines.append("  Statistici așteptare (minute):")
        lines.append(f"    max: {max(res.waits):.2f}")
        lines.append(f"    p50: {pct(res.waits, 50):.2f}")
        lines.append(f"    p90: {pct(res.waits, 90):.2f}")
        lines.append(f"    p95: {pct(res.waits, 95):.2f}")
        lines.append(f"    p99: {pct(res.waits, 99):.2f}")
    return "\n".join(lines)


def write_detailed_report(res: SimResult, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(format_result(res) + "\n\n")
        f.write("Momente congestie maximă (time, queue_len when new max reached):\n")
        for t, q in res.queue_max_times[:50]:
            f.write(f"  t={t:.2f}  q={q}\n")
        f.write("\nDistribuție așteptare (primele 50 valori):\n")
        for w in res.waits[:50]:
            f.write(f"{w:.4f}\n")


# -------------------- compare --------------------
def compare_scenarios(counters_list: List[int], clients: int, arrival_rate: float, service_rate: float) -> None:
    results: Dict[int, SimResult] = {}
    for c in counters_list:
        results[c] = simulate_queue(clients=clients, arrival_rate=arrival_rate, service_rate=service_rate, counters=c)

    print(f"Comparație scenarii ({clients} clienți):")
    for c in counters_list:
        r = results[c]
        print(f"  {c} ghișeu(e): timp mediu {r.avg_wait:.2f} min, congestie max {r.max_queue}, eficiență {100.0*r.utilization:.1f}%")

    # write a report too
    path = report_path("queue_compare")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Comparație scenarii ({clients} clienți)\n")
        f.write(f"arrival_rate={arrival_rate} service_rate={service_rate}\n\n")
        for c in counters_list:
            r = results[c]
            f.write(f"{c} ghișeu(e): avg_wait={r.avg_wait:.4f} max_queue={r.max_queue} util={r.utilization:.4f} total={r.total_time:.2f}\n")
    print(f"\nRaport comparație salvat în {path}")


# -------------------- CLI --------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="queue_simulator")

    p.add_argument("--clients", type=int, default=100)
    p.add_argument("--arrival_rate", type=float, default=0.3)
    p.add_argument("--service_rate", type=float, default=0.5)

    p.add_argument("--multi_queues", type=int, default=None, help="număr ghișee (paralel)")
    p.add_argument("--compare", type=str, default=None, help='ex: "1,2,3" compară ghișee')
    p.add_argument("--report", type=str, default=None, help="detailed | none")
    p.add_argument("--seed", type=int, default=None)

    p.add_argument("--viz", action="store_true", help="vizualizare text în timp real (opțional)")
    p.add_argument("--duration", type=float, default=60.0, help="durata viz (secunde wall-clock)")

    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    counters = args.multi_queues if args.multi_queues is not None else 1

    if args.compare:
        counters_list = [int(x.strip()) for x in args.compare.split(",") if x.strip()]
        compare_scenarios(counters_list, clients=args.clients, arrival_rate=args.arrival_rate, service_rate=args.service_rate)
        return

    res = simulate_queue(
        clients=args.clients,
        arrival_rate=args.arrival_rate,
        service_rate=args.service_rate,
        counters=counters,
        viz=args.viz,
        viz_duration=args.duration,
    )

    print(format_result(res))

    if args.report == "detailed":
        path = report_path("queue_report")
        write_detailed_report(res, path)
        print(f"\nRaport detaliat salvat în {path}")


if __name__ == "__main__":
    main()
