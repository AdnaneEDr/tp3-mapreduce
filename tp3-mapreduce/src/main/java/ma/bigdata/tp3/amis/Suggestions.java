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
public class Suggestions {

public static class CandidatMapper extends Mapper<LongWritable,Text,Text,Text>{
protected void map(LongWritable k,Text v,Context c)throws IOException,InterruptedException{String[] f=v.toString().split(":",-1);if(f.length!=2||f[0].trim().isEmpty()){c.getCounter("Amis","LIGNES_INVALIDES").increment(1);return;}String p=f[0].trim();Set<String> a=new TreeSet<>();for(String x:f[1].split(","))if(!x.trim().isEmpty()&&!x.trim().equals(p))a.add(x.trim());c.write(new Text(p),new Text("S:"));for(String x:a){c.write(new Text(p),new Text("D:"+x));for(String y:a)if(!x.equals(y))c.write(new Text(x),new Text("C:"+y));}}}
public static class TopReducer extends Reducer<Text,Text,Text,Text>{
protected void reduce(Text k,Iterable<Text> vs,Context c)throws IOException,InterruptedException{Set<String>d=new HashSet<>();Map<String,Integer>m=new HashMap<>();for(Text v:vs){String s=v.toString(),x=s.substring(2);if(s.startsWith("D:"))d.add(x);else if(s.startsWith("C:"))m.put(x,m.getOrDefault(x,0)+1);}m.remove(k.toString());for(String x:d)m.remove(x);List<String>l=new ArrayList<>(m.keySet());l.sort((x,y)->{int z=Integer.compare(m.get(y),m.get(x));return z!=0?z:x.compareTo(y);});List<String>out=new ArrayList<>();for(int i=0;i<Math.min(3,l.size());i++){String x=l.get(i);out.add(x+" ("+m.get(x)+" en commun)");}c.write(k,new Text(out.isEmpty()?"[]":String.join(", ",out)));}}

public static void main(String[] args) throws Exception {
Configuration conf=new Configuration(); String[] a=new GenericOptionsParser(conf,args).getRemainingArgs();
if(a.length!=2) throw new IllegalArgumentException("Usage: [-D cle=valeur] entree sortie");
Job job=Job.getInstance(conf,"TP3 - Suggestions"); job.setJarByClass(Suggestions.class);
job.setMapperClass(CandidatMapper.class); job.setReducerClass(TopReducer.class);
job.setOutputKeyClass(Text.class); job.setOutputValueClass(Text.class);

FileInputFormat.addInputPath(job,new Path(a[0])); FileOutputFormat.setOutputPath(job,new Path(a[1]));
System.exit(job.waitForCompletion(true)?0:1); }
}
