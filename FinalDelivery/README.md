# Implementation of a Real-Time Ethernet with Quality-of-Service mechanisms

## Abstract

This project has been performed as an Integrated Team Project of the Embedded Systems Advanced Master from ISAE-Supaéro & INP-Enseeiht.


## OUR MISSIONS

### AFDX P4 HARDWARE IMPLEMENTATION
Implement AFDX network switching capabilities on real hardware: PC (Linux stations) along with raspberry PI3 and PI4.


### QUALITY OF SERVICE MECHANISMS
Add quality of service mechanisms such as SPQ, WRR and optionally DRR to the P4 based AFDX switches.



## OUR SOLUTION

### AFDX ON PC
Using the library DPDK and the compiler T4P4S, a solution was implemented to give a Linux PC the capability to act as an AFDX switch using the language P4.



### AFDX ON RASPBERRY PI 3 & PI 4
Using the network data plane P4PI, both versions of Raspberry pi3 and pi4 can be turned into functional AFDX switches.



### QOS FOR AFDX
A Static Priority Queue along with pseudo Weighted Round Robin algorithms were implemented on P4 using the software p4 compilation target behavioral model v2 (BMV2).



## GROWTH HIGHLIGHTS
Airbus, the market leader in AFDX deployment as of 2022, does not adopt a quality-of-service mechanism. This study served as a proof of concept for the viability of incorporating such processes into the AFDX airborne network, potentially adding an additional layer of security by prioritizing time-sensitive flows (such as flight control) above less crucial ones (infotainment for example).
