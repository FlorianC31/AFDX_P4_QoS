# Enable vfio driver (alternative method, see §5.2.1 of DPDK documentation: https://doc.dpdk.org/guides/linux_gsg/linux_drivers.html#vfio-no-iommu-mode)
echo 1 > /sys/module/vfio/parameters/enable_unsafe_noiommu_mode

# Show the status of each ethernet card driver before binding
python3 dpdk-21.11/usertools/dpdk-devbind.py --status

# Unbind default driver
python3 dpdk-21.11/usertools/dpdk-devbind.py -u 0000:05:00.0
python3 dpdk-21.11/usertools/dpdk-devbind.py -u 0000:08:00.0

# Bind default driver
python3 dpdk-21.11/usertools/dpdk-devbind.py -b vfio-pci 0000:05:00.0
python3 dpdk-21.11/usertools/dpdk-devbind.py -b vfio-pci 0000:08:00.0

# Show the status of each ethernet card driver after binding
python3 dpdk-21.11/usertools/dpdk-devbind.py --status
