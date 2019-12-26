#!/usr/bin/env bash

HOSTS=(
  network-r1
  network-r2
  network-r3
)

run_router () {
  echo "Running experiment server on node $host..."
  ssh "$1" "tmux new -s router -d \"python3 -mprotocol --router\""
}

stop_router () {
  echo "Killing experiment server on node $host..."
  ssh "$1" "tmux kill-session -t router"
}

start_time=`date +%s`

case "$STOP" in
"1")
  for host in "${HOSTS[@]}";
  do
    stop_router $host
  done
  end_time=`date +%s`
  total_running_time=$((end_time - start_time))
  echo "Routers have been stopped in $total_running_time seconds"
  ;;
*)
  for host in "${HOSTS[@]}";
  do
    run_router $host
  done
  end_time=`date +%s`
  total_running_time=$((end_time - start_time))
  echo "Routers have started in $total_running_time seconds"
  ;;
esac

