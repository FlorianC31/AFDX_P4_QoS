#include <core.p4>
#include <v1model.p4>

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

//Parser
parser MyParser(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    state start {
        packet.extract(hdr.afdx);
        transition accept;
    }
}

//
control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {}
}

//Controls
control MyIngress(inout headers hdr,inout metadata meta,inout standard_metadata_t standard_metadata) {
    action Drop() {
        mark_to_drop(standard_metadata);
    }
    
    action Check_VL(bit<32> MaxLength, bit<9> port) {
            meta.maxi_length = MaxLength;
            standard_metadata.egress_port = port;
    }
    
    table afdx_table_port {
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

	    const entries = {
            (0x0100, 0x01) : Check_VL(64, 2);
            (0x0100, 0x02) : Check_VL(64, 2);
            (0x0100, 0x03) : Check_VL(64, 2);
            (0x0000, 0x04) : Check_VL(64, 2);
		}
    }

    apply{ 
        if ( (hdr.afdx.dstConst == DST_CONST) && (hdr.afdx.srcMac_cst == SRC_CONST) )//&& (hdr.afdx.etherType == TYPE_IPV4))
          {  afdx_table_port.apply();
	    //afdx_table_dstVL.apply();
	  }
        else
            mark_to_drop(standard_metadata);
    }
} 
    
//
control MyComputeChecksum(inout headers hdr, inout metadata meta) {   
    apply {}
}

//Egress
control MyEgress(inout headers hdr,inout metadata meta,inout standard_metadata_t standard_metadata) {
    apply {
        if (standard_metadata.packet_length > meta.maxi_length)
            mark_to_drop(standard_metadata);
    }
}


//Deparser
control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.afdx);
    }
}


//Execution
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
