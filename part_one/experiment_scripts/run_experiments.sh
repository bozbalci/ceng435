#!/usr/bin/env bash

HOSTS=(
  network-s
  network-r1
  network-r2
  network-r3
  network-d
)

run_experiment () {
  echo "Running experiment server on node $host..."
  ssh "$1" "tmux new -s experiment -d \"python3 ./experiment.py\""
}

kill_server() {
  echo "Killing experiment server on node $host..."
  ssh "$1" "tmux kill-session -t experiment"
}

start_time=`date +%s`

case "$KILL" in
"1")
  for host in "${HOSTS[@]}";
  do
    kill_server $host
  done
  end_time=`date +%s`
  total_running_time=$((end_time - start_time))
  echo "Experiments have been killed $total_running_time seconds"
  ;;
*)
  for host in "${HOSTS[@]}";
  do
    run_experiment $host
  done
  end_time=`date +%s`
  total_running_time=$((end_time - start_time))
  echo "Experiments have been started in $total_running_time seconds"
  ;;
esac

