#!/usr/bin/env bash
# Local checks only; all-rank verdict/collective is a separate required step.
set -euo pipefail
rank="${RANK:-unknown}"
report(){ printf '{"rank":"%s","check":"%s","result":"%s"}\n' "$rank" "$1" "$2"; }
nvidia-smi >/dev/null && report gpu visible
python3 -c 'import torch; assert torch.cuda.is_available(); print(torch.__version__)'
report runtime passed
if [[ -n "${MASTER_ADDR:-}" ]]; then
 python3 -c 'import socket,os; print(socket.getaddrinfo(os.environ["MASTER_ADDR"],None))'
 report dns passed
fi
report local_checks passed
printf '%s\n' 'Local pass is NOT an all-rank pass. Run allreduce.py with a bounded rendezvous.'
