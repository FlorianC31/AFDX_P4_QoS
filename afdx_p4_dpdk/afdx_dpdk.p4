/*
This is an attempt to port AFDX implementation to PSA architecture
it compiles with p4c-dpdk
it is not fully tested yet
*/
#include <core.p4>

/* use psa (portable switch architecture) switch model*/
#include <psa.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<32> DST_CONST = 0x3000000;
const bit<24> SRC_CONST = 0x20000;

//Headers

typedef bit<24>    MacAddr_t;   // Variable part = 24bits
typedef bit<16>    VLid_t;     // 2Bytes

header afdx_t {
    //bit<64>     preamble;   //Preamble+SFD
    bit<32>     dstConst;
    VLid_t      dstVL;
    bit<24>     srcMac_cst;
    MacAddr_t   srcMac_addr;
    bit<16>     etherType;
}

struct metadata {
    bit<32> maxi_length;
}

struct headers {
    afdx_t     afdx;
}

struct empty_metadata_t {
}

//Ingress
/*
(packet_in packet, out headers hdr, inout metadata meta, 
in psa_ingress_parser_input_metadata_t standard_metadata)
*/
//use PSA expected parser function 
parser MyParser(packet_in packet, out headers hdr, inout metadata local_metadata, in psa_ingress_parser_input_metadata_t standard_metadata, in empty_metadata_t resub_meta, in empty_metadata_t recirc_meta){
    state start {
        packet.extract(hdr.afdx);
        transition accept;
    }
}
//PSA expected ingress_deparser function
control MyDeparser(packet_out packet, out empty_metadata_t clone_i2e_meta, out empty_metadata_t resubmit_meta, out empty_metadata_t normal_meta, inout headers hdr, in metadata local_metadata, in psa_ingress_output_metadata_t istd) {
    apply {
        packet.emit(hdr.afdx);
    }
}
control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {}
}

//use PSA exposed metadata
control MyIngress(inout headers hdr,inout metadata meta,in psa_ingress_input_metadata_t standard_metadata, inout psa_ingress_output_metadata_t ostd) {
    action Drop() {
        //mark_to_drop(standard_metadata);
    	ingress_drop(ostd);
    }
    //MulticastGroup_t instead of bit<16>    
    action Check_VL(bit<32> MaxLength, MulticastGroup_t MCastGrp) {
            meta.maxi_length = MaxLength;
            //multicast_group is part of psa_ingress_output_metadata_t struct
            ostd.multicast_group = MCastGrp;
    }
    
    table afdx_table {
        key = {
                standard_metadata.ingress_port : exact;     //The sending node must be authorised to send on the desired VL.
                hdr.afdx.dstVL : exact;
                }
        
        actions = {
                    Check_VL;
                    Drop;
                    NoAction;
                    }
                    
        default_action = Drop();
    }
    
    apply{ 
        if ( (hdr.afdx.dstConst == DST_CONST) && (hdr.afdx.srcMac_cst == SRC_CONST) )//&& (hdr.afdx.etherType == TYPE_IPV4))
            afdx_table.apply();
        else
            //mark_to_drop(standard_metadata);
            ingress_drop(ostd);
    }
} 
    
//
control MyComputeChecksum(inout headers hdr, inout metadata meta) {   
    apply {}
}

//Egress
//use PSA expected egress function
control MyEgress(inout headers hdr,inout metadata meta,in psa_egress_input_metadata_t istd, inout psa_egress_output_metadata_t ostd) {
    apply {
    	//TODO
    	//did not find a way to replicat this behaviour using PSA specific code
        //if (standard_metadata.packet_length > meta.maxi_length)
            //mark_to_drop(standard_metadata);
       //     egress_drop(ostd);
    }
}

//PSA expected egress parser function
parser egress_parser(packet_in buffer, out headers hdr, inout metadata local_metadata, in psa_egress_parser_input_metadata_t istd, in empty_metadata_t normal_meta, in empty_metadata_t clone_i2e_meta, in empty_metadata_t clone_e2e_meta) {
    state start {
        transition accept;
    }
}
//PSA expected egress deparser function
control egress_deparser(packet_out packet, out empty_metadata_t clone_e2e_meta, out empty_metadata_t recirculate_meta, inout headers hdr, in metadata local_metadata, in psa_egress_output_metadata_t istd, in psa_egress_deparser_input_metadata_t edstd) {
    apply {
        packet.emit(hdr.afdx);    
    }
}


//PSA main
IngressPipeline(MyParser(), MyIngress(), MyDeparser()) ip;

EgressPipeline(egress_parser(), MyEgress(), egress_deparser()) ep;

PSA_Switch(ip, PacketReplicationEngine(), ep, BufferingQueueingEngine()) main;
