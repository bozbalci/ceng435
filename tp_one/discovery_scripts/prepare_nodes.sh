#!/usr/bin/env bash

HOSTS=(
  network-s
  network-r1
  network-r2
  network-r3
  network-d
)

send_measurement_script () {
  echo "Sending measurement script to $1..."
  scp measure.py "$1:"
}

remove_existing_measurements () {
  echo "Removing existing measurement results in $1..."
  ssh "$1" "rm -f link_costs_*"
}

reset_configuration () {
  echo "Sending configuration script $2 to $1..."
  scp "$2" "$1:"

  echo "Resetting emulated network delays in $1 using script: $2"
  CONFIGURATION_SCRIPT=$2

  ssh "$1" /bin/bash << EOF
    sudo tc qdisc del dev eth1 root 2> /dev/null
    sudo tc qdisc del dev eth2 root 2> /dev/null
    sudo tc qdisc del dev eth3 root 2> /dev/null
    sudo tc qdisc del dev eth4 root 2> /dev/null
    /bin/bash "${CONFIGURATION_SCRIPT}"
EOF
}

start_time=`date +%s`

# Reset the network emulation delays in hosts if requested.
case "$RESET_DELAYS" in
"1")
  echo "Reconfiguring network emulation delays..."
  reset_configuration network-r1 configureR1.sh
  reset_configuration network-r2 configureR2.sh
  ;;
*)
  echo "Skipping network emulation delay reconfiguration..."
  ;;
esac

# For all hosts, send scripts and remove pre-existing data, unless requested not to.
case "$SYNC" in
"0")
  echo "Skipping file sync..."
  ;;
*)
  echo "Syncing files..."
  for host in "${HOSTS[@]}";
  do
    send_measurement_script $host
    remove_existing_measurements $host
  done
  ;;
esac

case "$EXPERIMENT_NUMBER" in
"1")
  echo "Configuring experiment 1..."
  ;;
"2")
  echo "Configuring experiment 2..."
  ;;
"3")
  echo "Configuring experiment 3..."
  ;;
*)
  echo "Skipping experiment configuration..."
  ;;
esac

end_time=`date +%s`
total_running_time=$((end_time - start_time))
echo "Nodes have been prepared in $total_running_time seconds"
