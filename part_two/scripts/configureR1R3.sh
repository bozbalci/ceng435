#!/bin/bash

s=$(getent ahosts "s" | cut -d " " -f 1 | uniq)
r2=$(getent ahosts "r2" | cut -d " " -f 1 | uniq)
d=$(getent ahosts "d" | cut -d " " -f 1 | uniq)

s_adapter=$(ip route get $s | grep -Po '(?<=(dev )).*(?= src| proto)')
r2_adapter=$(ip route get $r2 | grep -Po '(?<=(dev )).*(?= src| proto)')
d_adapter=$(ip route get $d | grep -Po '(?<=(dev )).*(?= src| proto)')

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

sudo tc qdisc add dev $s_adapter root netem loss "$LOSS"% delay 3ms
sudo tc qdisc add dev $r2_adapter root netem loss "$LOSS"% delay 3ms
sudo tc qdisc add dev $d_adapter root netem loss "$LOSS"% delay 3ms
