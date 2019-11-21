#!/bin/bash

s=$(getent ahosts "s" | cut -d " " -f 1 | uniq)
r2=$(getent ahosts "r2" | cut -d " " -f 1 | uniq)
d=$(getent ahosts "d" | cut -d " " -f 1 | uniq)

s_adapter=$(ip route get $s | grep -Po '(?<=(dev )).*(?= src| proto)')
r2_adapter=$(ip route get $r2 | grep -Po '(?<=(dev )).*(?= src| proto)')
d_adapter=$(ip route get $d | grep -Po '(?<=(dev )).*(?= src| proto)')

EXPERIMENT_NUMBER=$1

case "$EXPERIMENT_NUMBER" in
"1")
  echo "Configuring using experiment 1..."
  EXPERIMENT_DELAY=20
  ;;
"2")
  echo "Configuring using experiment 2..."
  EXPERIMENT_DELAY=40
  ;;
"3")
  echo "Configuring using experiment 3..."
  EXPERIMENT_DELAY=50
  ;;
*)
  echo "You must provide an experiment number to this script."
  exit 1
  ;;
esac

sudo tc qdisc add dev $s_adapter root netem delay "${EXPERIMENT_DELAY}ms" 5ms distribution normal
sudo tc qdisc add dev $r2_adapter root netem delay "${EXPERIMENT_DELAY}ms" 5ms distribution normal
sudo tc qdisc add dev $d_adapter root netem delay "${EXPERIMENT_DELAY}ms" 5ms distribution normal

