# Compte rendu - TP 3 MapReduce en action

Nom(s) : à renseigner. Date : 13 octobre 2026.

## Périmètre et statut des résultats
L'énoncé réduit contient les questions Q1-Q13 et Q20-Q28 : Q14-Q19 et l'exercice de jointure ne sont pas présents. Les quatre exercices présents sont résolus, ainsi que MotsParLivre, Suggestions et le bonus chinois. Les sources Java sont dans le projet Maven. Les données et sorties de référence sont jointes.

Les sorties ci-dessous sont calculées directement sur les fichiers réels par un programme Python indépendant. Elles ne sont pas présentées comme des exécutions HDFS/YARN. Les nombres de tâches et les compteurs dépendant du moteur sont des prévisions expliquées. Docker n'étant pas démarré, les deux captures demandées, la ligne finale du job pi et les journaux YARN restent à produire avec les scripts fournis. Aucune capture ni durée n'est inventée.

## Partie 0
**Q1.** Le job pi 2 100 comporte 2 tâches Map et 1 tâche Reduce, plus l'ApplicationMaster : au minimum 4 allocations de containers au cours du job, sans tentative supplémentaire. Cela ne signifie pas 4 containers simultanés. Les deux mappers lancent chacun 100 échantillons. La valeur approximative de pi et la dernière ligne doivent être relevées sur l'exécution réelle. Captures à joindre : Datanodes sur localhost:9870 et Nodes sur localhost:8088, avec 2 nœuds actifs de chaque type.

**Q2.** La taille du jar final compilé est indiquée dans VALIDATION.md. Le jar initial contenant seulement des classes vides n'a pas été mesuré. La dépendance Hadoop est `provided` : ses bibliothèques ne sont pas embarquées, car elles sont disponibles dans le cluster. Le jar contient le bytecode du projet et les métadonnées Maven. Le bytecode est ciblé Java 8.

## Exercice 1 - Mots
**Q3.** Sans filtre : (le,1), (soir,1), (le,1), (village,1), (entier,1), (attendait,1), (le,1), (retour,1), (des,1), (bateaux,1). Avec le/la/les/de/des : (soir,1), (village,1), (entier,1), (attendait,1), (retour,1), (bateaux,1). Pour village, le reducer reçoit [1,1,1] dans les mini-livres, ou des sommes partielles équivalentes après Combiner ; résultat 3.

**Q4.** On prévoit 3 mappers avec TextInputFormat : un FileSplit par petit fichier. Les fichiers différents ne sont pas fusionnés dans un split, malgré leur petite taille. CombineTextInputFormat permettrait de les regrouper.

**Q5.** wc2 : GARDES=51, IGNORES=40 tokens rejetés non vides, Map output records=51, Reduce output records=42. Le squelette compte aussi les chaînes vides produites par split : le compteur IGNORES effectif est donc à lire dans le journal Hadoop, plutôt qu'à assimiler automatiquement au nombre de mots rejetés. Avec une combinaison complète par fichier, Combine output records=45. La combinaison peut être exécutée zéro, une ou plusieurs fois ; ses compteurs exacts dépendent de l'exécution. Top 5, départagés par mot : [('mer', 4), ('données', 3), ('village', 3), ('ville', 2), ('voyage', 2)]. Le Combiner additionne localement, réduisant les paires du shuffle sans modifier les totaux.

**Q6.** Sortie :
```text
dans	3	{'conte': 1, 'science': 3, 'voyage': 1}
les	2	{'conte': 1, 'science': 3}
mer	3	{'conte': 2, 'science': 1, 'voyage': 1}
ville	2	{'science': 1, 'voyage': 1}
```
Le reducer ne peut pas être réutilisé comme Combiner : il reçoit des noms de livres mais produit un nombre et une représentation de dictionnaire. Les types sémantiques diffèrent et le seuil de livres ne doit pas être appliqué localement. Une combinaison adaptée utiliserait (mot,livre) et un compteur, puis une seconde agrégation.

**Q7.** Corpus exact : identifiants Gutenberg 1342, 84, 11, 2701 et 1661. Les fichiers téléchargés sont joints ; en-têtes et licences conservés, comme dans la commande de l'énoncé. Résultats de référence calculés le 13 octobre 2026, avec longueur minimale 1 et la liste exacte de mots vides de Q7 :

Sans filtre : top 5 [('the', 31628), ('and', 17426), ('of', 16894), ('to', 14929), ('a', 11746)]. 571470 occurrences ; 42451 paires après une combinaison idéale par fichier, gain 92.57 %.

