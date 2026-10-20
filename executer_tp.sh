#!/usr/bin/env bash
# A lancer dans WSL/Linux, depuis le dossier TP3-MapReduce.
# Les sorties HDFS ne sont jamais supprimees automatiquement.
set -euo pipefail
export LC_ALL=C.UTF-8
mkdir -p traces
docker compose -p tp3captures up -d --scale datanode=2 --scale nodemanager=2
echo "Attente du HDFS (au plus 120 secondes)..."
ready=false
for i in $(seq 1 60); do
  if docker compose -p tp3captures exec -T namenode hdfs dfsadmin -safemode get 2>/dev/null | grep -q OFF; then ready=true; break; fi
  sleep 2
done
if [ "$ready" != true ]; then echo "HDFS indisponible : consulter docker compose -p tp3captures logs"; exit 1; fi
docker compose -p tp3captures exec -T namenode hdfs dfsadmin -report | tee traces/hdfs.txt
docker compose -p tp3captures exec -T namenode yarn node -list | tee traces/yarn.txt
docker compose -p tp3captures exec -T namenode hadoop jar /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar pi 2 100 2>&1 | tee traces/pi.txt
docker compose -p tp3captures exec -T namenode bash /opt/donnees/charger_hdfs.sh
docker compose -p tp3captures exec -T namenode hdfs dfs -mkdir -p tp3/gutenberg
docker compose -p tp3captures exec -T namenode hdfs dfs -put -f /opt/donnees/gutenberg_5/*.txt tp3/gutenberg/
RUN="tp3/out/run_$(date +%Y%m%d_%H%M%S)"
run() {
  local label="$1" cls="$2"; shift 2
  docker compose -p tp3captures exec -T namenode hadoop jar /opt/jobs/tp3.jar "ma.bigdata.tp3.$cls" "$@" 2>&1 | tee "traces/$label.log"
  docker compose -p tp3captures exec -T namenode hdfs dfs -cat "$RUN/$label/part-*" > "traces/$label.txt"
}
run wc1 wordcount.WordCountLivres tp3/livres "$RUN/wc1"
run wc2 wordcount.WordCountLivres -D wc.mots.vides=le,la,les,de,des,dans,en,un,une,et,au,ce,l,il,son,par,puis -D wc.longueur.min=2 tp3/livres "$RUN/wc2"
run mpl wordcount.MotsParLivre -D mpl.livres.min=2 tp3/livres "$RUN/mpl"
run gutenberg wordcount.WordCountLivres tp3/gutenberg "$RUN/gutenberg"
run gutenberg_filtre wordcount.WordCountLivres -D wc.mots.vides=the,of,and,to,a,in,i,it,that,was,he,you,his,her,as,with,for,had,is,my,on,at,be,not,but,she,me,so,by,all tp3/gutenberg "$RUN/gutenberg_filtre"
run amis amis.AmisCommuns tp3/amis/amis_mini.txt "$RUN/amis"
run amis_asym amis.AmisCommuns tp3/amis/amis_asymetrique.txt "$RUN/amis_asym"
run suggestions amis.Suggestions tp3/amis/amis_mini.txt "$RUN/suggestions"
run tri_asc tri.TriSimple tp3/tri/nombres_mini.txt "$RUN/tri_asc"
run tri_desc tri.TriSimple -D tri.ordre=desc tp3/tri/nombres_mini.txt "$RUN/tri_desc"
run tri_grand tri.TriSimple -D tri.reducers=4 tp3/tri/uniforme_1M.txt "$RUN/tri_grand"
run tri_biaise tri.TriSimple -D tri.reducers=4 tp3/tri/biaise_1M.txt "$RUN/tri_biaise"
run tri_ech tri.TriEchantillon tp3/tri/biaise_1M.txt "$RUN/tri_ech" 4
run horo horoscope.Horoscope tp3/horoscope/personnes_mini.csv "$RUN/horo"
run horo_ville horoscope.Horoscope -D horoscope.ville=true tp3/horoscope/personnes_mini.csv "$RUN/horo_ville"
run horo_tous horoscope.Horoscope -D horoscope.min=1 tp3/horoscope/personnes_mini.csv "$RUN/horo_tous"
run horo_grand horoscope.Horoscope tp3/horoscope/personnes_100k.csv "$RUN/horo_grand"
sort -n -c traces/tri_grand.txt
sort -n -c traces/tri_biaise.txt
sort -n -c traces/tri_ech.txt
test "$(wc -l < traces/tri_grand.txt)" -eq 1000000
test "$(wc -l < traces/tri_biaise.txt)" -eq 1000000
test "$(wc -l < traces/tri_ech.txt)" -eq 1000000
echo "Sorties HDFS : $RUN ; journaux et sorties locales : traces/"
echo "Captures a joindre : localhost:9870 (Datanodes), localhost:8088 (Nodes)."
