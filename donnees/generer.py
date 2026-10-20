#!/usr/bin/env python3
"""
Générateur des jeux de données synthétiques du TP 3 (MapReduce).
Reproductible : mêmes graines → mêmes fichiers. Python 3.8+, bibliothèque standard uniquement.

Usage :
  python3 generer.py                 # tailles par défaut (celles du pack)
  python3 generer.py --echelle 10    # 10 fois plus de lignes (pour mesurer les performances)
"""
import argparse, os, random, datetime

PRENOMS = ["Amina", "Bilal", "Chaima", "Driss", "Elias", "Fatima", "Ghita", "Hamza", "Imane", "Jalil", "Kenza", "Loubna",
           "Mehdi", "Nora", "Omar", "Rania", "Salma", "Taha", "Yasmine", "Zakaria", "Adam", "Aya", "Youssef", "Hiba",
           "Anas", "Sara", "Ayoub", "Meryem", "Karim", "Nadia", "Othmane", "Houda", "Reda", "Ilham", "Soufiane", "Asmae",
           "Hassan", "Khadija", "Rachid", "Latifa", "Nabil", "Samira", "Walid", "Zineb", "Ismail", "Malak", "Amine", "Wiam"]
NOMS = ["Alaoui", "Bennani", "Chraibi", "Daoudi", "El Idrissi", "Fassi", "Guessous", "Haddad", "Idrissi", "Jabri", "Kettani",
        "Lahlou", "Mansouri", "Naciri", "Ouazzani", "Sqalli", "Tazi", "Yacoubi", "Zniber", "Raji", "Benjelloun", "Berrada",
        "Cherkaoui", "El Amrani", "El Fassi", "Filali", "Hajji", "Kabbaj", "Lamrani", "Mernissi", "Ouali", "Rami", "Sebti",
        "Tahiri", "Wahbi", "Ziani", "Amrani", "Bouzid", "Choukri", "Drissi"]
# villes pondérées par une population approximative : Casablanca domine (utile pour parler de data skew)
VILLES = [("Casablanca", 34), ("Rabat", 9), ("Fès", 11), ("Marrakech", 9), ("Tanger", 9), ("Agadir", 4), ("Meknès", 6),
          ("Oujda", 5), ("Kénitra", 4), ("Tétouan", 4), ("Safi", 3), ("El Jadida", 2), ("Béni Mellal", 2), ("Nador", 1), ("Laâyoune", 1)]


def ville(r):
    return r.choices([v for v, _ in VILLES], weights=[p for _, p in VILLES])[0]


def ecrire(chemin, lignes):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        for l in lignes:
            f.write(l + "\n")
    print(f"  {chemin:45s} {os.path.getsize(chemin) / 1e6:8.2f} Mo")