Avec filtre : top 5 [('s', 3227), ('this', 3112), ('have', 3052), ('which', 2629), ('from', 2595)]. 358906 occurrences ; 42301 paires après une combinaison idéale par fichier, gain 88.21 %.

Les gains ci-dessus sont des calculs de combinaison idéale par fichier, et non des compteurs Hadoop relevés. Les fichiers Gutenberg peuvent changer ; les copies jointes fixent l'entrée pour la reproduction.

## Exercice 2 - Amis
**Q8.** (Amina,Bilal ; Bilal,Chaima,Driss), (Amina,Chaima ; Bilal,Chaima,Driss), (Amina,Driss ; Bilal,Chaima,Driss). La paire canonique triée rassemble les émissions A→B et B→A sous la même clé.

**Q9.** Bilal,Chaima reçoit les listes Amina,Chaima,Driss,Elias et Amina,Bilal,Driss,Elias. Intersection : [Amina, Driss, Elias]. Les Text Hadoop sont réutilisés : leur contenu est copié dans des ensembles.

**Q10.** Sortie complète :
```text
Amina,Bilal	['Chaima', 'Driss']
Amina,Chaima	['Bilal', 'Driss']
Amina,Driss	['Bilal', 'Chaima']
Bilal,Chaima	['Amina', 'Driss', 'Elias']
Bilal,Driss	['Amina', 'Chaima', 'Elias']
Bilal,Elias	['Chaima', 'Driss']
Chaima,Driss	['Amina', 'Bilal', 'Elias']
Chaima,Elias	['Bilal', 'Driss']
Driss,Elias	['Bilal', 'Chaima']
```
Map output records=18 (3+4+4+4+3 liens dirigés), Reduce input groups=9 (9 arêtes non orientées). Chaque groupe possède 2 listes.

**Q11.** Farid ajoute 2 émissions ; 20 sorties Map et 11 groupes Reduce, mais seulement 9 lignes finales. AMITIES_A_SENS_UNIQUE=2 : Amina,Farid et Bilal,Farid ne reçoivent qu'une liste.

**Q12.** Pas de Combiner fondé sur le reducer proposé : il peut recevoir une seule liste et supprimer une paire valide avant le shuffle. Pour d=5000 amis, 5000 émissions transportent chacune une liste de 5000 noms, soit environ 25 millions de références à des noms : volume O(d²). L'intersection coûte O(dA+dB) par paire avec des ensembles de hachage, avec un surcoût logarithmique pour les TreeSet ; le tri rend la sortie déterministe. Le bonus Suggestions génère d(d-1)=24 995 000 candidatures orientées.

**Q13.**
```text
Amina	Elias (3 en commun)
Bilal	[]
Chaima	[]
Driss	[]
Elias	Amina (3 en commun)
```
Amina et Elias ne sont pas amis ; Bilal, Chaima et Driss sont leurs trois amis communs. Toutes les autres paires sont déjà directes.

## Exercice 3 - Tri (sections 4.x du PDF)
**Q20.** Le shuffle trie les clés Map dans chaque partition avant le Reduce. Map émet (nombre,NullWritable), car seule la clé est utile. Le reducer réécrit la clé une fois par valeur : sinon les doublons disparaîtraient. Aucun Combiner ne doit supprimer les occurrences.

**Q21.** Croissant : [0, 2, 3, 5, 7, 7, 7, 11, 19, 31, 42, 42, 64, 73, 88, 99, 150, 256, 512, 1000]. Décroissant : [1000, 512, 256, 150, 99, 88, 73, 64, 42, 42, 31, 19, 11, 7, 7, 7, 5, 3, 2, 0]. La ligne `job.setSortComparatorClass(LongWritable.DecreasingComparator.class)` inverse l'ordre. Avec plusieurs reducers, les indices des plages sont également inversés.

**Q22.** Résultats exacts sur uniforme_1M.txt :
| Reducer | Lignes | Première | Dernière |
|---|---:|---:|---:|
| 0 | 250118 | 0 | 249999 |
| 1 | 249244 | 250000 | 499999 |
| 2 | 250443 | 500000 | 749998 |
| 3 | 250195 | 750000 | 999999 |

