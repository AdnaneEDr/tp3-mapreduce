# Compte rendu - TP 3 MapReduce en action

Nom(s) : à renseigner. Date : 13 octobre 2026.

## Périmètre et statut des résultats
L'énoncé réduit contient les questions Q1-Q13 et Q20-Q28 : Q14-Q19 et l'exercice de jointure ne sont pas présents. Les quatre exercices présents sont résolus, ainsi que MotsParLivre, Suggestions et le bonus chinois. Les sources Java sont dans le projet Maven. Les données et sorties de référence sont jointes.

Les sorties et compteurs présentés ci-dessous proviennent d’exécutions réelles sur le cluster HDFS et YARN avec Hadoop 3.4.1. Le cluster possède deux DataNodes et deux NodeManagers, soit six conteneurs Docker. Les captures des interfaces HDFS/YARN, les journaux bruts et les sorties HDFS sont joints. Les calculs Python indépendants restent disponibles pour contrôler les résultats.

## Partie 0
**Q1.** Les captures montrent deux DataNodes en service et deux NodeManagers RUNNING. Dernière ligne réelle du job : `Estimated value of Pi is 3.12000000000000000000`. Le journal indique une durée de 52,425 secondes. Le job comporte 2 tâches Map et 1 tâche Reduce, plus l’ApplicationMaster : au minimum 4 allocations de containers au cours du job, sans nouvelle tentative. Cela ne signifie pas 4 containers simultanés. Chaque mapper traite 100 échantillons. Le journal indique `uber mode : false` : les tâches utilisent leurs propres containers.


**Q2.** Un projet initial séparé avec les quatre classes vides des exercices a été compilé : le jar mesure **3 660 octets**. Le projet final, avec les bonus, produit un jar de **32 085 octets**, environ 31,3 Kio. La dépendance hadoop-client est `provided` : ses bibliothèques ne sont pas embarquées car elles sont déjà dans le cluster. Le jar contient le bytecode du projet et les métadonnées Maven. Le bytecode est ciblé Java 8 (major version 52).


## Exercice 1 - Mots
**Q3.** Sans filtre : (le,1), (soir,1), (le,1), (village,1), (entier,1), (attendait,1), (le,1), (retour,1), (des,1), (bateaux,1). Avec le/la/les/de/des : (soir,1), (village,1), (entier,1), (attendait,1), (retour,1), (bateaux,1). Pour village, le reducer reçoit [1,1,1] dans les mini-livres, ou des sommes partielles équivalentes après Combiner ; résultat 3.

**Q4.** Le premier job a réellement lancé **3 tâches Map**. Avec TextInputFormat, un FileSplit est créé par petit fichier ; les fichiers distincts ne sont pas fusionnés, malgré leur petite taille. CombineTextInputFormat permettrait de les regrouper.


**Q5.** Compteurs réels du second job : **GARDES=51**, **IGNORES=40**, Map output records=51, Combine input records=51, Combine output records=45, Reduce output records=42. Top 5, départagés par mot : [('mer', 4), ('données', 3), ('village', 3), ('ville', 2), ('voyage', 2)]. Le Combiner additionne localement les occurrences : 51 paires deviennent 45 avant le shuffle, puis le reducer produit 42 mots distincts. Le résultat est identique à une exécution sans Combiner. Ces compteurs ont été relevés dans le journal de l’exécution jointe ; d’autres volumes d’entrée peuvent conduire à plusieurs passages du Combiner.


**Q6.** Sortie HDFS réelle :
```text
dans	3	{conte=1, science=3, voyage=1}
les	2	{conte=1, science=3}
mer	3	{conte=2, science=1, voyage=1}
ville	2	{science=1, voyage=1}
```
Le reducer ne peut pas être réutilisé comme Combiner : il reçoit des noms de livres mais produit un nombre et une représentation de dictionnaire. Les types sémantiques diffèrent et le seuil de livres ne doit pas être appliqué localement. Une combinaison adaptée utiliserait (mot,livre) et un compteur, puis une seconde agrégation.


**Q7.** Les cinq livres demandés ont été téléchargés, conservés avec leurs en-têtes et licences, chargés dans HDFS puis traités sur YARN : identifiants 1342, 84, 11, 2701 et 1661. Longueur minimale : 1. Liste des mots vides : celle de Q7.

**Sans filtre.** Top 5 réel : [('the', 31628), ('and', 17426), ('of', 16894), ('to', 14929), ('a', 11746)]. Combine input records=571470, Combine output records=42451, gain=92.57 %. Le job produit 22683 mots distincts.

**Avec filtre.** Top 5 réel : [('s', 3227), ('this', 3112), ('have', 3052), ('which', 2629), ('from', 2595)]. Combine input records=358906, Combine output records=42301, gain=88.21 %. Le job produit 22653 mots distincts.

