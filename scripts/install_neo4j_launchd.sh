#!/bin/bash
set -euo pipefail

SERVICE_DIR="/opt/homebrew/var/jobkg-neo4j"
RUNNER_PATH="$SERVICE_DIR/jobkg-neo4j-java.sh"
PLIST_PATH="$SERVICE_DIR/jobkg.neo4j.plist"
LABEL="jobkg.neo4j"
USER_ID="$(id -u)"

mkdir -p "$SERVICE_DIR"

NEO4J_HOME="$(python - <<'PY'
from pathlib import Path
print(Path('/opt/homebrew/opt/neo4j').resolve() / 'libexec')
PY
)"
JAVA_HOME="$(python - <<'PY'
from pathlib import Path
print(Path('/opt/homebrew/opt/openjdk@21').resolve() / 'libexec/openjdk.jdk/Contents/Home')
PY
)"

sed \
  -e "s#/opt/homebrew/Cellar/neo4j/2026.03.1/libexec#$NEO4J_HOME#g" \
  -e "s#/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home#$JAVA_HOME#g" \
  "$(dirname "$0")/neo4j-java-runner.sh" > "$RUNNER_PATH"
chmod +x "$RUNNER_PATH"
xattr -c "$RUNNER_PATH" 2>/dev/null || true

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$RUNNER_PATH</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>WorkingDirectory</key><string>/opt/homebrew/var/neo4j</string>
  <key>StandardOutPath</key><string>/opt/homebrew/var/log/neo4j.log</string>
  <key>StandardErrorPath</key><string>/opt/homebrew/var/log/neo4j.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
</dict>
</plist>
EOF

launchctl bootout "gui/$USER_ID" "$PLIST_PATH" 2>/dev/null || true
launchctl bootstrap "gui/$USER_ID" "$PLIST_PATH"
launchctl kickstart -k "gui/$USER_ID/$LABEL"

echo "Installed launchd service at $PLIST_PATH"
echo "Check status with: launchctl print gui/$USER_ID/$LABEL | sed -n '1,80p'"
