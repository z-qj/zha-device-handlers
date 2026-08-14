"""Sonoff ZBMINIR2 and MINI-ZBD - Zigbee Switches."""

from zigpy import types
import zigpy.types as t
from zigpy.zcl.foundation import BaseAttributeDefs, DataTypeId, ZCLAttributeDef

from zhaquirks.builder import QuirkBuilder
from zhaquirks.clusters import CustomCluster
from zhaquirks.const import (
    CLUSTER_ID,
    COMMAND,
    ENDPOINT_ID,
    ZHA_SEND_EVENT,
)

# Attribute Define
RELAY_DETACH_ATTR_ID = 0x0028
RELAY_DETACH_ACTION = "relay_detach_action"

ACTION_SINGLE_CLICK = 0x01
ACTION_DOUBLE_CLICK = 0x02
ACTION_LONG_PRESS = 0x03
ACTION_FOLLOW_ON = 0x04
ACTION_FOLLOW_OFF = 0x05

# Event Name
ACTION_TO_COMMAND = {
    ACTION_SINGLE_CLICK: "single_click",
    ACTION_DOUBLE_CLICK: "double_click",
    ACTION_LONG_PRESS: "long_press",
    ACTION_FOLLOW_ON: "follow_on",
    ACTION_FOLLOW_OFF: "follow_off",
}


class SonoffExternalSwitchTriggerType(types.enum8):
    """External switch trigger type."""

    Edge_trigger = 0x00
    Pulse_trigger = 0x01
    Normally_off_follow_trigger = 0x02
    Normally_on_follow_trigger = 0x82


class SonoffCluster(CustomCluster):
    """Custom Sonoff cluster."""

    cluster_id = 0xFC11

    class AttributeDefs(BaseAttributeDefs):
        """Attribute definitions."""

        external_trigger_mode = ZCLAttributeDef(
            id=0x0016,
            type=SonoffExternalSwitchTriggerType,
            zcl_type=DataTypeId.uint8,
            manufacturer_code=None,
        )
        detach_relay = ZCLAttributeDef(
            id=0x0017,
            type=t.Bool,
            manufacturer_code=None,
        )
        turbo_mode = ZCLAttributeDef(
            id=0x0012,
            type=t.int16s,
            manufacturer_code=None,
        )
        network_led = ZCLAttributeDef(
            id=0x0001,
            type=t.Bool,
            manufacturer_code=None,
        )
        relay_spera_key_action_event = ZCLAttributeDef(
            id=RELAY_DETACH_ATTR_ID,
            type=t.uint8_t,
            manufacturer_code=None,
        )

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)

        if attrid == RELAY_DETACH_ATTR_ID:
            # 根据值获取对应的命令字符串，若未定义则使用 "unknown"
            command = ACTION_TO_COMMAND.get(value, "unknown_action")
            self.listener_event(ZHA_SEND_EVENT, command, {})


(
    QuirkBuilder("SONOFF", "ZBMINIR2")
    .applies_to("SONOFF", "MINI-ZBD")
    .replaces(SonoffCluster)
    .enum(
        SonoffCluster.AttributeDefs.external_trigger_mode.name,
        SonoffExternalSwitchTriggerType,
        SonoffCluster.cluster_id,
        translation_key="external_trigger_mode",
        fallback_name="External trigger mode",
    )
    .switch(
        SonoffCluster.AttributeDefs.turbo_mode.name,
        SonoffCluster.cluster_id,
        off_value=9,
        on_value=20,
        translation_key="turbo_mode",
        fallback_name="Turbo mode",
    )
    .switch(
        SonoffCluster.AttributeDefs.detach_relay.name,
        SonoffCluster.cluster_id,
        translation_key="detach_relay",
        fallback_name="Detach relay",
    )
    .switch(
        SonoffCluster.AttributeDefs.network_led.name,
        SonoffCluster.cluster_id,
        translation_key="network_led",
        fallback_name="Network LED",
    )
    .device_automation_triggers(
        {
            ("single_click", RELAY_DETACH_ACTION): {
                CLUSTER_ID: SonoffCluster.cluster_id,
                ENDPOINT_ID: 1,
                COMMAND: "single_click",
            },
            ("double_click", RELAY_DETACH_ACTION): {
                CLUSTER_ID: SonoffCluster.cluster_id,
                ENDPOINT_ID: 1,
                COMMAND: "double_click",
            },
            ("long_press", RELAY_DETACH_ACTION): {
                CLUSTER_ID: SonoffCluster.cluster_id,
                ENDPOINT_ID: 1,
                COMMAND: "long_press",
            },
            ("follow_on", RELAY_DETACH_ACTION): {
                CLUSTER_ID: SonoffCluster.cluster_id,
                ENDPOINT_ID: 1,
                COMMAND: "follow_on",
            },
            ("follow_off", RELAY_DETACH_ACTION): {
                CLUSTER_ID: SonoffCluster.cluster_id,
                ENDPOINT_ID: 1,
                COMMAND: "follow_off",
            },
        }
    )
    .add_to_registry()
)