# ---------------------------------------------------------------- Exercice 2 : graphe d'amitié
def amis(n, groupes, p_in, p_out, graine, chemin):
    r = random.Random(graine)
    noms = [f"{PRENOMS[i % len(PRENOMS)]}{i:05d}" for i in range(n)]
    groupe = [i * groupes // n for i in range(n)]          # classes / équipes : forte densité à l'intérieur
    adj = [set() for _ in range(n)]
    taille = n // groupes
    for i in range(n):
        g = groupe[i]
        debut = g * taille
        for j in range(max(i + 1, debut), min(n, debut + taille)):   # liens dans le groupe
            if r.random() < p_in:
                adj[i].add(j); adj[j].add(i)
        for _ in range(int(p_out * n)):                       # quelques liens hors du groupe
            j = r.randrange(n)
            if j != i:
                adj[i].add(j); adj[j].add(i)
    for i in range(n):                                        # personne n'est isolé
        if not adj[i]:
            j = (i + 1) % n
            adj[i].add(j); adj[j].add(i)
    ecrire(chemin, (noms[i] + ":" + ",".join(noms[j] for j in sorted(adj[i])) for i in range(n)))


# ---------------------------------------------------------------- Exercice 3 : clients / commandes
def jointure(n_clients, n_cmd, graine, rep):
    r = random.Random(graine)
    clients = []
    for i in range(1, n_clients + 1):
        clients.append(f"C{i:06d},{r.choice(PRENOMS)} {r.choice(NOMS)},{ville(r)}")
    ecrire(f"{rep}/clients_{n_clients // 1000}k.csv", ["id_client,nom,ville"] + clients)
    # 5 % des clients n'achètent jamais ; quelques gros clients (loi de Pareto) ; 0,5 % de commandes orphelines
    actifs = list(range(1, n_clients + 1))
    r.shuffle(actifs)
    actifs = actifs[: int(n_clients * 0.95)]
    poids = [r.paretovariate(1.5) for _ in actifs]
    debut = datetime.date(2026, 1, 1)
    lignes = ["id_cmd,id_client,date_cmd,montant"]
    choix = r.choices(actifs, weights=poids, k=n_cmd)
    for k in range(n_cmd):
        idc = choix[k] if r.random() > 0.005 else n_clients + 1 + r.randrange(1000)   # orpheline
        d = debut + datetime.timedelta(days=r.randrange(273))
        montant = round(min(r.lognormvariate(4.3, 0.9), 20000), 2)
        lignes.append(f"K{k + 1:07d},C{idc:06d},{d.isoformat()},{montant:.2f}")
    ecrire(f"{rep}/commandes_{n_cmd // 1000}k.csv", lignes)


# ---------------------------------------------------------------- Exercice 4 : nombres
def nombres(n, graine, rep):
    r = random.Random(graine)
    ecrire(f"{rep}/uniforme_{n // 1_000_000}M.txt", (str(r.randrange(1_000_000)) for _ in range(n)))
    r = random.Random(graine + 1)
    ecrire(f"{rep}/biaise_{n // 1_000_000}M.txt", (f"{int(r.random() ** 4 * 1_000_000):07d}" for _ in range(n)))


# ---------------------------------------------------------------- Exercice 5 : personnes
def personnes(n, graine, chemin):
    r = random.Random(graine)
    lignes = ["id,prenom,nom,date_naissance,ville"]
    debut = datetime.date(1960, 1, 1)
    for i in range(1, n + 1):
        d = debut + datetime.timedelta(days=r.randrange(365 * 46))
        txt = d.isoformat()
        x = r.random()
        if x < 0.002:   # 0,2 % de 29 février sur une année non bissextile
            a = r.choice([2001, 2003, 2005, 2007, 2010, 2015])
            txt = f"{a}-02-29"
        elif x < 0.004:  # 0,2 % de mois impossible
            txt = f"{d.year}-{r.choice([0, 13, 14])}-{d.day:02d}"
        elif x < 0.005:  # 0,1 % de format invalide
            txt = d.strftime("%d/%m/%Y")
        lignes.append(f"{i},{r.choice(PRENOMS)},{r.choice(NOMS)},{txt},{ville(r)}")
    ecrire(chemin, lignes)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--echelle", type=int, default=1, help="multiplie le nombre de lignes")
    ap.add_argument("--sortie", default=".", help="dossier de sortie")
    a = ap.parse_args()
    e, o = a.echelle, a.sortie
    print("Génération (échelle ×%d) :" % e)
    amis(1000 * e, 20 * e, 0.25, 0.005, 42, f"{o}/ex2_amis/amis_{1000 * e}.txt")
    if e == 1:
        amis(10000, 200, 0.25, 0.0005, 43, f"{o}/ex2_amis/amis_10000.txt")
    jointure(10_000 * e, 200_000 * e, 2026, f"{o}/ex3_jointure")
    nombres(1_000_000 * e, 7, f"{o}/ex4_tri")
    personnes(100_000 * e, 5, f"{o}/ex5_horoscope/personnes_{100 * e}k.csv")
