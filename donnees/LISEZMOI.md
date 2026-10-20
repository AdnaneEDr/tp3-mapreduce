# Jeux de données — TP 3 « MapReduce en action »

Pack de données prêt à l'emploi pour les 5 exercices du TP 3. Chaque exercice a :

- un **mini** jeu, pour vérifier à la main (ce sont exactement les données de l'énoncé) ;
- un **grand** jeu, pour voir le parallélisme, les compteurs et les problèmes de performance.

## 1. Contenu

| Dossier / fichier | Lignes | Taille | Exercice | Remarques |
|---|---:|---:|---|---|
| `ex1_livres/mini/` (3 fichiers) | 9 | 1 Ko | 1 | les 3 mini-livres de l'énoncé |
| `ex1_livres/anglais_gutenberg/` (18 livres) | 256 893 | 11,6 Mo | 1 | **vrais livres** du projet Gutenberg : Austen, Melville, Shakespeare, Carroll, Bible KJV… |
| `ex1_livres/francais_europarl/` (10 fichiers) | 21 203 | 3,6 Mo | 1 | **vrais débats** du Parlement européen en français (janv.–févr. 2000), ≈ 640 000 mots |
| `ex2_amis/amis_mini.txt` | 5 | — | 2 | graphe de l'énoncé (Amina … Elias) |
| `ex2_amis/amis_asymetrique.txt` | 6 | — | 2 | + `Farid:Amina,Bilal` (amitiés à sens unique) |
| `ex2_amis/amis_1000.txt` | 1 000 | 0,26 Mo | 2 | réseau social synthétique : 20 « classes » de 50 personnes, ≈ 22 amis par personne |
| `ex2_amis/amis_10000.txt` | 10 000 | 2,6 Mo | 2 | même structure (200 classes), 10 fois plus grand |
| `ex3_jointure/clients_mini.csv`, `commandes_mini.csv` | 6 / 10 | — | 3 | données de l'énoncé (C06 sans commande, K109 orpheline) |
| `ex3_jointure/clients_10k.csv` | 10 000 | 0,3 Mo | 3 | noms et villes marocaines (Casablanca ≈ 34 %) |
| `ex3_jointure/commandes_200k.csv` | 200 000 | 6,9 Mo | 3 | 2026 ; 5 % de clients sans commande ; 0,5 % de commandes orphelines ; quelques très gros clients |
| `ex4_tri/nombres_mini.txt` | 20 | — | 4 | tableau de l'énoncé |
| `ex4_tri/uniforme_1M.txt` | 1 000 000 | 6,9 Mo | 4 | entiers uniformes dans [0 ; 999 999] |
| `ex4_tri/biaise_1M.txt` | 1 000 000 | 8,0 Mo | 4 | rand()⁴, écrits sur 7 chiffres (`0000042`) → pour `TriEchantillon` |
| `ex5_horoscope/personnes_mini.csv` | 20 | — | 5 | données de l'énoncé (2 dates invalides) |
| `ex5_horoscope/personnes_100k.csv` | 100 000 | 3,9 Mo | 5 | nés entre 1960 et 2005 ; ≈ 0,5 % de dates invalides (29/02 non bissextile, mois 0/13/14, format JJ/MM/AAAA) |
| `generer.py` | | | tous | régénère les données synthétiques ; `--echelle 10` pour 10 fois plus de lignes |
| `charger_hdfs.sh` | | | tous | copie tout dans HDFS sous `tp3/` |

Les formats sont exactement ceux attendus par le code du TP :

- `personne:ami1,ami2,…`
- `id_client,nom,ville`
- `id_cmd,id_client,date_cmd,montant`
- un nombre par ligne
- `id,prenom,nom,date_naissance,ville`

Tous les fichiers sont en UTF-8, avec des fins de ligne Unix.

## 2. Mise en place

1. Décompressez l'archive dans `~/tp3/donnees/`, monté dans le conteneur sous `/opt/donnees`.
2. Chargez les données dans HDFS :

```bash
docker compose exec namenode bash /opt/donnees/charger_hdfs.sh
```

Les fichiers arrivent dans HDFS sous `tp3/livres`, `tp3/livres_en`, `tp3/livres_fr`, `tp3/amis`, `tp3/jointure`, `tp3/tri` et `tp3/horoscope`.

Exemples d'exécution :

```bash
hadoop jar /opt/jobs/tp3.jar ma.bigdata.tp3.wordcount.WordCountLivres tp3/livres_fr tp3/out/fr
hadoop jar /opt/jobs/tp3.jar ma.bigdata.tp3.amis.AmisCommuns tp3/amis/amis_1000.txt tp3/out/amis1000
hadoop jar /opt/jobs/tp3.jar ma.bigdata.tp3.jointure.JointureReduce -D jointure.mode=agg \
    tp3/jointure/clients_10k.csv tp3/jointure/commandes_200k.csv tp3/out/j_agg
hadoop jar /opt/jobs/tp3.jar ma.bigdata.tp3.tri.TriEchantillon tp3/tri/biaise_1M.txt tp3/out/tri_ech 4
hadoop jar /opt/jobs/tp3.jar ma.bigdata.tp3.horoscope.Horoscope tp3/horoscope/personnes_100k.csv tp3/out/horo
```

> ⚠️ **Accents dans les options `-D`** : si la locale du terminal n'est pas UTF-8, les mots accentués (`été`, `être`…) passés en `-D wc.mots.vides=…` sont mal décodés et ne sont pas filtrés. Lancez d'abord `export LC_ALL=C.UTF-8` (le script de chargement le fait déjà).

## 3. Résultats de contrôle (pour l'enseignant)

Ces résultats ont été obtenus en exécutant le code du corrigé (Hadoop en mode local) sur ces fichiers exacts. Sur le cluster, on obtient les mêmes résultats : seuls les compteurs de fichiers et les durées changent.

### Exercice 1 — comptage des mots

**Corpus anglais, sans filtre**

| Compteur | Valeur |
|---|---:|
| Map input records | 256 893 |
| Map output records | 2 136 080 |
| Combine output records | 121 064, soit **94 % de paires en moins** |
| Mots distincts | 41 509 |

Top 5 : the 133 603, and 95 444, of 71 269, to 48 060, a 33 962.

**Corpus anglais, mots vides filtrés**

Liste utilisée :

```
the,of,and,to,a,in,i,it,that,was,he,you,his,her,as,with,for,had,is,my,on,at,be,not,but,she,me,so,by,all,him,they,this,have,which,shall,unto,from,said,there,were,we,them,their,what,or,will,when,are,no,one,if,would,thou,thy,an,been,upon
```

Options : `wc.longueur.min=2`.

Top 5 : lord 8 590, out 5 771, man 5 616, god 5 287, your 5 126. La Bible KJV, qui fait 37 % du corpus, domine.

**Corpus français, sans filtre**

| Compteur | Valeur |
|---|---:|
| Map output records | 583 815 |
| Combine output records | 58 450 |
| Mots distincts | 19 519 |

Top 5 : de 30 706, la 20 457, l 14 408, et 13 657, le 13 021.

**Corpus français, mots vides filtrés**

Liste utilisée :

```
les,des,que,qui,une,est,pour,dans,par,pas,nous,sur,cette,mais,sont,vous,avec,aux,ont,ces,plus,été,comme,être,tout,elle,ils,leur,très,également,aussi,doit,peut,fait,entre,dont,même,donc,car,ainsi,sans,cela,son,parce,leurs
```

Options : `wc.longueur.min=3`.

Top 10 :

| Rang | Mot | Occurrences |
|---:|---|---:|
| 1 | commission | 2 947 |
| 2 | européenne | 1 618 |
| 3 | union | 1 579 |
| 4 | monsieur | 1 526 |
| 5 | parlement | 1 526 |
| 6 | politique | 1 423 |
| 7 | président | 1 366 |
| 8 | pays | 1 276 |
| 9 | rapport | 1 154 |
| 10 | conseil | 1 131 |

### Exercice 2 — amis en commun

| Fichier | Map input | Map output (= liens) | Paires d'amis (lignes de sortie) |
|---|---:|---:|---:|
| `amis_1000.txt` | 1 000 | 22 036 | 11 018 (dont 3 690 sans ami commun, `[]`) |
| `amis_10000.txt` | 10 000 | 221 814 | 110 907 |
| `amis_asymetrique.txt` | 6 | 20 | 9 + compteur `AMITIES_A_SENS_UNIQUE=2` |

Suggestions sur `amis_1000.txt` : 1 000 lignes.

Exemple : `Adam00020  Reda00032 (6 en commun), Walid00042 (6 en commun), Asmae00035 (5 en commun)`.

### Exercice 3 — jointure (`clients_10k` × `commandes_200k`)

| Mode | Lignes en sortie | Compteurs |
|---|---:|---|
| inner | 199 001 | CLIENTS_SANS_COMMANDE=507, COMMANDES_ORPHELINES=999 |
| left | 199 508 (= 199 001 + 507 lignes NULL) | idem |
| agg | 10 000 (un par client) | idem |
| JointureMap (côté Map) | 199 001 (`part-m-00000`) | COMMANDES_ORPHELINES=999, aucun shuffle |

- **Shuffle** de la jointure côté Reduce : 8 014 110 octets, soit environ 8 Mo, alors qu'il est **nul** côté Map.
- **Chiffre d'affaires total** (mode agg) : 21 985 336,81 sur 199 001 commandes.
- **Point de discussion, client géant** : C007123 (Othmane Berrada, Tanger) totalise **44 076 commandes**, 22 % du total, pour 4 846 727,36. C'est une clé très déséquilibrée. Le reducer qui la reçoit garde 44 076 commandes en mémoire et travaille beaucoup plus que les autres : c'est un bon exemple réel de **data skew** et une bonne motivation du tri secondaire.

### Exercice 4 — tri (4 reducers)

| Fichier | Méthode | Lignes par reducer |
|---|---|---|
| `uniforme_1M.txt` | TriSimple + plages | 250 118 / 249 244 / 250 443 / 250 195 → équilibré, tri global vérifié (`sort -n -c`) |
| `biaise_1M.txt` | TriSimple + plages | **706 980** / 134 006 / 89 755 / 69 259 → déséquilibre |
| `biaise_1M.txt` | TriEchantillon | 251 254 / 245 917 / 255 106 / 247 723 → équilibré |

Les bornes de TriEchantillon varient légèrement d'une exécution à l'autre, car l'échantillon est aléatoire.

`uniforme_1M.txt` contient 264 023 valeurs présentes en plusieurs exemplaires : les doublons doivent être conservés.

### Exercice 5 — horoscope (`personnes_100k.csv`)

DATES_INVALIDES=486, donc 99 514 personnes valides :

| Signe | Personnes | Signe | Personnes |
|---|---:|---|---:|
| 01 Bélier | 8 160 | 07 Balance | 8 209 |
| 02 Taureau | 8 544 | 08 Scorpion | 8 051 |
| 03 Gémeaux | 8 294 | 09 Sagittaire | 8 159 |
| 04 Cancer | 8 894 | 10 Capricorne | 7 798 |
| 05 Lion | 8 408 | 11 Verseau | 8 162 |
| 06 Vierge | 8 590 | 12 Poissons | 8 245 |

Avec `-D horoscope.ville=true` : 180 groupes (12 signes × 15 villes). Le plus gros groupe est « 04 Cancer | Casablanca », avec 2 958 personnes.

Ici, chaque ligne de sortie contient environ 8 000 noms : c'est l'occasion de discuter de la mémoire du Reducer, et de l'intérêt de ne sortir que les effectifs.

## 4. Sources et licences

- **Gutenberg** : sélection du corpus « gutenberg » de NLTK (nltk_data). Ce sont des textes du domaine public issus du projet Gutenberg (gutenberg.org) ; les en-têtes de licence ont été retirés par NLTK.
- **Europarl** : extraits français du corpus « europarl_raw » de NLTK. Ils proviennent du corpus Europarl de P. Koehn, « Europarl: A Parallel Corpus for Statistical Machine Translation », MT Summit 2005, diffusé sans restriction de droits connue (statmt.org/europarl).
- **Données synthétiques** : clients, commandes, amis, nombres et personnes sont générés par `generer.py`. Les noms sont fictifs, et toute ressemblance avec des personnes réelles est fortuite.
