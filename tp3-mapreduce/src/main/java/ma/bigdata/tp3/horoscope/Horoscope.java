package ma.bigdata.tp3.horoscope;
import java.io.*;
import java.util.*;
import java.time.*;
import org.apache.hadoop.conf.*;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.*;
import org.apache.hadoop.mapreduce.lib.output.*;
import org.apache.hadoop.mapreduce.lib.partition.*;
import org.apache.hadoop.util.GenericOptionsParser;

/** Solution du TP, execution via Hadoop. */
public class Horoscope {

static final String[] SIGNES={"Capricorne","Verseau","Poissons","Bélier","Taureau","Gémeaux","Cancer","Lion","Vierge","Balance","Scorpion","Sagittaire"};
static final int[] DEBUT={20,19,21,20,21,21,23,23,23,23,22,22},ORDRE={10,11,12,1,2,3,4,5,6,7,8,9};
static final String[] ANIMAUX={"Rat","Bœuf","Tigre","Lapin","Dragon","Serpent","Cheval","Chèvre","Singe","Coq","Chien","Cochon"};
static int signe(int m,int j){int i=m-1;return j>=DEBUT[i]?(i+1)%12:i;}
public static class SigneMapper extends Mapper<LongWritable,Text,Text,Text>{
protected void map(LongWritable k,Text v,Context c)throws IOException,InterruptedException{String[] f=v.toString().split(",",-1);if(f[0].equals("id")||v.toString().trim().isEmpty())return;if(f.length!=5){c.getCounter("Horoscope","LIGNES_INVALIDES").increment(1);return;}LocalDate d;try{if(!f[3].matches("[0-9]{4}-[0-9]{2}-[0-9]{2}"))throw new IllegalArgumentException();d=LocalDate.parse(f[3]);}catch(Exception e){c.getCounter("Horoscope","DATES_INVALIDES").increment(1);return;}int s=signe(d.getMonthValue(),d.getDayOfMonth());String cle=String.format(Locale.ROOT,"%02d %s",ORDRE[s],SIGNES[s]);if(c.getConfiguration().getBoolean("horoscope.chinois",false)){cle=ANIMAUX[Math.floorMod(d.getYear()-4,12)];if(d.getMonthValue()==1||(d.getMonthValue()==2&&d.getDayOfMonth()<=20))c.getCounter("Horoscope","CHINOIS_DATE_INCERTAINE").increment(1);}if(c.getConfiguration().getBoolean("horoscope.ville",false))cle+=" | "+f[4];c.write(new Text(cle),new Text(f[1]+" "+f[2]));}}
public static class GroupeReducer extends Reducer<Text,Text,Text,Text>{protected void reduce(Text k,Iterable<Text> vs,Context c)throws IOException,InterruptedException{List<String>l=new ArrayList<>();for(Text v:vs)l.add(v.toString());if(l.size()<c.getConfiguration().getInt("horoscope.min",2))return;Collections.sort(l);c.write(k,new Text(l.size()+"\t"+String.join(", ",l)));}}

public static void main(String[] args) throws Exception {
Configuration conf=new Configuration(); String[] a=new GenericOptionsParser(conf,args).getRemainingArgs();
if(a.length!=2) throw new IllegalArgumentException("Usage: [-D cle=valeur] entree sortie");
Job job=Job.getInstance(conf,"TP3 - Horoscope"); job.setJarByClass(Horoscope.class);
job.setMapperClass(SigneMapper.class); job.setReducerClass(GroupeReducer.class);
job.setOutputKeyClass(Text.class); job.setOutputValueClass(Text.class);

FileInputFormat.addInputPath(job,new Path(a[0])); FileOutputFormat.setOutputPath(job,new Path(a[1]));
System.exit(job.waitForCompletion(true)?0:1); }
}
