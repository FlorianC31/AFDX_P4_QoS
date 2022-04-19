/// based on `afdx_spw.p4app/afdx.p4`
/// XXX: untested
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<32> DST_CONST = 0x3000000;
const bit<24> SRC_CONST = 0x20000;

// with this version, NB_VL needs to be known at compile time :/
#define NB_VL 8
#define NB_Q 8

// Headers
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
    bit<16> curr_usage;
    bit<16> below_usage;
}

struct headers {
    afdx_t     afdx;
}

register<bit<32>>(NB_Q * NB_VL) usage;

// Parser
parser MyParser(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    state start {
        packet.extract(hdr.afdx);
        transition accept;
    }
}

// XXX
control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

// Controls
control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    action Drop() {
        mark_to_drop(standard_metadata);
    }

    /// @note: `VLWeight`; not sure should be there, maybe in some other
    /// table's action for consistency (with `key = { dstVL : exact; }`)
    action Check_VL(bit<32> MaxLength, bit<16> MCastGrp, bit<8> VLWeight) {
        meta.maxi_length = MaxLength;
        standard_metadata.mcast_grp = MCastGrp;

        // test each queue for its `usage`, use the first one with free space
        #define CASCADE_IF_DO                                             \
            usage.read(meta.curr_usage, q + NB_Q*hdr.afdx.dstVL);         \
            if (meta.curr_usage < VLWeight) {                             \
                usage.write(q + NB_Q*hdr.afdx.dstVL, meta.curr_usage+1);  \
                standard_metadata.priority = q;                           \
            } else /* next iteration */

        // if none found, default to the last one (preserves message order)
        #define CASCADE_ELSE_DO                                       \
            usage.write(q + NB_Q*hdr.afdx.dstVL, meta.curr_usage+1);  \
            standard_metadata.priority = q;

        // (insert the cascading 'if-else's)
        #include "CASCADE_IF_ELSE.p4"
    }

    table afdx_table {
        key = {
            standard_metadata.ingress_port : exact; // The sending node must be authorised to send on the desired VL.
            hdr.afdx.dstVL : exact;
        }

        actions = {
            Check_VL;
            Drop;
            NoAction;
        }

        default_action = Drop();
    }

    apply {
        if ( (hdr.afdx.dstConst == DST_CONST) && (hdr.afdx.srcMac_cst == SRC_CONST) )//&& (hdr.afdx.etherType == TYPE_IPV4))
        {
            afdx_table.apply();
        }
        else mark_to_drop(standard_metadata);
    }
}

// XXX
control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

// Egress
control MyEgress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    apply {
        if (standard_metadata.packet_length <= meta.maxi_length)
        {
            // entering here,
            // meta.curr_usage: usage of the queue when it was enqueued
            // standard_metadata.priority: queue it is enqueued in

            // update curr_usage
            usage.read(meta.curr_usage, standard_metadata.priority + NB_Q*hdr.afdx.dstVL);

            // if this is already the least prio queue (nothing "below")
            if (8 == standard_metadata.priority+1)
            {
                // make it 0 so it is considered as "tail" in the next `if`
                meta.below_usage = 0;
            }
            else
            {
                // if this is any other queue but the last one, it has one "below"
                usage.read(meta.below_usage, standard_metadata.priority+1 + NB_Q*hdr.afdx.dstVL);
            }

            // if is tail, free 1 on this queue
            if (0 == meta.below_usage)
            {
                // was the last pending message, reset
                if (0 == meta.curr_usage-1)
                {
                    // foreach q up to standard_metadata.priority do usage[vl][q] = 0 end
                    usage.write(0 + NB_Q*hdr.afdx.dstVL, 0);
                    usage.write(1 + NB_Q*hdr.afdx.dstVL, 0);
                    usage.write(2 + NB_Q*hdr.afdx.dstVL, 0);
                    usage.write(3 + NB_Q*hdr.afdx.dstVL, 0);
                    usage.write(4 + NB_Q*hdr.afdx.dstVL, 0);
                    usage.write(5 + NB_Q*hdr.afdx.dstVL, 0);
                    usage.write(6 + NB_Q*hdr.afdx.dstVL, 0);
                    usage.write(7 + NB_Q*hdr.afdx.dstVL, 0);
                }
                else
                {
                    usage.write(standard_metadata.priority + NB_Q*hdr.afdx.dstVL, meta.curr_usage-1);
                }
            } // (endif 0 below)
        }
        else mark_to_drop(standard_metadata);
    }
}

// Deparser
control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.afdx);
    }
}

// Execution
V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