Les fichiers joints fixent le corpus pour la reproduction ; les 18 livres anglais du pack ne sont pas confondus avec ces cinq livres.


## Exercice 2 - Amis
**Q8.** (Amina,Bilal ; Bilal,Chaima,Driss), (Amina,Chaima ; Bilal,Chaima,Driss), (Amina,Driss ; Bilal,Chaima,Driss). La paire canonique triée rassemble les émissions A→B et B→A sous la même clé.

**Q9.** Bilal,Chaima reçoit les listes Amina,Chaima,Driss,Elias et Amina,Bilal,Driss,Elias. Intersection : [Amina, Driss, Elias]. Les Text Hadoop sont réutilisés : leur contenu est copié dans des ensembles.

**Q10.** Sortie HDFS complète :
```text
Amina,Bilal	[Chaima, Driss]
Amina,Chaima	[Bilal, Driss]
Amina,Driss	[Bilal, Chaima]
Bilal,Chaima	[Amina, Driss, Elias]
Bilal,Driss	[Amina, Chaima, Elias]
Bilal,Elias	[Chaima, Driss]
Chaima,Driss	[Amina, Bilal, Elias]
Chaima,Elias	[Bilal, Driss]
Driss,Elias	[Bilal, Chaima]
```
Compteurs réels : Map output records=18 (3+4+4+4+3 liens dirigés), Reduce input groups=9 (9 arêtes non orientées), Reduce output records=9. Chaque groupe reçoit deux listes.


**Q11.** Le fichier asymétrique ajoute Farid:Amina,Bilal. Le job réel donne 20 sorties Map, 11 groupes Reduce et 9 lignes finales. **AMITIES_A_SENS_UNIQUE=2** : Amina,Farid et Bilal,Farid ne reçoivent qu’une liste. La sortie des neuf paires réciproques est conservée.


**Q12.** Pas de Combiner fondé sur le reducer proposé : il peut recevoir une seule liste et supprimer une paire valide avant le shuffle. Pour d=5000 amis, 5000 émissions transportent chacune une liste de 5000 noms, soit environ 25 millions de références à des noms : volume O(d²). L'intersection coûte O(dA+dB) par paire avec des ensembles de hachage, avec un surcoût logarithmique pour les TreeSet ; le tri rend la sortie déterministe. Le bonus Suggestions génère d(d-1)=24 995 000 candidatures orientées.

**Q13.** Sortie HDFS réelle :
```text
Amina	Elias (3 en commun)
Bilal	[]
Chaima	[]
Driss	[]
Elias	Amina (3 en commun)
```
Amina et Elias ne sont pas amis ; Bilal, Chaima et Driss sont leurs trois amis communs. Toutes les autres paires du graphe sont déjà directes.


## Exercice 3 - Tri (sections 4.x du PDF)
**Q20.** Le shuffle trie les clés Map dans chaque partition avant le Reduce. Map émet (nombre,NullWritable), car seule la clé est utile. Le reducer réécrit la clé une fois par valeur : sinon les doublons disparaîtraient. Aucun Combiner ne doit supprimer les occurrences.

**Q21.** Croissant : [0, 2, 3, 5, 7, 7, 7, 11, 19, 31, 42, 42, 64, 73, 88, 99, 150, 256, 512, 1000]. Décroissant : [1000, 512, 256, 150, 99, 88, 73, 64, 42, 42, 31, 19, 11, 7, 7, 7, 5, 3, 2, 0]. La ligne `job.setSortComparatorClass(LongWritable.DecreasingComparator.class)` inverse l'ordre. Avec plusieurs reducers, les indices des plages sont également inversés.

**Q22.** Résultats réellement relevés sur uniforme_1M.txt :

| Reducer | Lignes | Première | Dernière |
|---|---:|---:|---:|
| 0 | 250118 | 0 | 249999 |
| 1 | 249244 | 250000 | 499999 |
| 2 | 250443 | 500000 | 749998 |
| 3 | 250195 | 750000 | 999999 |

