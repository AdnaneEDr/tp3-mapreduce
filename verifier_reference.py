from pathlib import Path
from collections import Counter,defaultdict
import re,csv,datetime,json,random,bisect,shutil,urllib.request
r=Path(__file__).resolve().parent; d=r/'donnees'; out=r/'resultats'; out.mkdir(exist_ok=True)
def save(name,lines):
    s='\n'.join(lines)+'\n';(out/name).write_text(s,encoding='utf8');return s
def tokens(s):
    import unicodedata
    normalized=''.join(c if unicodedata.category(c).startswith('L') else ' ' for c in s.lower())
    return normalized.split()
stop=set('le,la,les,de,des,dans,en,un,une,et,au,ce,l,il,son,par,puis'.split(','))
books={p.stem:tokens(p.read_text(encoding='utf8')) for p in (d/'ex1_livres/mini').glob('*.txt')}
c=Counter(w for b in books.values() for w in b if len(w)>=2 and w not in stop)
wc=save('wc2.txt',[f'{w}\t{n}' for w,n in sorted(c.items())]);top=c.most_common();top=sorted(c.items(),key=lambda x:(-x[1],x[0]))[:5]
mpl=[]
for w in sorted(set(w for b in books.values() for w in b if len(w)>=3)):
    counts={k:b.count(w) for k,b in sorted(books.items()) if w in b}
    if len(counts)>=2:mpl.append(f'{w}\t{len(counts)}\t'+str(counts))
mpls=save('mots_par_livre.txt',mpl)
g={p:set(a.split(',')) for p,a in (x.split(':') for x in (d/'ex2_amis/amis_mini.txt').read_text().splitlines())}
amis=save('amis_communs.txt',[f'{p},{q}\t{sorted(g[p]&g[q])}' for p in sorted(g) for q in sorted(g[p]) if p<q and p in g[q]])
sug=[]
for p in sorted(g):
    cand=sorted([(q,len(g[p]&g[q])) for q in g if q!=p and q not in g[p] and g[p]&g[q]],key=lambda x:(-x[1],x[0]))[:3]
    sug.append(p+'\t'+(', '.join(f'{q} ({n} en commun)' for q,n in cand) or '[]'))
