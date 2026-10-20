#!/bin/bash
# Charge tous les jeux de données du TP 3 dans HDFS, sous /user/<vous>/tp3/...
# À lancer DANS le conteneur namenode, le pack étant copié dans ~/tp3/donnees (monté sur /opt/donnees) :
#   docker compose exec namenode bash /opt/donnees/charger_hdfs.sh
set -e
export LC_ALL=en_US.utf8          # indispensable pour les accents dans les options -D
SRC=${1:-/opt/donnees}
hdfs dfs -mkdir -p tp3/livres tp3/livres_en tp3/livres_fr tp3/amis tp3/jointure tp3/tri tp3/horoscope
hdfs dfs -put -f $SRC/ex1_livres/mini/*.txt               tp3/livres/
hdfs dfs -put -f $SRC/ex1_livres/anglais_gutenberg/*.txt  tp3/livres_en/
hdfs dfs -put -f $SRC/ex1_livres/francais_europarl/*.txt  tp3/livres_fr/
hdfs dfs -put -f $SRC/ex2_amis/*.txt                      tp3/amis/
hdfs dfs -put -f $SRC/ex3_jointure/*.csv                  tp3/jointure/
hdfs dfs -put -f $SRC/ex4_tri/*.txt                       tp3/tri/
hdfs dfs -put -f $SRC/ex5_horoscope/*.csv                 tp3/horoscope/
hdfs dfs -du -s -h tp3/*
echo "Jeux de données chargés dans HDFS (répertoire tp3/)."
