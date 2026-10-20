# TP3 MapReduce - livraison

Lire COMPTE_RENDU_ILLUSTRE.pdf ou COMPTE_RENDU_AVEC_CAPTURES.md pour les réponses Q1-Q13 et Q20-Q28. Le PDF fourni est une version réduite sans les questions sur la jointure.

## Contenu
- tp3-mapreduce/ : projet Maven, 7 classes Java, Hadoop 3.4.1, bytecode Java 8.
- jobs/tp3.jar : jar compilé, dépendances Hadoop fournies par le cluster.
- donnees/ : données originales et les cinq livres Gutenberg de Q7.
- resultats/ : sorties de référence indépendantes et vérifications numériques.
- docker-compose.yml, config : cluster de l'énoncé.
- executer_tp.sh : exécutions avec traces et vérifications de tri.
- VALIDATION.md : contrôles effectués et limites.

## Compilation
Dans tp3-mapreduce : `mvn clean package`, puis copier target/tp3.jar vers ../jobs/.
Alternative depuis WSL : `docker run --rm -v "$PWD/tp3-mapreduce:/app" -w /app maven:3.9-eclipse-temurin-17 mvn clean package`.

## Cluster sous Windows
Lancer Docker Desktop avec le moteur Linux/WSL2. Ouvrir un terminal WSL dans ce dossier puis : `bash executer_tp.sh`.
Le script attend HDFS et conserve les traces sous traces/. Le compte rendu joint correspond au cluster compose nommé tp3captures. Il utilise un dossier de sortie daté pour éviter d'effacer des résultats existants. Vérifier 2 DataNodes et 2 NodeManagers actifs avant d'interpréter les mesures. La configuration reprend le TP ; elle n'est pas destinée à une production.

## Précautions de lecture
Le compte rendu final présente les exécutions réelles HDFS/YARN et leurs compteurs. Les résultats Python servent de contrôle indépendant ; leur simulation d’échantillonnage reste distincte du job Hadoop. Les journaux bruts et les captures sont joints. Les trois sorties de tri d’un million de nombres conservent toutes les lignes et tous les doublons.
TriEchantillon attend exclusivement des entiers non négatifs écrits sur 7 chiffres, sans tabulation, et un échantillon avec assez de clés distinctes. Les CSV du pack n'utilisent pas de champs entre guillemets contenant des virgules ; les mappers Java utilisent ce contrat simple.

## Compte rendu illustré
COMPTE_RENDU_ILLUSTRE.pdf contient les réponses et les captures pour les étapes de préparation et chaque exécution. Les interfaces HDFS et YARN sont capturées directement ; les autres figures montrent les journaux réels et leurs résultats dans le navigateur de consultation.
