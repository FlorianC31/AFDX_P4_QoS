# T4P4s installation

To avoid compatibility issues with DPDK, P4C and T4P4S, each PC potentially used as a P4
switch has been formatted with the latest LTS Ubuntu version (20.04 LTS).

The T4P4S script directly provided on GitHub compiles and installs all the tools needed for P4.
https://github.com/P4ELTE/t4p4s#preparation


# Ethernet Cards binding

Once T4P4S is installed on the PC, the next major step is to bind the Ethernet Cards with the vfio-pci driver which is used by DPDK.
The vfio driver must be priorly loaded. Since no IOMMU was available on our configuration, we needed to refer to DPDK documentation (https://doc.dpdk.org/guides/linux_gsg/linux_drivers.html#vfio).

Moreover, since the first method presented in the documentation, we had to use the alternative method.
Once the vfio driver enabled, the default driver can be unbonded from the Ethernet Card and the vfio driver bind.

The script config.sh can edited be used direclty to automatically bind Ethernet cards.


# T4P4S configuration

The afdx.p4 file must be in the example
directory and the configuration line add to be added in the examples.cfg file:
```shell
afdx arch=dpdk hugepages=1024 model=v1model smem cores=1 ports=1x2
```

Finally, the t4p4s script can be launched with debug and verbose parameters to get the full log in the terminal:
```shell
./t4p4s.sh :afdx.p4 dbg verbose
```

The switch is now operational and the tests have shown that the AFDX packets are correctly
forwarded along VL, but all the other packets are dropped as expected.


# Limitations

Some hardware issues have been encountered during the study:
- The PC first used was equipped with Core 2 Duo processors with only 1 GB ram memory with Lubuntu (Light Version of Ubuntu). Unfortunately, 1 GB memory was insufficient to compile DPDK.
- On second try, DPDK and T4P4S ware successfully installed on a Core 2 Duo processors with only 4 Go ram memory with classic Ubuntu 20.04 LTS. However, it turned out that DPDK is only compatible with recent processors because of the SSE4.2 instruction (Intel Core i7 (“Nehalem”), Intel Atom (Silvermont core), AMD Bulldozer, AMD Jaguar, and later processors.)
- On the third and last try, T4P4S were successfully installed on an Intel I7 processor with 8 GB Ram. The PC was equipped with the motherboard Ethernet port, and 2 double port Ethernet PCI cards, totaling 5 Ethernet ports. Nevertheless, only one double port Ethernet card was recent enough to have a driver supported by DPDK ( Intel egb driver). The other Ethernet card ( Intel e1000 driver) and the motherboard Ethernet port ( Intel e1000e driver) are too ancient and are not supported by DPDK.

Unfortunately, obtaining a new compatible Ethernet card before the project's finish was not possible. As a result, with the available hardware, only a two-port switch could be implemented on a PC.
