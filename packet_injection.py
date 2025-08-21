#!/usr/bin/env python3
"""
RAMSES RF - Direct Packet Injection Example

This demonstrates how to inject a raw packet string directly into the RAMSES RF system
to trigger the same command processing flow that occurs when packets are received
from the transport layer.

Example packet: " I --- 29:162275 32:134446 --:------ 22F1 003 000407"
"""

from datetime import datetime as dt

from ramses_rf.gateway import Gateway
from ramses_tx import Packet


def inject_packet_string(gateway: Gateway, packet_string: str) -> None:
    """
    Inject a raw packet string directly into the RAMSES RF gateway.

    This bypasses the transport layer and feeds the packet directly to the
    protocol's packet processing pipeline, triggering the same flow as if
    the packet was received via RF.

    Args:
        gateway: Active RAMSES RF Gateway instance
        packet_string: Raw packet string (e.g., " I --- 29:162275 32:134446 --:------ 22F1 003 000407")
    """

    # Method 1: Direct protocol injection (preferred for simulation)
    if hasattr(gateway, "_protocol") and gateway._protocol:
        try:
            # Create a Packet from the string with current timestamp
            # The from_file method expects format: "timestamp pkt_line"
            timestamp = dt.now().isoformat()
            packet = Packet.from_file(timestamp, packet_string)

            # Inject directly into protocol's packet receiver
            gateway._protocol.pkt_received(packet)
            print(f"✓ Packet injected successfully: {packet}")

        except Exception as e:
            print(f"✗ Failed to inject packet: {e}")
    else:
        print("✗ Gateway protocol not available")


def inject_via_transport(gateway: Gateway, packet_string: str) -> None:
    """
    Alternative method: Inject via transport layer (if available).

    This method uses the transport's internal packet processing, which is
    closer to how packets would arrive from actual RF communication.
    """

    if hasattr(gateway, "_transport") and gateway._transport:
        try:
            timestamp = dt.now().isoformat()
            # Use transport's frame reading method
            gateway._transport._frame_read(timestamp, packet_string)
            print(f"✓ Packet injected via transport: {packet_string}")

        except Exception as e:
            print(f"✗ Failed to inject via transport: {e}")
    else:
        print("✗ Gateway transport not available")


# Example usage function
def example_injection(gateway: Gateway):
    """
    Example of how to inject your specific 22F1 command packet.

    The packet " I --- 29:162275 32:134446 --:------ 22F1 003 000407" represents:
    - Verb: I (Information)
    - Source: 29:162275 (HVAC remote controller)
    - Destination: 32:134446 (HVAC device)
    - Command: 22F1 (Fan mode command)
    - Payload: 000407 (Fan mode data)
    """

    # Your specific packet string
    packet_string = " I --- 29:162275 32:134446 --:------ 22F1 003 000407"

    print("Injecting HVAC fan mode command...")
    print(f"Packet: {packet_string}")

    # Try primary injection method
    inject_packet_string(gateway, packet_string)

    # Alternative: try transport method
    # inject_via_transport(gateway, packet_string)


def inject_multiple_packets(gateway: Gateway, packet_list: list[str]):
    """
    Inject multiple packets in sequence.

    Useful for simulating command sequences or device interactions.
    """

    for i, packet_string in enumerate(packet_list):
        print(f"Injecting packet {i+1}/{len(packet_list)}: {packet_string}")
        inject_packet_string(gateway, packet_string)


# Integration points for different use cases:


def integrate_with_home_assistant(gateway: Gateway, command_data: dict):
    """
    Example integration point for Home Assistant custom components.

    This shows how you could create packets programmatically based on
    Home Assistant service calls or state changes.
    """

    # Example: Convert HA fan command to RAMSES packet
    if command_data.get("command") == "set_fan_mode":
        fan_mode = command_data.get("fan_mode", 0)
        source_id = command_data.get("source_id", "29:162275")
        target_id = command_data.get("target_id", "32:134446")

        # Construct 22F1 fan command packet
        payload = f"0004{fan_mode:02d}"  # Example payload format
        packet_string = f" I --- {source_id} {target_id} --:------ 22F1 003 {payload}"

        print(f"HA Command: {command_data}")
        inject_packet_string(gateway, packet_string)


def integrate_with_mqtt(gateway: Gateway, mqtt_topic: str, mqtt_payload: str):
    """
    Example integration point for MQTT-based command injection.

    This could be used to inject packets based on MQTT messages.
    """

    # Example: Parse MQTT payload and create packet
    if mqtt_topic == "ramses_rf/inject_packet":
        try:
            packet_string = mqtt_payload.strip()
            print(f"MQTT Injection - Topic: {mqtt_topic}")
            inject_packet_string(gateway, packet_string)
        except Exception as e:
            print(f"✗ MQTT injection failed: {e}")


if __name__ == "__main__":
    print("""
RAMSES RF Direct Packet Injection Guide:

1. Basic injection:
   inject_packet_string(gateway, " I --- 29:162275 32:134446 --:------ 22F1 003 000407")

2. The packet will flow through:
   Protocol.pkt_received() → Message() → process_msg() → Device handling

3. Key functions to call:
   - inject_packet_string(): Main injection function
   - inject_via_transport(): Alternative transport-level injection
   - example_injection(): Ready-to-use example with your packet

4. Integration examples:
   - integrate_with_home_assistant(): HA service integration
   - integrate_with_mqtt(): MQTT-based injection
   - inject_multiple_packets(): Sequence injection

Your packet " I --- 29:162275 32:134446 --:------ 22F1 003 000407" will trigger:
- Device creation (if devices don't exist)
- 22F1 command parsing (HVAC fan mode)
- Device state updates
- Any registered callbacks/handlers
""")
