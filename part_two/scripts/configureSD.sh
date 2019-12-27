#!/bin/bash

r1=$(getent ahosts "r1" | cut -d " " -f 1 | uniq)
r2=$(getent ahosts "r2" | cut -d " " -f 1 | uniq)
r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)

r1_adapter=$(ip route get $r1 | grep -Po '(?<=(dev )).*(?= src| proto)')
r2_adapter=$(ip route get $r2 | grep -Po '(?<=(dev )).*(?= src| proto)')
r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')

case "$NETEM" in
"1")
  LOSS=5
  ;;
"2")
  LOSS=15
  ;;
"3")
  LOSS=38
  ;;
*)
  ;;
esac

sudo tc qdisc add dev $r1_adapter root netem loss "$LOSS"% delay 3ms
sudo tc qdisc add dev $r2_adapter root netem loss "$LOSS"% delay 3ms
sudo tc qdisc add dev $r3_adapter root netem loss "$LOSS"% delay 3ms