Les plages sont [0,250000[, [250000,500000[, [500000,750000[, [750000,1000000[. Chaque partition est triée et les plages sont disjointes et ordonnées. La concaténation dans l’ordre des indices est donc triée globalement. La sortie réelle contient un million de lignes. Le contrôle indépendant compare la concaténation au tri de l’entrée et confirme la conservation de tous les doublons.


**Q23.** Effectifs réels par reducer sur le fichier biaisé : plages fixes **[706980, 134006, 89755, 69259]** ; échantillonnage Hadoop **[247195, 248025, 259921, 244859]**. RandomSampler échantillonne 10 % des lignes, jusqu’à 10 000 clés et 10 splits. InputSampler.writePartitionFile calcule des bornes adaptées à la distribution ; TotalOrderPartitioner affecte chaque clé à sa plage. L’échantillonnage vise des quantiles, ce qui répartit mieux la charge que des intervalles numériques égaux. Les sorties de ces deux jobs contiennent chacune un million de nombres, triés globalement avec tous les doublons conservés. Les bornes et effectifs peuvent changer lors d’une nouvelle exécution aléatoire. Les nombres sont écrits sur 7 chiffres pour que l’ordre lexicographique Text coïncide avec l’ordre numérique : 0000042 < 0000100. Sans remplissage, "100" < "42". Ce format suppose des entiers non négatifs de même largeur.


## Exercice 4 - Horoscope (sections 5.x)
**Q24.** 2004-03-25 : Bélier ; 2005-01-19 : Capricorne ; 2004-01-20 : Verseau ; 2003-12-21 : Sagittaire ; 2004-06-21 : Cancer ; 2005-06-20 : Gémeaux. Ces cas testent les frontières inclusives, particulièrement le passage janvier et juin. 2005-02-29 est impossible (année non bissextile) ; 2004-13-02 a un mois invalide. On incrémente DATES_INVALIDES et on ne les émet pas. LocalDate.parse vérifie réellement le calendrier ; le format AAAA-MM-JJ est imposé.

**Q25.** Map émet ("01 Bélier", "Amina Alaoui"), ou ("01 Bélier | Rabat", "Amina Alaoui") en mode ville. Le préfixe 01-12 donne l'ordre zodiacal par le tri des clés, au lieu de l'ordre alphabétique des signes. Avec plusieurs reducers, l'ordre global des signes nécessite un partitionnement adapté ou une fusion finale.

**Q26.** Sortie HDFS réelle :
```text
01 Bélier	4	Amina Alaoui, Elias El Idrissi, Loubna Lahlou, Zakaria Zniber
05 Lion	4	Chaima Chraibi, Fatima Fassi, Jalil Jabri, Yasmine Yacoubi
08 Scorpion	3	Bilal Bennani, Kenza Kettani, Mehdi Mansouri
10 Capricorne	2	Driss Daoudi, Ghita Guessous
11 Verseau	2	Imane Idrissi, Taha Tazi
```
**DATES_INVALIDES=2** ; 18 personnes valides. Les trois groupes unitaires, Gémeaux (Salma), Cancer (Omar) et Sagittaire (Nora), sont filtrés : 3 personnes omises et 15 affichées. Le job avec horoscope.min=1 produit huit groupes et affiche les 18 personnes valides.


**Q27.** Sortie HDFS réelle par signe et ville :
```text
01 Bélier | Rabat	4	Amina Alaoui, Elias El Idrissi, Loubna Lahlou, Zakaria Zniber
05 Lion | Fès	2	Chaima Chraibi, Jalil Jabri
08 Scorpion | Casablanca	3	Bilal Bennani, Kenza Kettani, Mehdi Mansouri
11 Verseau | Tanger	2	Imane Idrissi, Taha Tazi
```
Le groupe Lion | Fès contient Chaima et Jalil. Fatima est à Agadir et Yasmine à Casablanca, chacune dans un groupe de taille 1 filtré. Le seuil s’applique à chaque couple signe-ville.


**Q28.** Il existe seulement 12 clés : au plus 12 reducers reçoivent des données, et les collisions de hachage peuvent réduire encore ce nombre. 20 reducers ne garantissent donc pas 12 actifs. Pour les 12 libellés exacts du TP, le HashPartitioner Hadoop (hash Text positif modulo 20) donne seulement 9 reducers distincts : 0, 2, 4, 5, 6, 7, 11, 12 et 15. Ce calcul a été vérifié avec les classes Hadoop 3.4.1. Les gros groupes imposent un fort coût mémoire si l'on stocke tous les noms. Pour des effectifs, additionner avec Combiner ; pour toutes les personnes, utiliser une clé (signe,identifiant) et diffuser plusieurs fragments par signe, ou une agrégation en deux étapes avec salage. Ajouter la ville augmente les clés seulement si le regroupement demandé l'autorise.

**Bonus chinois.** Option horoscope.chinois=true : animal=(année-4) modulo 12. Compteur CHINOIS_DATE_INCERTAINE pour janvier et les 20 premiers jours de février. Le résultat reste une approximation signalée, car les dates du Nouvel An chinois ne sont pas fournies.

## Exécution et validation finale

Tous les jobs exécutés sont terminés avec succès. Les captures documentent les étapes et les journaux complets sont conservés dans traces/. Le grand horoscope contient 486 dates invalides et 99 514 personnes valides. Le bonus chinois signale 3 dates incertaines sur les mini-données. Les données de jointure restent disponibles mais les questions correspondantes sont absentes de l’énoncé réduit.
