# Strict Priority Queueing

```
            ____
h1-------->|    |
h2-------->|    |
h3-------->| s1 |----->h7
h4-------->|    |
h5-------->|    |
h6-------->|___ |


```


### Introduction

To make this example work you will first need to make a small change to the `bmv2` code,
then recompile it again. At the time  of writing this, the `v1model.p4` architecture
file does not include the needed metadata to set and read the priority queues,
thus you will also have to add that in the `v1model.p4` file.

1. Go to the directory where you have downloaded `bmv2`.
2. Go to `PATH_TO_BMV2/targets/simple_switch/simple_switch.h`.
3. Look for the line `// #define SSWITCH_PRIORITY_QUEUEING_ON` and uncomment it.
4. Compile and install `bmv2` again.
5. Go to the directory where you have downloaded `p4c`.
6. Copy and edit `PATH_TO_P4C/p4include/v1model.p4` in another location. You will have to add the following metadata fields inside the `standard_metadata` struct (if not already present). You can find an already configured `v1model.p4` in this directory.
    ```
    /// set packet priority
    @alias("intrinsic_metadata.priority")
    bit<3> priority;
    @alias("queueing_metadata.qid")
    bit<5> qid;
    ```
7. Copy the updated `v1model.p4` to the global path `/usr/local/share/p4c/p4include/`. Remember that every time you update `p4c` this file will be overwritten and the metadata fields might be removed. As an alternative, you can copy the preconfigured `v1model.p4` in the global path.
    ```
    sudo wget https://raw.githubusercontent.com/nsg-ethz/p4-learning/master/examples/multiqueueing/v1model.p4 -O /usr/local/share/p4c/p4include/v1model.p4
    ```
8. Now you are ready to go and test the `simple_switch` strict priority queues!


## How to run

AFDX Packets from `h1`, `h2`, `h3`, `h4`,`h5` and `h6`  towards `h7` will be sent to two different priority queues 0 and 7, respectively.
(if the following commads fail please install the dependencies found at https://github.com/nsg-ethz/p4-learning#install-the-required-software )
```
bash
sudo p4run
```

or
```
bash
sudo python network.py
```

Do a tcpdump on the various hosts to be able to analyze the traffic:
examples:
```
h1 exec tcpdump -i h1-eth0 ether host 03:00:00:00:00:01 &
h7 exec tcpdump -i h7-eth0 ether host 03:00:00:00:00:01 or ether host 03:00:00:00:00:02 or ether host 03:00:00:00:00:03 or ether host 03:00:00:00:00:04 or ether host 03:00:00:00:00:05 or ether host 03:00:00:00:00:06 &
```
Send AFDX flow from a host:
example:
```
bash
h1 exec xterm
                                            #VL host-name bag
(in the h1 xterm) python3 send_afdx_packet.py 1 h1        64
```
