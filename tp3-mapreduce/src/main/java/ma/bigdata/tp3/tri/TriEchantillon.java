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
public class TriEchantillon {
public static class ClesReducer extends Reducer<Text,Text,Text,NullWritable>{protected void reduce(Text k,Iterable<Text> vs,Context c)throws IOException,InterruptedException{for(Text v:vs)c.write(k,NullWritable.get());}}
public static void main(String[] args)throws Exception{
Configuration conf=new Configuration();String[] a=new GenericOptionsParser(conf,args).getRemainingArgs();if(a.length!=3)throw new IllegalArgumentException("Usage: entree sortie reducers");int r=Integer.parseInt(a[2]);if(r<2)throw new IllegalArgumentException("Au moins 2 reducers");
Job job=Job.getInstance(conf,"TP3 - tri echantillonne");job.setJarByClass(TriEchantillon.class);job.setInputFormatClass(KeyValueTextInputFormat.class);job.setMapperClass(Mapper.class);job.setReducerClass(ClesReducer.class);job.setMapOutputKeyClass(Text.class);job.setMapOutputValueClass(Text.class);job.setOutputKeyClass(Text.class);job.setOutputValueClass(NullWritable.class);job.setNumReduceTasks(r);
FileInputFormat.addInputPath(job,new Path(a[0]));FileOutputFormat.setOutputPath(job,new Path(a[1]));Path bornes=new Path(a[1]+"_bornes");TotalOrderPartitioner.setPartitionFile(job.getConfiguration(),bornes);InputSampler.writePartitionFile(job,new InputSampler.RandomSampler<Text,Text>(0.1,10000,10));job.setPartitionerClass(TotalOrderPartitioner.class);System.exit(job.waitForCompletion(true)?0:1);}}
