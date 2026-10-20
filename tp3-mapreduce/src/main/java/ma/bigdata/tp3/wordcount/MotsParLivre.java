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
public class MotsParLivre {

public static class LivreMapper extends Mapper<LongWritable,Text,Text,Text>{
private String livre; protected void setup(Context c){livre=((FileSplit)c.getInputSplit()).getPath().getName().replaceFirst("\\.txt$","");}
protected void map(LongWritable k,Text v,Context c)throws IOException,InterruptedException{for(String s:v.toString().toLowerCase(Locale.ROOT).split("[^\\p{L}]+"))if(s.length()>=3)c.write(new Text(s),new Text(livre));}}
public static class LivresReducer extends Reducer<Text,Text,Text,Text>{
protected void reduce(Text k,Iterable<Text> vs,Context c)throws IOException,InterruptedException{Map<String,Integer> m=new TreeMap<>();for(Text v:vs){String s=v.toString();m.put(s,m.getOrDefault(s,0)+1);}if(m.size()>=c.getConfiguration().getInt("mpl.livres.min",1))c.write(k,new Text(m.size()+"\t"+m));}}

public static void main(String[] args) throws Exception {
Configuration conf=new Configuration(); String[] a=new GenericOptionsParser(conf,args).getRemainingArgs();
if(a.length!=2) throw new IllegalArgumentException("Usage: [-D cle=valeur] entree sortie");
Job job=Job.getInstance(conf,"TP3 - MotsParLivre"); job.setJarByClass(MotsParLivre.class);
job.setMapperClass(LivreMapper.class); job.setReducerClass(LivresReducer.class);
job.setOutputKeyClass(Text.class); job.setOutputValueClass(Text.class);

FileInputFormat.addInputPath(job,new Path(a[0])); FileOutputFormat.setOutputPath(job,new Path(a[1]));
System.exit(job.waitForCompletion(true)?0:1); }
}