sugs=save('suggestions.txt',sug)
nums=sorted(map(int,(d/'ex4_tri/nombres_mini.txt').read_text().split()))
save('tri_asc.txt',map(str,nums));save('tri_desc.txt',map(str,reversed(nums)))
parts={}
for filename in ['uniforme_1M.txt','biaise_1M.txt']:
    ns=sorted(map(int,(d/'ex4_tri'/filename).read_text().split())); buckets=[[] for _ in range(4)]
    for n in ns:buckets[min(3,n*4//1000000)].append(n)
    stats=[{'reducer':i,'lignes':len(b),'premiere':b[0],'derniere':b[-1]} for i,b in enumerate(buckets)]
    parts[filename]=stats
    for i,b in enumerate(buckets):save(filename.replace('.txt','')+f'_part-r-{i:05d}.txt',map(str,b))
    assert sum(map(len,buckets))==1000000
    assert [n for b in buckets for n in b]==ns
    if filename.startswith('biaise'):
        sample=sorted(random.Random(2026).sample(ns,10000));bounds=[sample[len(sample)*i//4] for i in range(1,4)];counts=Counter(bisect.bisect_right(bounds,n) for n in ns)
        parts['simulation_echantillon']={'bornes':bounds,'effectifs':[counts[i] for i in range(4)],'note':'Simulation Python deterministe; pas une execution InputSampler Hadoop.'}
signs=['Capricorne','Verseau','Poissons','Bélier','Taureau','Gémeaux','Cancer','Lion','Vierge','Balance','Scorpion','Sagittaire'];starts=[20,19,21,20,21,21,23,23,23,23,22,22];order=[10,11,12,1,2,3,4,5,6,7,8,9]
def horoscope(file,city=False):
    groups=defaultdict(list); invalid=0
    for row in csv.DictReader(file.open(encoding='utf8')):
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',row['date_naissance']):raise ValueError()
            date=datetime.date.fromisoformat(row['date_naissance'])
        except ValueError:invalid+=1;continue
        i=date.month-1;s=(i+1)%12 if date.day>=starts[i] else i;key=f'{order[s]:02d} {signs[s]}'+(' | '+row['ville'] if city else '')
        groups[key].append(row['prenom']+' '+row['nom'])
    return groups,invalid
h,inv=horoscope(d/'ex5_horoscope/personnes_mini.csv');hc,_=horoscope(d/'ex5_horoscope/personnes_mini.csv',True)
hs=save('horoscope.txt',[f'{k}\t{len(v)}\t'+', '.join(sorted(v)) for k,v in sorted(h.items()) if len(v)>=2]);hcs=save('horoscope_ville.txt',[f'{k}\t{len(v)}\t'+', '.join(sorted(v)) for k,v in sorted(hc.items()) if len(v)>=2])
hg,ig=horoscope(d/'ex5_horoscope/personnes_100k.csv');assert ig==486 and sum(map(len,hg.values()))==99514
save('horoscope_100k_effectifs.txt',[f'{k}\t{len(v)}' for k,v in sorted(hg.items())])
gainmini=sum(len(set(w for w in b if len(w)>=2 and w not in stop)) for b in books.values())
(out/'verification.json').write_text(json.dumps({'wc_gardes':sum(c.values()),'wc_ignores_tokens':sum(len(b) for b in books.values())-sum(c.values()),'wc_reduce_output':len(c),'wc_combiner_ideal_par_fichier':gainmini,'tri':parts,'horoscope_invalides':inv,'horoscope_grand_invalides':ig},ensure_ascii=False,indent=2),encoding='utf8')
# Le corpus Q7 exact est téléchargé, sans confondre les 18 livres fournis avec les 5 demandés.
gut=d/'gutenberg_5';gut.mkdir(exist_ok=True);download=[]
for ident in [1342,84,11,2701,1661]:
    p=gut/f'livre_{ident}.txt'
    try:
        if not p.exists():p.write_bytes(urllib.request.urlopen(f'https://www.gutenberg.org/cache/epub/{ident}/pg{ident}.txt',timeout=30).read())
        download.append(p)
    except Exception as e:print('Gutenberg indisponible',ident,str(e))
q7=''
if len(download)==5:
    eng=set('the,of,and,to,a,in,i,it,that,was,he,you,his,her,as,with,for,had,is,my,on,at,be,not,but,she,me,so,by,all'.split(','))
    for filtered in [False,True]:
        lists=[[w for w in tokens(p.read_text(encoding='utf-8-sig')) if not filtered or w not in eng] for p in download]; cc=Counter(w for b in lists for w in b);ni=sum(map(len,lists));no=sum(len(set(b)) for b in lists)
        q7+=f"\n{'Avec filtre' if filtered else 'Sans filtre'} : top 5 {sorted(cc.items(),key=lambda x:(-x[1],x[0]))[:5]}. {ni} occurrences ; {no} paires après une combinaison idéale par fichier, gain {100*(1-no/ni):.2f} %.\n"
        save('gutenberg_'+('filtre' if filtered else 'sans_filtre')+'.txt',[f'{w}\t{n}' for w,n in sorted(cc.items())])
else:q7='Téléchargement du corpus exact incomplet : Q7 doit être exécutée sur les cinq fichiers demandés. Les 18 livres fournis ne constituent pas ce corpus.'
report=f'''# Compte rendu - TP 3 MapReduce en action

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

**Q5.** wc2 : GARDES={sum(c.values())}, IGNORES={sum(len(b) for b in books.values())-sum(c.values())} tokens rejetés non vides, Map output records={sum(c.values())}, Reduce output records={len(c)}. Le squelette compte aussi les chaînes vides produites par split : le compteur IGNORES effectif est donc à lire dans le journal Hadoop, plutôt qu'à assimiler automatiquement au nombre de mots rejetés. Avec une combinaison complète par fichier, Combine output records={gainmini}. La combinaison peut être exécutée zéro, une ou plusieurs fois ; ses compteurs exacts dépendent de l'exécution. Top 5, départagés par mot : {top}. Le Combiner additionne localement, réduisant les paires du shuffle sans modifier les totaux.

**Q6.** Sortie :
```text
{mpls}```
Le reducer ne peut pas être réutilisé comme Combiner : il reçoit des noms de livres mais produit un nombre et une représentation de dictionnaire. Les types sémantiques diffèrent et le seuil de livres ne doit pas être appliqué localement. Une combinaison adaptée utiliserait (mot,livre) et un compteur, puis une seconde agrégation.

**Q7.** Corpus exact : identifiants Gutenberg 1342, 84, 11, 2701 et 1661. Les fichiers téléchargés sont joints ; en-têtes et licences conservés, comme dans la commande de l'énoncé. Résultats de référence calculés le 13 octobre 2026, avec longueur minimale 1 et la liste exacte de mots vides de Q7 :
{q7}
Les gains ci-dessus sont des calculs de combinaison idéale par fichier, et non des compteurs Hadoop relevés. Les fichiers Gutenberg peuvent changer ; les copies jointes fixent l'entrée pour la reproduction.

## Exercice 2 - Amis
**Q8.** (Amina,Bilal ; Bilal,Chaima,Driss), (Amina,Chaima ; Bilal,Chaima,Driss), (Amina,Driss ; Bilal,Chaima,Driss). La paire canonique triée rassemble les émissions A→B et B→A sous la même clé.

**Q9.** Bilal,Chaima reçoit les listes Amina,Chaima,Driss,Elias et Amina,Bilal,Driss,Elias. Intersection : [Amina, Driss, Elias]. Les Text Hadoop sont réutilisés : leur contenu est copié dans des ensembles.

**Q10.** Sortie complète :
```text
{amis}```
Map output records=18 (3+4+4+4+3 liens dirigés), Reduce input groups=9 (9 arêtes non orientées). Chaque groupe possède 2 listes.

**Q11.** Farid ajoute 2 émissions ; 20 sorties Map et 11 groupes Reduce, mais seulement 9 lignes finales. AMITIES_A_SENS_UNIQUE=2 : Amina,Farid et Bilal,Farid ne reçoivent qu'une liste.

**Q12.** Pas de Combiner fondé sur le reducer proposé : il peut recevoir une seule liste et supprimer une paire valide avant le shuffle. Pour d=5000 amis, 5000 émissions transportent chacune une liste de 5000 noms, soit environ 25 millions de références à des noms : volume O(d²). L'intersection coûte O(dA+dB) par paire avec des ensembles de hachage, avec un surcoût logarithmique pour les TreeSet ; le tri rend la sortie déterministe. Le bonus Suggestions génère d(d-1)=24 995 000 candidatures orientées.

**Q13.**
```text
{sugs}```
Amina et Elias ne sont pas amis ; Bilal, Chaima et Driss sont leurs trois amis communs. Toutes les autres paires sont déjà directes.

## Exercice 3 - Tri (sections 4.x du PDF)
**Q20.** Le shuffle trie les clés Map dans chaque partition avant le Reduce. Map émet (nombre,NullWritable), car seule la clé est utile. Le reducer réécrit la clé une fois par valeur : sinon les doublons disparaîtraient. Aucun Combiner ne doit supprimer les occurrences.

**Q21.** Croissant : {nums}. Décroissant : {list(reversed(nums))}. La ligne `job.setSortComparatorClass(LongWritable.DecreasingComparator.class)` inverse l'ordre. Avec plusieurs reducers, les indices des plages sont également inversés.

**Q22.** Résultats exacts sur uniforme_1M.txt :
| Reducer | Lignes | Première | Dernière |
|---|---:|---:|---:|
'''
for p in parts['uniforme_1M.txt']:report+=f"| {p['reducer']} | {p['lignes']} | {p['premiere']} | {p['derniere']} |\n"
report+=f'''
Les plages sont [0,250000[, [250000,500000[, [500000,750000[, [750000,1000000[. Les partitions sont disjointes et ordonnées ; chaque fichier est trié. Les concaténer par indice donne donc un tri global. La vérification indépendante conserve le million d'éléments, y compris les doublons, et compare la concaténation au tri intégral de l'entrée.

**Q23.** Plages fixes sur biaise_1M : {[p['lignes'] for p in parts['biaise_1M.txt']]}. Simulation d'un échantillon de 10000 valeurs, graine 2026 : {parts['simulation_echantillon']}. Les valeurs exactes Hadoop varieront : RandomSampler échantillonne jusqu'à 10 splits, puis writePartitionFile calcule les bornes. TotalOrderPartitioner affecte les clés aux plages obtenues. L'échantillonnage vise des quantiles, pas des intervalles numériques égaux, d'où un meilleur équilibre. Sur 7 chiffres, l'ordre lexicographique Text coïncide avec l'ordre numérique pour les entiers non négatifs : 0000042 < 0000100. Sans remplissage, "100" < "42". Ne pas utiliser ce format pour des nombres négatifs ou de largeur variable.

## Exercice 4 - Horoscope (sections 5.x)
**Q24.** 2004-03-25 : Bélier ; 2005-01-19 : Capricorne ; 2004-01-20 : Verseau ; 2003-12-21 : Sagittaire ; 2004-06-21 : Cancer ; 2005-06-20 : Gémeaux. Ces cas testent les frontières inclusives, particulièrement le passage janvier et juin. 2005-02-29 est impossible (année non bissextile) ; 2004-13-02 a un mois invalide. On incrémente DATES_INVALIDES et on ne les émet pas. LocalDate.parse vérifie réellement le calendrier ; le format AAAA-MM-JJ est imposé.

**Q25.** Map émet ("01 Bélier", "Amina Alaoui"), ou ("01 Bélier | Rabat", "Amina Alaoui") en mode ville. Le préfixe 01-12 donne l'ordre zodiacal par le tri des clés, au lieu de l'ordre alphabétique des signes. Avec plusieurs reducers, l'ordre global des signes nécessite un partitionnement adapté ou une fusion finale.

**Q26.**
```text
{hs}```
DATES_INVALIDES=2 ; 18 personnes valides, dont 4 omises avec le seuil 2 : Salma (Gémeaux), Omar (Cancer), Nora (Sagittaire), Yasmine (Lion) n'est pas omise : le Lion contient quatre personnes. Correction du décompte : les seuls groupes unitaires sont Gémeaux, Cancer et Sagittaire, donc 3 personnes omises et 15 affichées.

**Q27.**
```text
{hcs}```
Le groupe Lion devient Lion | Fès avec Chaima et Jalil ; Fatima est à Agadir et Yasmine à Casablanca, chacune dans un groupe de taille 1 filtré. Le seuil porte sur chaque couple signe-ville.

**Q28.** Il existe seulement 12 clés : au plus 12 reducers reçoivent des données, et les collisions de hachage peuvent réduire encore ce nombre. 20 reducers ne garantissent donc pas 12 actifs. Les gros groupes imposent un fort coût mémoire si l'on stocke tous les noms. Pour des effectifs, additionner avec Combiner ; pour toutes les personnes, utiliser une clé (signe,identifiant) et diffuser plusieurs fragments par signe, ou une agrégation en deux étapes avec salage. Ajouter la ville augmente les clés seulement si le regroupement demandé l'autorise.

**Bonus chinois.** Option horoscope.chinois=true : animal=(année-4) modulo 12. Compteur CHINOIS_DATE_INCERTAINE pour janvier et les 20 premiers jours de février. Le résultat reste une approximation signalée, car les dates du Nouvel An chinois ne sont pas fournies.

## Exécution et pièces à compléter
Voir README.md et executer_tp.sh. Après lancement du cluster : joindre les captures réelles des interfaces, la dernière ligne de pi et les compteurs Combine de Q5/Q7. Les données jointes de jointure restent disponibles mais aucune question correspondante ne figure dans cet énoncé réduit.
'''
# Supprimer la formulation de travail et garder uniquement la conclusion vérifiée.
report=report.replace("DATES_INVALIDES=2 ; 18 personnes valides, dont 4 omises avec le seuil 2 : Salma (Gémeaux), Omar (Cancer), Nora (Sagittaire), Yasmine (Lion) n'est pas omise : le Lion contient quatre personnes. Correction du décompte : les seuls groupes unitaires sont Gémeaux, Cancer et Sagittaire, donc 3 personnes omises et 15 affichées.","DATES_INVALIDES=2 ; 18 personnes valides. Les trois groupes unitaires, Gémeaux (Salma), Cancer (Omar) et Sagittaire (Nora), sont filtrés : 3 personnes omises et 15 affichées.")
(r/'resultats/COMPTE_RENDU_REFERENCE.md').write_text(report,encoding='utf8')
assert sum(len(v) for v in h.values() if len(v)>=2)==15
print(json.dumps({'top5':top,'gardes':sum(c.values()),'distincts':len(c),'combiner_ideal':gainmini,'horoscope_sortie':hs,'gutenberg_fichiers':len(download)},ensure_ascii=False,indent=2))
