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
  scp "$1:link_costs_*" .
  popd
}

start_time=`date +%s`

for host in "${HOSTS[@]}";
do
  pushd .
  mkdir -p measurements && cd measurements
  fetch_result $host
  popd
done

tail measurements/**/*.txt > measurements/results_summary

end_time=`date +%s`
total_running_time=$((end_time - start_time))
echo "All results fetched in $total_running_time seconds"