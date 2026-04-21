#!/bin/bash
set -euo pipefail

JAVA_HOME="${JAVA_HOME:-/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home}"
NEO4J_HOME="${NEO4J_HOME:-/opt/homebrew/Cellar/neo4j/2026.03.1/libexec}"

exec "$JAVA_HOME/bin/java" \
  -cp "$NEO4J_HOME/plugins/*:$NEO4J_HOME/conf/*:$NEO4J_HOME/lib/*" \
  -XX:+UseG1GC \
  -XX:-OmitStackTraceInFastThrow \
  -XX:+AlwaysPreTouch \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+TrustFinalNonStaticFields \
  -XX:+DisableExplicitGC \
  -Djdk.nio.maxCachedBufferSize=1024 \
  -Dio.netty.tryReflectionSetAccessible=true \
  -Dio.netty.leakDetection.level=DISABLED \
  -Djdk.tls.ephemeralDHKeySize=2048 \
  -Djdk.tls.rejectClientInitiatedRenegotiation=true \
  -XX:FlightRecorderOptions=stackdepth=256 \
  -XX:+UnlockDiagnosticVMOptions \
  -XX:+DebugNonSafepoints \
  --add-opens=java.base/java.nio=ALL-UNNAMED \
  --add-opens=java.base/java.io=ALL-UNNAMED \
  --add-opens=java.base/sun.nio.ch=ALL-UNNAMED \
  --add-opens=java.base/java.util.concurrent=ALL-UNNAMED \
  --enable-native-access=ALL-UNNAMED \
  -Dorg.neo4j.shaded.lucene9.vectorization.upperJavaFeatureVersion=25 \
  -Dlog4j2.disable.jmx=true \
  -Dlog4j.layout.jsonTemplate.maxStringLength=32768 \
  -Djava.awt.headless=true \
  -Dunsupported.dbms.udc.source=homebrew \
  -Dfile.encoding=UTF-8 \
  org.neo4j.server.Neo4jCommunity \
  --home-dir="$NEO4J_HOME" \
  --config-dir="$NEO4J_HOME/conf" \
  --console-mode
