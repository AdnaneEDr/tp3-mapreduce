$ErrorActionPreference = 'Stop'
$tpRoot = Split-Path -Parent $PSScriptRoot
Push-Location (Join-Path $tpRoot 'tp3-mapreduce')
try {
  mvn -q dependency:build-classpath '-Dmdep.outputFile=classpath.txt'
  if ($LASTEXITCODE -ne 0) { throw 'Resolution des dependances impossible' }
  $tpClasspath = (Get-Content -Raw 'classpath.txt').Trim()
  $tpJar = Join-Path $tpRoot 'jobs/tp3.jar'
  javac -encoding UTF-8 -cp "$tpJar;$tpClasspath" (Join-Path $PSScriptRoot 'VerificationJava.java')
  if ($LASTEXITCODE -ne 0) { throw 'Compilation des verifications impossible' }
  java -cp "$PSScriptRoot;$tpJar;$tpClasspath" VerificationJava (Join-Path $tpRoot 'donnees/ex1_livres/mini')
  if ($LASTEXITCODE -ne 0) { throw 'Verification Java echouee' }
} finally { Pop-Location }
