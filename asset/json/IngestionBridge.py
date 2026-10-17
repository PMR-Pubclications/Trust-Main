import zstd
import trust_packet_pb2 as pb

def ingest_trust_packet(binary_data: bytes):
    """
    Unpacks incoming protobuf packet and routes the inner JSON to existing handlers.
    """
    # 1. Parse the incoming binary Protobuf packet
    packet = pb.TrustPacket.FromString(binary_data)
    
    # 2. Decompress the inner payload
    raw_json_bytes = zstd.decompress(packet.payload_json)
    
    # 3. Reconstruct your standard Python dict
    payload_dict = json.loads(raw_json_bytes.decode('utf-8'))
    
    # 4. Route to your existing JSON processing pipelines without changes!
    print(f"Received packet from {packet.device_id} [Schema: {packet.schema_type}]")
    process_legacy_json_schema(packet.schema_type, payload_dict)

def process_legacy_json_schema(schema_type, data):
    # Your existing code that expects normal JSON dicts stays 100% untouched
    pass