Les plages sont [0,250000[, [250000,500000[, [500000,750000[, [750000,1000000[. Les partitions sont disjointes et ordonnées ; chaque fichier est trié. Les concaténer par indice donne donc un tri global. La vérification indépendante conserve le million d'éléments, y compris les doublons, et compare la concaténation au tri intégral de l'entrée.

**Q23.** Plages fixes sur biaise_1M : [706980, 134006, 89755, 69259]. Simulation d'un échantillon de 10000 valeurs, graine 2026 : {'bornes': [3677, 58149, 310717], 'effectifs': [246366, 244501, 255642, 253491], 'note': 'Simulation Python deterministe; pas une execution InputSampler Hadoop.'}. Les valeurs exactes Hadoop varieront : RandomSampler échantillonne jusqu'à 10 splits, puis writePartitionFile calcule les bornes. TotalOrderPartitioner affecte les clés aux plages obtenues. L'échantillonnage vise des quantiles, pas des intervalles numériques égaux, d'où un meilleur équilibre. Sur 7 chiffres, l'ordre lexicographique Text coïncide avec l'ordre numérique pour les entiers non négatifs : 0000042 < 0000100. Sans remplissage, "100" < "42". Ne pas utiliser ce format pour des nombres négatifs ou de largeur variable.

## Exercice 4 - Horoscope (sections 5.x)
**Q24.** 2004-03-25 : Bélier ; 2005-01-19 : Capricorne ; 2004-01-20 : Verseau ; 2003-12-21 : Sagittaire ; 2004-06-21 : Cancer ; 2005-06-20 : Gémeaux. Ces cas testent les frontières inclusives, particulièrement le passage janvier et juin. 2005-02-29 est impossible (année non bissextile) ; 2004-13-02 a un mois invalide. On incrémente DATES_INVALIDES et on ne les émet pas. LocalDate.parse vérifie réellement le calendrier ; le format AAAA-MM-JJ est imposé.

**Q25.** Map émet ("01 Bélier", "Amina Alaoui"), ou ("01 Bélier | Rabat", "Amina Alaoui") en mode ville. Le préfixe 01-12 donne l'ordre zodiacal par le tri des clés, au lieu de l'ordre alphabétique des signes. Avec plusieurs reducers, l'ordre global des signes nécessite un partitionnement adapté ou une fusion finale.

**Q26.**
```text
01 Bélier	4	Amina Alaoui, Elias El Idrissi, Loubna Lahlou, Zakaria Zniber
05 Lion	4	Chaima Chraibi, Fatima Fassi, Jalil Jabri, Yasmine Yacoubi
08 Scorpion	3	Bilal Bennani, Kenza Kettani, Mehdi Mansouri
10 Capricorne	2	Driss Daoudi, Ghita Guessous
11 Verseau	2	Imane Idrissi, Taha Tazi
```
DATES_INVALIDES=2 ; 18 personnes valides. Les trois groupes unitaires, Gémeaux (Salma), Cancer (Omar) et Sagittaire (Nora), sont filtrés : 3 personnes omises et 15 affichées.

**Q27.**
```text
01 Bélier | Rabat	4	Amina Alaoui, Elias El Idrissi, Loubna Lahlou, Zakaria Zniber
05 Lion | Fès	2	Chaima Chraibi, Jalil Jabri
08 Scorpion | Casablanca	3	Bilal Bennani, Kenza Kettani, Mehdi Mansouri
11 Verseau | Tanger	2	Imane Idrissi, Taha Tazi
```
Le groupe Lion devient Lion | Fès avec Chaima et Jalil ; Fatima est à Agadir et Yasmine à Casablanca, chacune dans un groupe de taille 1 filtré. Le seuil porte sur chaque couple signe-ville.

**Q28.** Il existe seulement 12 clés : au plus 12 reducers reçoivent des données, et les collisions de hachage peuvent réduire encore ce nombre. 20 reducers ne garantissent donc pas 12 actifs. Les gros groupes imposent un fort coût mémoire si l'on stocke tous les noms. Pour des effectifs, additionner avec Combiner ; pour toutes les personnes, utiliser une clé (signe,identifiant) et diffuser plusieurs fragments par signe, ou une agrégation en deux étapes avec salage. Ajouter la ville augmente les clés seulement si le regroupement demandé l'autorise.

**Bonus chinois.** Option horoscope.chinois=true : animal=(année-4) modulo 12. Compteur CHINOIS_DATE_INCERTAINE pour janvier et les 20 premiers jours de février. Le résultat reste une approximation signalée, car les dates du Nouvel An chinois ne sont pas fournies.

## Exécution et pièces à compléter
Voir README.md et executer_tp.sh. Après lancement du cluster : joindre les captures réelles des interfaces, la dernière ligne de pi et les compteurs Combine de Q5/Q7. Les données jointes de jointure restent disponibles mais aucune question correspondante ne figure dans cet énoncé réduit.
