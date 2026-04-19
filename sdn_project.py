from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet, ethernet


class SDNProject(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SDNProject, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    # TABLE MISS FLOW (IMPORTANT)
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
    	datapath = ev.msg.datapath
    	ofproto = datapath.ofproto
    	parser = datapath.ofproto_parser

    	# 🔴 BLOCK h1 AT SWITCH LEVEL
    	match = parser.OFPMatch(eth_src="00:00:00:00:00:01")
    	self.add_flow(datapath, 100, match, [])  # DROP

    	# DEFAULT rule (send to controller)
    	match = parser.OFPMatch()
    	actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                      ofproto.OFPCML_NO_BUFFER)]
    	self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                               match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
    	msg = ev.msg
    	datapath = msg.datapath
    	ofproto = datapath.ofproto
    	parser = datapath.ofproto_parser
    	dpid = datapath.id
    	in_port = msg.match['in_port']

    	pkt = packet.Packet(msg.data)
    	eth = pkt.get_protocol(ethernet.ethernet)

    	src = eth.src
    	dst = eth.dst

    	# 🔴 BLOCK h1 FIRST (HIGH PRIORITY)
    	if src == "00:00:00:00:00:01":
        	print("Blocked traffic from h1")

        	match = parser.OFPMatch(eth_src=src)
        	self.add_flow(datapath, 100, match, [])  # DROP rule

        	return

    	self.mac_to_port.setdefault(dpid, {})

    	# Learn MAC
    	self.mac_to_port[dpid][src] = in_port

    	# Forwarding logic
    	if dst in self.mac_to_port[dpid]:
        	out_port = self.mac_to_port[dpid][dst]
    	else:
        	out_port = ofproto.OFPP_FLOOD

    	actions = [parser.OFPActionOutput(out_port)]

    	match = parser.OFPMatch(in_port=in_port, eth_src=src, eth_dst=dst)
    	self.add_flow(datapath, 1, match, actions)

    	out = parser.OFPPacketOut(
        	datapath=datapath,
        	buffer_id=msg.buffer_id,
        	in_port=in_port,
        	actions=actions,
        	data=msg.data
    	)
    	datapath.send_msg(out)

