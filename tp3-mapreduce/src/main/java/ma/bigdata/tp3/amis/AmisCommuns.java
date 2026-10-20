package ma.bigdata.tp3.amis;
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
public class AmisCommuns {

public static class PaireMapper extends Mapper<LongWritable,Text,Text,Text>{
protected void map(LongWritable k,Text v,Context c)throws IOException,InterruptedException{String[] f=v.toString().split(":",-1);if(f.length!=2||f[0].trim().isEmpty()){c.getCounter("Amis","LIGNES_INVALIDES").increment(1);return;}String p=f[0].trim();Set<String> amis=new TreeSet<>();for(String x:f[1].split(","))if(!x.trim().isEmpty()&&!x.trim().equals(p))amis.add(x.trim());String liste=String.join(",",amis);for(String x:amis)c.write(new Text(p.compareTo(x)<0?p+","+x:x+","+p),new Text(liste));}}
public static class IntersectionReducer extends Reducer<Text,Text,Text,Text>{
protected void reduce(Text k,Iterable<Text> vs,Context c)throws IOException,InterruptedException{List<Set<String>> l=new ArrayList<>();for(Text v:vs)l.add(new TreeSet<>(Arrays.asList(v.toString().split(","))));if(l.size()!=2){c.getCounter("Amis","AMITIES_A_SENS_UNIQUE").increment(1);return;}l.get(0).retainAll(l.get(1));c.write(k,new Text(l.get(0).toString()));}}

public static void main(String[] args) throws Exception {
Configuration conf=new Configuration(); String[] a=new GenericOptionsParser(conf,args).getRemainingArgs();
if(a.length!=2) throw new IllegalArgumentException("Usage: [-D cle=valeur] entree sortie");
Job job=Job.getInstance(conf,"TP3 - AmisCommuns"); job.setJarByClass(AmisCommuns.class);
job.setMapperClass(PaireMapper.class); job.setReducerClass(IntersectionReducer.class);
job.setOutputKeyClass(Text.class); job.setOutputValueClass(Text.class);

FileInputFormat.addInputPath(job,new Path(a[0])); FileOutputFormat.setOutputPath(job,new Path(a[1]));
System.exit(job.waitForCompletion(true)?0:1); }
}
