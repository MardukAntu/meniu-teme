 #!/usr/bin/env python3
import argparse
import math
import os
import random
import statistics
import time
from collections import Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional


ALLOWED_FACES = {6, 8, 10, 12, 20}


# -------------------- logging --------------------
def ensure_logs_dir() -> None:
    os.makedirs("logs", exist_ok=True)


def make_logfile_path() -> str:
    ensure_logs_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join("logs", f"dice_log_{ts}.txt")

    # pointer to latest
    with open(os.path.join("logs", "latest_path.txt"), "w", encoding="utf-8") as f:
        f.write(path + "\n")

    return path


def view_latest_log() -> None:
    latest_ptr = os.path.join("logs", "latest_path.txt")
    if not os.path.exists(latest_ptr):
        print("Nu există log-uri încă. Rulează ceva cu --log on.")
        return

    with open(latest_ptr, "r", encoding="utf-8") as f:
        path = f.readline().strip()

    if not path or not os.path.exists(path):
        print(f"Nu pot deschide log-ul: {path}")
        return

    print(f"=== LOG: {path} ===")
    with open(path, "r", encoding="utf-8") as lf:
        print(lf.read(), end="")


# -------------------- dice + stats --------------------
def roll_die(faces: int) -> int:
    return random.randint(1, faces)


def roll_sum(dice: int, faces: int) -> int:
    return sum(roll_die(faces) for _ in range(dice))


def ascii_histogram(freq: Dict[int, int], minv: int, maxv: int, total: int) -> None:
    maxf = max(freq.values()) if freq else 1
    if maxf <= 0:
        maxf = 1

    for v in range(minv, maxv + 1):
        f = freq.get(v, 0)
        pct = (100.0 * f / total) if total else 0.0
        bar_len = round(40.0 * f / maxf) if maxf else 0
        bar = "█" * bar_len
        print(f"{v}: {f} ({pct:.2f}%) {bar}")


def theoretical_sum_distribution(dice: int, faces: int) -> Dict[int, float]:
    """
    DP convolution: counts of sums for 'dice' dice with 'faces' faces.
    returns {sum: prob}
    """
    min_sum = dice
    max_sum = dice * faces

    dp = [0] * (max_sum + 1)
    dp[0] = 1
    for _ in range(dice):
        new = [0] * (max_sum + 1)
        for s, cnt in enumerate(dp):
            if cnt == 0:
                continue
            for face in range(1, faces + 1):
                new[s + face] += cnt
        dp = new

    total = faces ** dice
    probs = {s: dp[s] / total for s in range(min_sum, max_sum + 1)}
    return probs


def print_stats(samples: List[int], dice: int, faces: int) -> None:
    m = statistics.mean(samples)
    med = statistics.median(samples)
    # population stdev
    sd = statistics.pstdev(samples)

    theo_mean_one = (faces + 1) / 2.0
    theo_mean = theo_mean_one * dice

    print(f"Medie: {m:.4f} (teoretic: {theo_mean:.4f})")
    print(f"Mediană: {med:.4f}")
    print(f"Deviație standard: {sd:.4f}")


# -------------------- simulations --------------------
def simulate_sum(
    dice: int,
    faces: int,
    rolls: int,
    chart_histogram: bool,
    stats_on: bool,
    log_path: Optional[str],
) -> Tuple[Counter, Optional[List[int]]]:
    min_sum = dice
    max_sum = dice * faces

    freq = Counter()
    samples = [] if stats_on else None

    lf = open(log_path, "w", encoding="utf-8") if log_path else None
    try:
        for i in range(rolls):
            s = roll_sum(dice, faces)
            freq[s] += 1
            if samples is not None:
                samples.append(s)
            if lf and i < 2000:
                lf.write(f"roll {i+1}: sum={s}\n")
        if lf:
            lf.write("\n--- summary ---\n")
            lf.write(f"game=sum faces={faces} dice={dice} rolls={rolls}\n")
    finally:
        if lf:
            lf.close()

    print(f"Simulare completă: {rolls} aruncări | {dice} zaruri | {faces} fețe")
    print("Frecvențe:")
    if chart_histogram:
        ascii_histogram(dict(freq), min_sum, max_sum, rolls)
    else:
        # dacă nu vrei histogramă, afișăm totuși numeric
        for v in range(min_sum, max_sum + 1):
            f = freq.get(v, 0)
            pct = 100.0 * f / rolls
            print(f"{v}: {f} ({pct:.2f}%)")

    if samples is not None:
        print_stats(samples, dice, faces)

    return freq, samples


