package ma.bigdata.tp3.tri;
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
public class TriSimple {

public static class NombreMapper extends Mapper<LongWritable,Text,LongWritable,NullWritable>{
protected void map(LongWritable k,Text v,Context c)throws IOException,InterruptedException{String s=v.toString().trim();if(s.isEmpty())return;try{c.write(new LongWritable(Long.parseLong(s)),NullWritable.get());}catch(NumberFormatException e){c.getCounter("Tri","LIGNES_INVALIDES").increment(1);}}}
public static class IdentiteReducer extends Reducer<LongWritable,NullWritable,LongWritable,NullWritable>{protected void reduce(LongWritable k,Iterable<NullWritable> vs,Context c)throws IOException,InterruptedException{for(NullWritable v:vs)c.write(k,v);}}
public static class PlagePartitioner extends Partitioner<LongWritable,NullWritable> implements Configurable{
private Configuration conf;private long max;private boolean desc;
public void setConf(Configuration c){conf=c;max=c.getLong("tri.max",999999);if(max<0||max==Long.MAX_VALUE)throw new IllegalArgumentException("tri.max hors limites");desc=c.get("tri.ordre","asc").equals("desc");}public Configuration getConf(){return conf;}
public int getPartition(LongWritable k,NullWritable v,int r){long n=Math.max(0,Math.min(max,k.get()));int p=java.math.BigInteger.valueOf(n).multiply(java.math.BigInteger.valueOf(r)).divide(java.math.BigInteger.valueOf(max+1)).intValue();return desc?r-1-p:p;}}

public static void main(String[] args) throws Exception {
Configuration conf=new Configuration(); String[] a=new GenericOptionsParser(conf,args).getRemainingArgs();
if(a.length!=2) throw new IllegalArgumentException("Usage: [-D cle=valeur] entree sortie");
Job job=Job.getInstance(conf,"TP3 - TriSimple"); job.setJarByClass(TriSimple.class);
job.setMapperClass(NombreMapper.class); job.setReducerClass(IdentiteReducer.class);
job.setOutputKeyClass(LongWritable.class); job.setOutputValueClass(NullWritable.class);
int r=conf.getInt("tri.reducers",1);if(r<1)throw new IllegalArgumentException("tri.reducers >= 1");job.setNumReduceTasks(r);if(r>1)job.setPartitionerClass(PlagePartitioner.class);if(conf.get("tri.ordre","asc").equals("desc"))job.setSortComparatorClass(LongWritable.DecreasingComparator.class);
FileInputFormat.addInputPath(job,new Path(a[0])); FileOutputFormat.setOutputPath(job,new Path(a[1]));
System.exit(job.waitForCompletion(true)?0:1); }
}
