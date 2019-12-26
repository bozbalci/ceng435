#!/usr/bin/env bash

HOSTS=(
  network-s
  network-r1
  network-r2
  network-r3
  network-d
)

sync () {
  echo "Syncing host $1..."
  rsync -avzh --exclude="*.pyc" --exclude="__pycache__" ./ "$1":
}

reset_configuration () {
  echo "Resetting NetEm on host $1 using experiment $3..."
  ssh "$1" /bin/bash << EOF
    sudo tc qdisc del dev eth1 root 2> /dev/null
    sudo tc qdisc del dev eth2 root 2> /dev/null
    sudo tc qdisc del dev eth3 root 2> /dev/null
    sudo tc qdisc del dev eth4 root 2> /dev/null
EOF
}

configure_host () {
  echo "Configuring NetEm on host $1 using $2..."
  ssh "$1" "NETEM=$NETEM bash scripts/$2"
}

start_time=`date +%s`

for host in "${HOSTS[@]}";
do
  case "$NETEM" in
  "1"|"2"|"3")
    reset_configuration $host
    ;;
  *)
    ;;
  esac
  sync $host
done

case "$NETEM" in
"1"|"2"|"3")
  configure_host network-s configureSD.sh "$NETEM"
  configure_host network-r1 configureR1R3.sh "$NETEM"
  configure_host network-r2 configureR2.sh "$NETEM"
  configure_host network-r3 configureR1R3.sh "$NETEM"
  configure_host network-d configureSD.sh "$NETEM"
  ;;
*)
  ;;
esac

end_time=`date +%s`
total_running_time=$((end_time - start_time))
echo "Nodes have been prepared in $total_running_time seconds"
