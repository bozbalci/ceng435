#!/usr/bin/env bash

HOSTS=(
  network-s
  network-r1
  network-r2
  network-r3
  network-d
)

synchronize_time() {
  echo "Synchronizing time in $1..."
  ssh "$1" /bin/bash << EOF
  sudo systemctl stop ntp
  sudo ntpdate 0.tr.pool.ntp.org
EOF
}

send_experiment_script () {
  echo "Sending experiment script to $1..."
  scp experiment.py route.json "$1:"
}

remove_existing_experiments () {
  echo "Removing existing experiment results in $1..."
  ssh "$1" "rm -f end_to_end_costs*"
}

set_experiment_delays () {
  echo "Sending configuration script $2 to $1 with argument: $3"
  scp "$2" "$1:"

  echo "Resetting emulated network delays in $1 using script: $2"
  CONFIGURATION_SCRIPT=$2
  ARGUMENT=$3

  ssh "$1" /bin/bash << EOF
    sudo tc qdisc del dev eth1 root 2> /dev/null
    sudo tc qdisc del dev eth2 root 2> /dev/null
    sudo tc qdisc del dev eth3 root 2> /dev/null
    sudo tc qdisc del dev eth4 root 2> /dev/null
    /bin/bash "${CONFIGURATION_SCRIPT}" "${ARGUMENT}"
EOF
}

start_time=`date +%s`

# For all hosts, send scripts and remove pre-existing data, unless requested not to.
case "$SYNC" in
"0")
  echo "Skipping file sync..."
  ;;
*)
  echo "Syncing files..."
  for host in "${HOSTS[@]}";
  do
    synchronize_time $host
    send_experiment_script $host
    remove_existing_experiments $host
  done
  ;;
esac

case "$EXPERIMENT" in
"1"|"2"|"3")
  echo "Setting experiment delays (exp. ${EXPERIMENT})"
  set_experiment_delays network-s configureSD.sh "$EXPERIMENT"
  set_experiment_delays network-d configureSD.sh "$EXPERIMENT"
  set_experiment_delays network-r3 configureR3.sh "$EXPERIMENT"
  ;;
*)
  echo "No experiment value provided. Not going to alter delays."
  ;;
esac

end_time=`date +%s`
total_running_time=$((end_time - start_time))
echo "Nodes have been prepared in $total_running_time seconds"
