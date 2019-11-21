# CENG435 Term Project: Part One

## Group members

|Full name      |ID number|
|---------------|---------|
|Narmin Aliyeva |  2177269|
|Berk Ozbalci   |  2171791|

## How to run the measurements (discovery part)

In order to run the measurements, cd into `discovery_scripts` and then follow these steps:

### SSH config

Add the following to your `~/.ssh/config`

```ssh-config
Host network-*
    HostName pc5.instageni.stanford.edu
    User {REPLACE_WITH_YOUR_USER_NAME}
    IdentityFile {REPLACE_WITH_PATH_TO_GENI_SSH_KEY}

Host network-d
    Port 29610

Host network-r1
    Port 29611

Host network-r2
    Port 29612

Host network-r3
    Port 29613

Host network-s
    Port 29614
```

### Prepare nodes

We bundled a script, `prepare_nodes.sh` that does a multitude of things:

- It sends the measurement script to all nodes,
- It removes any pre-existing link cost measurements,
- (Optional) It removes network emulation delays and sets new ones,

#### Usage:

    # Just sync the files and exit.
    $ ./prepare_nodes.sh
    
    # Disable file sync.
    $ SYNC=0 ./prepare_nodes.sh
    
    # Reset network emulation delays on r1 and r2.
    $ RESET_DELAYS=1 ./prepare_nodes.sh


### Run measurements

In order to run the measurements, run:

    $ ./run_measurements.sh

Unfortunately there is no way to verify that all nodes have finished processing. The
safest would be to ssh into r2 (the node with highest number of links) and attach
into the tmux session started by the above script and look at the output.

When all measurements are done, run:

    $ KILL=1 ./run_measurements.sh

in order to kill all tmux sessions across all nodes. This will terminate the server
processes properly.

### Fetch results

After the above steps are completed, run

    $ ./fetch_results.sh

in order to retrieve the link costs computed at each node. This will save the measurement
results to a file named `results_summary`. It will look like this:

```
==> measurements/network-d/link_costs_r1.txt <==
0.0628435492515564

==> measurements/network-d/link_costs_r2.txt <==
0.10868188142776489

==> measurements/network-d/link_costs_r3.txt <==
0.001066446304321289

==> measurements/network-r1/link_costs_d.txt <==
0.06269283294677734
```

The first line indicates that the RTT from `d` to `r1` is approx. 0.06 seconds.

Using the numbers from this file, one can apply the Dijkstra algorithm to find the
shortest path from `s` to `d`.
