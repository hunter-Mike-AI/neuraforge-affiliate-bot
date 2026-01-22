 #!/usr/bin/env bash
  set -e
  apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python3-dev cargo
  pip install --no-cache-dir -r requirements.txt