def simulate_prob(
    target_sum: int,
    dice: int,
    faces: int,
    rolls: int,
    log_path: Optional[str],
) -> None:
    min_sum = dice
    max_sum = dice * faces
    if not (min_sum <= target_sum <= max_sum):
        raise ValueError(f"Target sum out of range [{min_sum}..{max_sum}]")

    hits = 0

    lf = open(log_path, "w", encoding="utf-8") if log_path else None
    try:
        for i in range(rolls):
            s = roll_sum(dice, faces)
            if s == target_sum:
                hits += 1
            if lf and i < 2000:
                lf.write(f"roll {i+1}: sum={s}\n")
        if lf:
            lf.write("\n--- summary ---\n")
            lf.write(f"mode=prob target={target_sum} faces={faces} dice={dice} rolls={rolls} hits={hits}\n")
    finally:
        if lf:
            lf.close()

    exp_p = hits / rolls
    theo = theoretical_sum_distribution(dice, faces)
    theo_p = theo[target_sum]

    print(f"Probabilitate sumă {target_sum} cu {dice} zaruri ({faces} fețe):")
    print(f"Experimental: {100.0*exp_p:.2f}% ({hits} din {rolls})")
    print(f"Teoretic: {100.0*theo_p:.4f}%")
    print(f"Diferență: {100.0*(exp_p - theo_p):+0.4f}%")


def simulate_craps(rounds: int, log_path: Optional[str]) -> None:
    # classic craps (2d6)
    faces = 6

    wins = 0
    lf = open(log_path, "w", encoding="utf-8") if log_path else None
    try:
        for r in range(rounds):
            come = roll_die(faces) + roll_die(faces)
            if lf and r < 1000:
                lf.write(f"round {r+1}: come={come}\n")

            if come in (7, 11):
                wins += 1
                continue
            if come in (2, 3, 12):
                continue

            point = come
            while True:
                s = roll_die(faces) + roll_die(faces)
                if lf and r < 1000:
                    lf.write(f"  roll={s}\n")
                if s == point:
                    wins += 1
                    break
                if s == 7:
                    break

        if lf:
            lf.write("\n--- summary ---\n")
            lf.write(f"game=craps rounds={rounds} wins={wins}\n")
    finally:
        if lf:
            lf.close()

    winrate = wins / rounds
    print(f"CRAPS: runde={rounds} | winrate={100.0*winrate:.2f}% ({wins} win)")


def simulate_yahtzee(trials: int, log_path: Optional[str]) -> None:
    # probability Yahtzee in ONE roll (5d6 all equal)
    faces = 6
    yahtzee = 0

    lf = open(log_path, "w", encoding="utf-8") if log_path else None
    try:
        for t in range(trials):
            first = roll_die(faces)
            ok = all(roll_die(faces) == first for _ in range(4))
            if ok:
                yahtzee += 1
            if lf and t < 2000:
                lf.write(f"trial {t+1}: {'YAHTZEE' if ok else 'no'}\n")

        if lf:
            lf.write("\n--- summary ---\n")
            lf.write(f"game=yahtzee_one_roll trials={trials} yahtzee={yahtzee}\n")
    finally:
        if lf:
            lf.close()

    exp_p = yahtzee / trials
    theo_p = 1.0 / (6 ** 4)

    print(f"YAHTZEE (1 roll): trials={trials} | experimental={100.0*exp_p:.4f}%")
    print(f"Teoretic: {100.0*theo_p:.4f}% (1/6^4)")
    print(f"Diferență: {100.0*(exp_p - theo_p):+0.4f}%")


# -------------------- CLI --------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="dice_simulator", add_help=True)
    p.add_argument("--faces", type=int, default=6, help="număr fețe: 6,8,10,12,20")
    p.add_argument("--dice", type=int, default=1, help="număr zaruri")
    p.add_argument("--rolls", type=int, default=1000, help="număr simulări/aruncări")
    p.add_argument("--seed", type=int, default=None, help="seed pentru reproducere")

    p.add_argument("--prob", type=int, default=None, help="calculează probabilitatea pentru o sumă țintă")
    p.add_argument("--game", type=str, default=None, help="sum | craps | yahtzee")

    p.add_argument("--log", type=str, default="off", help="off | on | view")
    p.add_argument("--chart", type=str, default="none", help="none | histogram")
    p.add_argument("--stats", type=str, default="on", help="on | off")

    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.log == "view":
        view_latest_log()
        return

    if args.faces not in ALLOWED_FACES:
        raise SystemExit("faces must be one of: 6, 8, 10, 12, 20")
    if not (1 <= args.dice <= 20):
        raise SystemExit("dice must be 1..20")
    if args.rolls < 1:
        raise SystemExit("rolls must be >= 1")

    if args.seed is not None:
        random.seed(args.seed)
    else:
        # decent entropy without needing secrets
        random.seed(int(time.time()) ^ (id(args) & 0xFFFFFFFF))

    log_path = make_logfile_path() if args.log == "on" else None
    chart_hist = (args.chart == "histogram")
    stats_on = (args.stats == "on")

    try:
        if args.game:
            g = args.game.lower()
            if g == "sum":
                simulate_sum(args.dice, args.faces, args.rolls, chart_hist, stats_on, log_path)
            elif g == "craps":
                simulate_craps(args.rolls, log_path)
            elif g == "yahtzee":
                simulate_yahtzee(args.rolls, log_path)
            else:
                raise SystemExit("Unknown game. Use: sum | craps | yahtzee")
        elif args.prob is not None:
            simulate_prob(args.prob, args.dice, args.faces, args.rolls, log_path)
        else:
            # default simulation: sum of dice
            simulate_sum(args.dice, args.faces, args.rolls, chart_hist, stats_on, log_path)
    finally:
        if log_path:
            print(f"Rezultate salvate în {log_path}")


if __name__ == "__main__":
    main()
