import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.lang.reflect.Method;
import java.time.LocalDate;
import java.util.*;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.*;
import ma.bigdata.tp3.tri.TriSimple;
public class VerificationJava {
 public static void main(String[] args)throws Exception{
  Class<?> h=Class.forName("ma.bigdata.tp3.horoscope.Horoscope");Method m=h.getDeclaredMethod("signe",int.class,int.class);m.setAccessible(true);
  int[] starts={20,19,21,20,21,21,23,23,23,23,22,22};int tests=0;
  for(int month=1;month<=12;month++){int before=(Integer)m.invoke(null,month,starts[month-1]-1),after=(Integer)m.invoke(null,month,starts[month-1]);if(before!=month-1||after!=month%12)throw new AssertionError("Frontiere "+month);tests+=2;}
  if(LocalDate.of(2004,2,29).getDayOfMonth()!=29)throw new AssertionError();
  for(String invalid:Arrays.asList("2005-02-29","2004-13-02")){try{LocalDate.parse(invalid);throw new AssertionError(invalid);}catch(java.time.DateTimeException expected){tests++;}}
  TriSimple.PlagePartitioner p=new TriSimple.PlagePartitioner();Configuration c=new Configuration(false);c.setLong("tri.max",999999);p.setConf(c);
  long[] ns={-1,0,249999,250000,499999,500000,749999,750000,999999,1000000};int[] want={0,0,0,1,1,2,2,3,3,3};
  for(int i=0;i<ns.length;i++){if(p.getPartition(new LongWritable(ns[i]),NullWritable.get(),4)!=want[i])throw new AssertionError("Plage asc");tests++;}
  c.set("tri.ordre","desc");p.setConf(c);for(int i=0;i<ns.length;i++){if(p.getPartition(new LongWritable(ns[i]),NullWritable.get(),4)!=3-want[i])throw new AssertionError("Plage desc");tests++;}
  Set<String> stop=new HashSet<>(Arrays.asList("le,la,les,de,des,dans,en,un,une,et,au,ce,l,il,son,par,puis".split(",")));int kept=0,ignored=0,empty=0;
  for(Path file:Files.newDirectoryStream(Paths.get(args[0]),"*.txt"))for(String line:Files.readAllLines(file,StandardCharsets.UTF_8))for(String w:line.toLowerCase(Locale.ROOT).split("[^\\p{L}]+")){if(w.isEmpty()||w.length()<2||stop.contains(w)){ignored++;if(w.isEmpty())empty++;}else kept++;}
  if(kept!=51)throw new AssertionError("Mots conserves");tests++;
  Set<Integer> reducers=new TreeSet<>();for(String key:Arrays.asList("01 Bélier","02 Taureau","03 Gémeaux","04 Cancer","05 Lion","06 Vierge","07 Balance","08 Scorpion","09 Sagittaire","10 Capricorne","11 Verseau","12 Poissons"))reducers.add((new Text(key).hashCode()&Integer.MAX_VALUE)%20);
  System.out.println("Verifications Java reussies : "+tests+"; GARDES="+kept+"; IGNORES="+ignored+"; tokens vides="+empty+"; reducers distincts pour les 12 signes/20="+reducers.size()+" "+reducers);
 }
}
