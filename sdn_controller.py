from os_ken.base import app_manager
from os_ken.controller import ofp_event, event
from os_ken.controller.handler import (
    CONFIG_DISPATCHER,
    MAIN_DISPATCHER,
    set_ev_cls
)
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet, ethernet, ether_types
from os_ken.lib import hub

import csv
import os
import ipaddress


LOG_FILE = "/home/sathvik/Desktop/Proxy_Content_Filtering/logs/access_logs.csv"


class EventBlockClient(event.EventBase):

    def __init__(self, client_ip):
        super(EventBlockClient, self).__init__()
        self.client_ip = client_ip


class ProxySDNController(app_manager.OSKenApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ProxySDNController, self).__init__(*args, **kwargs)

        self.mac_to_port = {}
        self.datapaths = {}

        self.log_position = (
            os.path.getsize(LOG_FILE)
            if os.path.exists(LOG_FILE)
            else 0
        )

        print("[SDN] Proxy Content Filtering Controller Started")

        hub.spawn(self.monitor_access_log)

    def monitor_access_log(self):

        print("[SDN] Monitoring proxy access logs...")

        while True:

            try:
                if os.path.exists(LOG_FILE):

                    current_size = os.path.getsize(LOG_FILE)

                    if current_size < self.log_position:
                        self.log_position = 0

                    with open(LOG_FILE, "r", newline="") as file:

                        file.seek(self.log_position)

                        reader = csv.reader(file)

                        for row in reader:

                            if len(row) < 3:
                                continue

                            client_ip = row[0].strip()
                            decision = row[2].strip().upper()

                            if decision == "BLOCKED":

                                try:
                                    ipaddress.IPv4Address(client_ip)

                                    print(
                                        "[SDN] Block event detected:",
                                        client_ip
                                    )

                                    self.send_event(
                                        self.name,
                                        EventBlockClient(client_ip)
                                    )

                                except ValueError:
                                    continue

                        self.log_position = file.tell()

            except Exception as error:
                print("[SDN] Log monitoring error:", error)

            hub.sleep(1)

    def add_flow(
        self,
        datapath,
        priority,
        match,
        actions,
        idle_timeout=0
    ):

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        instructions = [
            parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS,
                actions
            )
        ]

        flow = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=instructions,
            idle_timeout=idle_timeout
        )

        datapath.send_msg(flow)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):

        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        self.datapaths[datapath.id] = datapath

        match = parser.OFPMatch()

        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]

        self.add_flow(datapath, 0, match, actions)

        print("[SDN] Switch connected:", datapath.id)

    @set_ev_cls(EventBlockClient)
    def block_client_handler(self, ev):

        client_ip = ev.client_ip

        for datapath in self.datapaths.values():

            parser = datapath.ofproto_parser

            match = parser.OFPMatch(
                eth_type=0x0800,
                ipv4_src=client_ip
            )

            flow = parser.OFPFlowMod(
                datapath=datapath,
                priority=100,
                match=match,
                instructions=[],
                hard_timeout=60
            )

            datapath.send_msg(flow)

            print(
                "[SDN] Temporary block installed for",
                client_ip,
                "for 60 seconds"
            )

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):

        msg = ev.msg
        datapath = msg.datapath

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth is None:
            return

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [
            parser.OFPActionOutput(out_port)
        ]

        if out_port != ofproto.OFPP_FLOOD:

            match = parser.OFPMatch(
                in_port=in_port,
                eth_dst=dst,
                eth_src=src
            )

            self.add_flow(
                datapath,
                1,
                match,
                actions
            )

        data = None

        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data
        )

        datapath.send_msg(out)
