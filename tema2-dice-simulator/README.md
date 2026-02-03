# Tema 2 – Simulator de zaruri și jocuri de noroc

Simulator CLI pentru aruncări de zaruri, simulări Monte Carlo, probabilități și statistici.
Include jocuri simple: sumă zaruri, craps, yahtzee.

## Funcționalități
- Zaruri cu fețe configurabile (6, 8, 10, 12, 20)
- Simulări Monte Carlo
- Probabilități experimentale vs teoretice
- Statistici: medie, mediană, deviație standard
- Histograme ASCII
- Log-uri în fișiere
- Seed pentru reproducerea rezultatelor
- Jocuri: sum, craps, yahtzee

## Rulare local (Python)
```bash
python dice-simulation.py --faces 6 --rolls 1000
python dice-simulation.py --faces 6 --rolls 1000 --chart histogram
python dice-simulation.py --prob 7 --dice 2 --faces 6 --rolls 10000
python dice-simulation.py --game craps --rolls 100
python dice-simulation.py --game yahtzee --rolls 200000
python dice-simulation.py --log view

## Rulare in powershell
```powershell
- docker run --rm potrabogdan/dice-simulator python dice-simulation.py --prob 7 --dice 2 --faces 6  -rolls 10000
