# Validation finale du 13 octobre 2026

Le projet est compilé et les exécutions sur HDFS et YARN sont terminées avec succès. Le cluster Hadoop 3.4.1 possède deux DataNodes et deux NodeManagers. Les captures directes des interfaces HDFS/YARN sont jointes, ainsi que les captures de consultation des journaux réels pour chaque étape.

- Maven clean package : réussite, 7 classes compilées, jar final de 32 085 octets, bytecode Java 8.
- Projet initial avec quatre classes vides : jar de 3 660 octets.
- 47 contrôles Java ciblés réussis sur les dates, signes, partitions et mots.
- Premier job YARN pi : 3,12000000000000000000, journal complet conservé.
- Tous les exercices et bonus présents dans l’énoncé réduit exécutés avec code de sortie 0.
- Compteurs réels de Combiner relevés pour wc2 et les deux jobs Gutenberg.
- Sorties des mini-exercices et de Gutenberg comparées aux résultats Python indépendants : identiques.
- Trois tris d’un million de nombres : ordre global, cardinalité et multiensemble identique à l’entrée vérifiés. Aucun doublon perdu.
- Grand horoscope : 486 dates invalides, 99 514 personnes valides.
- Les effectifs de TriEchantillon du compte rendu sont désormais ceux du job Hadoop réel. La simulation Python reste distincte dans resultats/verification.json.

Les traces contiennent les commandes, leurs horodatages UTC, les sorties HDFS et les journaux de chaque job. verification_cluster.json décrit les vérifications des tris. Le dossier captures contient les images intégrées au PDF. Les captures des journaux sont des vues du navigateur de consultation, et non des faux écrans de terminal.

Reproduction : lancer Docker Desktop puis `bash executer_tp.sh` depuis WSL/Linux. Le script de chargement utilise en_US.utf8, disponible dans l’image Hadoop ; la première exécution avait un avertissement C.UTF-8 sans impact sur les données, conservé dans le journal original.
