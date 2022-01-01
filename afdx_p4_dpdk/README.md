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


The first version of afdx.p4 (original_afdx.p4) using v1model.p4, it needed to be recoded with psa.p4 (afdx_dpdk.p4)
