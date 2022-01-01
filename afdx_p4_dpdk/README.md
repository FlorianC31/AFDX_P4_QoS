p4c for DPDK is not compatible with v1model.
Use following command to check the list of accepted target for dpdk:

```shell
$ p4c --target-help

Supported targets in "target, arch" tuple:
dpdk-psa
bmv2-v1model
bmv2-psa
ebpf-v1model
```


The first version of afdx.p4 (original_afdx.p4) using v1model.p4, it needed to be recoded with psa.p4 (afdx_dpdk.p4) to be used with p4c and dpdk.

However, p4app seems to run only with v1model:

```shell
$ p4app run afdx.p4app/
Entering build directory.
Extracting package.
> touch /tmp/p4app_logs/p4s.s1.log
> ln -s /tmp/p4app_logs/p4s.s1.log /tmp/p4s.s1.log
Reading package manifest.
> p4c-bm2-ss --p4v 16 "afdx_dpdk.p4" -o "afdx_dpdk.json"
/usr/local/share/p4c/p4include/psa.p4(852): [--Wwarn=invalid] warning: PSA_Switch: the main package should be called V1Switch; are you using the wrong architecture?
package PSA_Switch<IH, IM, EH, EM, NM, CI2EM, CE2EM, RESUBM, RECIRCM> (
        ^^^^^^^^^^
afdx_dpdk.p4(135): [--Werror=unsupported] error: package PSA_Switchpackage PSA_Switch: main package  match the expected model
Are you using an up-to-date v1model.p4?
PSA_Switch(ip, PacketReplicationEngine(), ep, BufferingQueueingEngine()) main;
                                                                         ^^^^
Compile failed.
```

Therefore, two versions of each p4 files will need to coexist...
