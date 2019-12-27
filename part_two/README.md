# CENG435 Term Project: Part Two

## Group members

|Full name      |ID number|
|---------------|---------|
|Narmin Aliyeva |  2177269|
|Berk Ozbalci   |  2171791|

## Running the experiments

In order to run the experiments, you must first connect to the GENI slice.

### SSH config

Add the following to your `~/.ssh/config`

```ssh-config
Host network-*
    HostName pc3.instageni.northwestern.edu
    User {REPLACE_WITH_YOUR_USER_NAME}
    IdentityFile {REPLACE_WITH_PATH_TO_GENI_SSH_KEY}

Host network-d
    Port 25410

Host network-r1
    Port 25411

Host network-r2
    Port 25412

Host network-r3
    Port 25413

Host network-s
    Port 25414
```

### Prepare the nodes

In order to prepare nodes, you have two options:

1. Set NetEm values and sync the files

    NETEM=1 bash scripts/prepare.sh

The value of `NETEM` can be 1, 2 or 3. Depending on the number given, it will configure
the emulated loss to 5%, 15% and 38% respectively.

2. Only sync the files

    bash scripts/prepare.sh

### Starting the routers

    bash run_routers.sh

In order to terminate all routers, run:

    STOP=1 bash run_routers.sh


### Run the experiments

Below is the usage of the experiment script:

```
usage: __main__.py [-h] [--router] [--source] [--destination]
                   [-E [EXPERIMENT_ID]] [-c [N]]
                   [file]

CENG435 Term Project - Part II - Experiment Scripts

positional arguments:
  file

optional arguments:
  -h, --help          show this help message and exit
  --router            only forward packets from/to s and d
  --source            send an input file to the destination node
  --destination       receive an input file from the source node
  -E [EXPERIMENT_ID]
  -c [N]              run the experiment N times
```

On the source node (using SSH):

    e2171791@s:~$ python3 -mprotocol --source -E1 input.txt -c100
    
On the destination node (using SSH):

    e2171791@d:~$ python3 -mprotocol --destination -E1 output.txt -c100

This will transfer `input.txt` from the source node to `output.txt` in the destination node,
repeating the experiment 100 times.

If you would like to run the second experiment, pass `-E2` as an argument (instead of `-E1`).

The file will be assembled only if `-c1` is given. In repeated experiments, the file is not
assembled in order to save time.

Note that the middle nodes are just running the same script with `--router` parameter given.
Routers do not accept a `-E` or `file` argument.

### Verification

In order to verify that the file has been transmitted without errors, run the following command:

    e2171791@d:~$ cmp --silent input.txt output.txt && echo OK || echo NOK

This will print OK if the file has been correctly assembled at the destination node.
