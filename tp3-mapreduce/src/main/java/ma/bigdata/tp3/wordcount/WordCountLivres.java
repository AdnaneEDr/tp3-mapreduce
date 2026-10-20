package ma.bigdata.tp3.wordcount;
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
public class WordCountLivres {

public static class MotMapper extends Mapper<LongWritable,Text,Text,IntWritable> {
private final Set<String> stop=new HashSet<>(); private int min;
protected void setup(Context c){min=c.getConfiguration().getInt("wc.longueur.min",1); for(String s:c.getConfiguration().get("wc.mots.vides","").split(",")) if(!s.trim().isEmpty())stop.add(s.trim().toLowerCase(Locale.ROOT));}
protected void map(LongWritable k,Text v,Context c)throws IOException,InterruptedException{
for(String s:v.toString().toLowerCase(Locale.ROOT).split("[^\\p{L}]+")){
if(s.isEmpty()||s.length()<min||stop.contains(s))c.getCounter("Mots","IGNORES").increment(1);
else{c.getCounter("Mots","GARDES").increment(1);c.write(new Text(s),new IntWritable(1));}}}}
public static class SommeReducer extends Reducer<Text,IntWritable,Text,IntWritable>{
protected void reduce(Text k,Iterable<IntWritable> vs,Context c)throws IOException,InterruptedException{int n=0;for(IntWritable v:vs)n+=v.get();c.write(k,new IntWritable(n));}}

public static void main(String[] args) throws Exception {
Configuration conf=new Configuration(); String[] a=new GenericOptionsParser(conf,args).getRemainingArgs();
if(a.length!=2) throw new IllegalArgumentException("Usage: [-D cle=valeur] entree sortie");
Job job=Job.getInstance(conf,"TP3 - WordCountLivres"); job.setJarByClass(WordCountLivres.class);
job.setMapperClass(MotMapper.class); job.setReducerClass(SommeReducer.class);
job.setOutputKeyClass(Text.class); job.setOutputValueClass(IntWritable.class);
job.setCombinerClass(SommeReducer.class);
FileInputFormat.addInputPath(job,new Path(a[0])); FileOutputFormat.setOutputPath(job,new Path(a[1]));
System.exit(job.waitForCompletion(true)?0:1); }
}
