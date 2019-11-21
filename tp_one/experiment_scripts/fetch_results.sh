#!/usr/bin/env bash

HOSTS=(
  network-s
  network-r1
  network-r2
  network-r3
  network-d
)

fetch_result () {
  echo "Fetching results from $1..."
  pushd .
  mkdir -p -- "$1" && cd -P -- "$1"
  scp "$1:end_to_end_costs*" .
  popd
}

start_time=`date +%s`

rm -rf experiments

for host in "${HOSTS[@]}";
do
  pushd .
  mkdir -p experiments && cd experiments
  fetch_result $host
  popd
done

tail experiments/**/*.json > experiments/results_summary

end_time=`date +%s`
total_running_time=$((end_time - start_time))
echo "All results fetched in $total_running_time seconds"
