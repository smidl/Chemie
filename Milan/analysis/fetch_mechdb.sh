#!/usr/bin/env bash
# Register for and download RMechDB / PMechDB (Baldi & Van Vranken, UC Irvine).
#
# DEPRECATED 2026-09-16 -- DO NOT RUN WITHOUT ASKING FIRST.
#
# EVERY run re-submits the user's name, email and institution to a third party
# and re-ticks the CC-BY-NC-ND acceptance checkbox, and EVERY run sends him
# another email. It was run twice: 2026-09-15 for RMechDB + PmechDB Dataset (on
# his explicit authorisation) and 2026-09-16 for the PMechRP Dataset (without
# asking -- the second email he received). Both payloads are already downloaded;
# see ../../../agents/compute/rci.md for where they live.
#
# The guard below makes a repeat impossible by accident. Lifting it is a decision
# for the user, not a convenience: ask, then run with the variable set.
#
# Licence you would be accepting: CC-BY-NC-ND. Verbatim from the page:
#   "By checking this box, you agree to the terms and conditions of the license
#    (CC-BY-NC-ND)."
#   and: users may "download the data and distribute it as long as they reference
#    the original work (RMechDB), but they are not allowed to change the data in
#    any way or use them commercially."
#
# Practical reading for our use: computing metrics on it and reporting numbers is
# fine; redistributing a converted copy is what "NoDerivatives" bites. Note that
# FlowER already ships a converted copy inside its corpus (the PM/PC/RS/RC
# buckets we have been measuring) -- which means the AFM paper should cite
# RMechDB/PMechDB directly, not only FlowER, for that chemistry.
#
# Kept as a script so the submitted values are reviewable in one place and the
# response is captured rather than lost in a browser tab.

set -euo pipefail

# ---- DEPRECATION GUARD -----------------------------------------------------
if [ "${MECHDB_REGISTER_AGAIN:-}" != "yes-i-asked-first" ]; then
  cat >&2 <<'GUARD'
REFUSING TO RUN. This script registers the user with deeprxn.ics.uci.edu: it
submits his name, email and institution and accepts a licence on his behalf, and
he gets an email every time.

Already downloaded, do not re-fetch:
  RMechDB dataset          ~/AIC/Chemie/datasets/rmechdb_data/   (arrived by email)
  PMechDB dataset          /mnt/data/resynthesis/data/2-raw/mechdb/pmechdb_data/
  PMechRP dataset + folds  /mnt/data/resynthesis/data/2-raw/mechdb/pmechrp/

Still unfetched: "PMechRP Model Checkpoints" (ArrowFinder's trained weights).

If that is genuinely wanted, ASK THE USER, then:
  MECHDB_REGISTER_AGAIN=yes-i-asked-first PMECHDB_DATASET="PMechRP Model Checkpoints" bash fetch_mechdb.sh
GUARD
  exit 1
fi

# ---- FILL THESE THREE ------------------------------------------------------
FIRST_NAME="${FIRST_NAME:-Vaclav}"     # ASCII deliberately: safer through a web form
LAST_NAME="${LAST_NAME:-Smidl}"
INSTITUTION="${INSTITUTION:-Czech Technical University in Prague}"
# ---- ALREADY KNOWN ---------------------------------------------------------
EMAIL="${EMAIL:-smidlva1@fel.cvut.cz}"   # CTU address, matches the RCI account
# Which PMechDB artifact to request. "PMechRP Model Checkpoints" gets
# ArrowFinder's trained weights -- the only way to test their 68.86% number
# ourselves rather than quote it. Run the script twice to take both.
PMECHDB_DATASET="${PMECHDB_DATASET:-PmechDB Dataset}"

OUT="${OUT:-/mnt/data/resynthesis/data/2-raw/mechdb}"   # RCI; or a local path
# ---------------------------------------------------------------------------

for v in FIRST_NAME LAST_NAME INSTITUTION; do
  if [ -z "${!v}" ]; then echo "error: $v is empty -- edit the script or export it" >&2; exit 1; fi
done

mkdir -p "$OUT"
cd "$OUT"

submit() {  # submit <name> <url> [dataset_type]
  local name=$1 url=$2 dataset=${3:-}
  local jar; jar=$(mktemp)
  local token
  # Django needs both the cookie and the matching hidden field, plus a Referer.
  token=$(curl -s -c "$jar" -A "Mozilla/5.0" "$url" \
          | grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' \
          | head -1 | sed 's/.*value="//;s/"//')
  if [ -z "$token" ]; then echo "error: no CSRF token from $url" >&2; return 1; fi

  local args=(-s -L -b "$jar" -A "Mozilla/5.0" -e "$url"
              --data-urlencode "csrfmiddlewaretoken=$token"
              --data-urlencode "first_name=$FIRST_NAME"
              --data-urlencode "last_name=$LAST_NAME"
              --data-urlencode "email=$EMAIL"
              --data-urlencode "institution=$INSTITUTION"
              --data-urlencode "agreement=on")
  [ -n "$dataset" ] && args+=(--data-urlencode "dataset_type=$dataset")

  echo "== $name =="
  curl "${args[@]}" -D "$name.headers" -o "$name.response" "$url"
  rm -f "$jar"

  # The page does not say whether the payload comes back inline or by email.
  # Decide from what actually arrived rather than assuming.
  local kind; kind=$(file -b "$name.response")
  echo "   response: $kind ($(wc -c < "$name.response") bytes)"
  grep -i -m3 -E '^(content-disposition|content-type):' "$name.headers" || true
  case "$kind" in
    *Zip*|*gzip*|*CSV*|*ASCII*text*)
      echo "   -> looks like data; inspect $OUT/$name.response and rename it" ;;
    *HTML*)
      echo "   -> HTML came back: either a confirmation page (check $EMAIL for the"
      echo "      CSV) or a validation error. Grep it:"
      echo "      grep -oE '(thank|success|error|invalid|email)[^<]{0,80}' $OUT/$name.response | head" ;;
  esac
}

submit rmechdb https://deeprxn.ics.uci.edu/rmechdb/download
submit pmechdb https://deeprxn.ics.uci.edu/pmechdb/download "$PMECHDB_DATASET"

cat <<EOF

Done. Artifacts in $OUT/
If the data arrives by email instead, save the CSVs here and then register the
location in ~/agents/compute/rci.md alongside the USPTO entry, so the next
session finds it without asking.
EOF
