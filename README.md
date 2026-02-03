# Meniu Teme – Proiecte Python + Docker

Acest repository conține mai multe teme implementate în Python.
Fiecare temă este rulabilă direct prin Docker, fără instalări locale.

STRUCTURA REPOSITORY

meniu-teme/
README.md
predare_master.txt
tema2-dice-simulator/
tema7-queue-simulator/
tema8-ascii-art/

---

## TEMA 2 – SIMULATOR DE ZARURI (MONTE CARLO)

Descriere:
Simulator de aruncări de zaruri pentru analizarea probabilităților și a statisticilor.

Funcționalități:
- Zaruri cu fețe configurabile (6, 8, 10, 12, 20)
- Simulări Monte Carlo
- Probabilități experimentale vs teoretice
- Medie, mediană, deviație standard
- Histograme ASCII
- Jocuri: sumă zaruri, craps, yahtzee

Rulare Docker:
docker run --rm potrabogdan/dice-simulator:latest

Exemplu:
docker run --rm potrabogdan/dice-simulator:latest python dice-simulation.py --prob 7 --dice 2 --faces 6 --rolls 10000

Cod sursă:
tema2-dice-simulator/

---

## TEMA 7 – SIMULATOR DE COZI LA GHIȘEU

Descriere:
Simulare discretă de cozi pentru analizarea timpilor de așteptare și a congestiei.

Funcționalități:
- Sosiri aleatorii ale clienților
- Rată de sosire configurabilă
- Rată de servire configurabilă
- Unul sau mai multe ghișee
- Timp mediu de așteptare
- Congestie maximă
- Comparație între scenarii

Rulare Docker:
docker run --rm potrabogdan/queue-simulator:latest

Exemplu:
docker run --rm potrabogdan/queue-simulator:latest python queue_simulator.py --compare "1,2,3" --clients 100

Cod sursă:
tema7-queue-simulator/

---

## TEMA 8 – PROCESOR ASCII ART

Descriere:
Aplicație pentru conversia imaginilor sau a textului în ASCII art.

Funcționalități:
- Conversie imagini PNG/JPG în ASCII art
- Conversie text în banner ASCII
- Scalare și redimensionare
- Filtre: grayscale, invert, contrast, blur
- Set de caractere configurabil
- Export în fișier text
- Preview în terminal

Rulare Docker:
docker run --rm potrabogdan/ascii-art:latest

Exemplu:
docker run --rm -v ${PWD}:/data potrabogdan/ascii-art:latest python ascii_art.py /data/input.png --width 80 --output /data/art.txt --preview

Cod sursă:
tema8-ascii-art/

---

STRUCTURA REPOSITORY

meniu-teme/
README.md
predare_master.txt
tema2-dice-simulator/
tema7-queue-simulator/
tema8-ascii-art/

Sfârșit README
