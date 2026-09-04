//! Data-codec entry points (R-CANON-12).
//!
//! The data decoder is the path used for messages, receipt results, plan
//! literals, and mailbox/snapshot *value* payloads. It:
//! - decodes `Value` envelopes via [`Value::decode_canonical`] (capability
//!   discriminant `0x05` → `CapabilityInData`);
//! - rejects a top-level standalone `CapRef` envelope (`0x30`) with
//!   `CapabilityInData` rather than producing a capability value.

use super::codec::{CanonicalDecode, CanonicalEncode, ReadCursor, CANONICAL_VERSION};
use super::error::CanonicalError;
use super::primitives::{TAG_CAP_REF, TAG_VALUE};
use super::value::{contains_capability, encode_data_value};
use crate::types::{CapRef, Value};

/// Decode a data-domain value envelope. Rejects capability payloads.
pub fn decode_data_value(bytes: &[u8]) -> Result<Value, CanonicalError> {
    // Standalone CapRef envelope at the top level (R-CANON-12).
    if let Some(tag) = peek_type_tag(bytes)? {
        if tag == TAG_CAP_REF {
            // Validate framing so malformed CapRef still surfaces framing errors,
            // then reject as capability-in-data.
            let mut cursor = ReadCursor::new(bytes);
            let _payload = cursor.read_envelope_payload(TAG_CAP_REF)?;
            cursor.expect_eof()?;
            return Err(CanonicalError::CapabilityInData);
        }
        if tag != TAG_VALUE {
            return Err(CanonicalError::InvalidTypeTag {
                expected: TAG_VALUE,
                found: tag,
            });
        }
    }

    let value = Value::decode_canonical(bytes)?;
    // Defense in depth: even if a future path produced a capability, refuse it.
    if contains_capability(&value) {
        return Err(CanonicalError::CapabilityInData);
    }
    Ok(value)
}

/// Encode via the data path (refuses capability-bearing values).
pub fn encode_data(value: &Value) -> Result<Vec<u8>, CanonicalError> {
    encode_data_value(value)
}

/// Round-trip helper used by tests: `decode_data(encode_data(v)) == v` for pure data.
pub fn round_trip_data(value: &Value) -> Result<Value, CanonicalError> {
    let bytes = encode_data(value)?;
    decode_data_value(&bytes)
}

fn peek_type_tag(bytes: &[u8]) -> Result<Option<u8>, CanonicalError> {
    if bytes.is_empty() {
        return Ok(None);
    }
    // version must be first; if short, let the full decoder report UnexpectedEof.
    if bytes.len() < 2 {
        return Ok(None);
    }
    if bytes[0] != CANONICAL_VERSION {
        // Defer to full decoder for the precise InvalidVersion.
        return Ok(None);
    }
    Ok(Some(bytes[1]))
}

/// Kernel-mediated CapRef codec (not the data path). Exposed for golden-vector
/// fixtures that pin the CapRef byte layout (R-CANON-05/11) and for future
/// kernel use. Callers outside the kernel must not use this for data payloads.
pub fn encode_cap_ref_kernel(cap: &CapRef) -> Result<Vec<u8>, CanonicalError> {
    cap.encode_canonical()
}

pub fn decode_cap_ref_kernel(bytes: &[u8]) -> Result<CapRef, CanonicalError> {
    CapRef::decode_canonical(bytes)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::Symbol;
    use std::collections::BTreeMap;

    #[test]
    fn integer_42_round_trip() {
        let v = Value::Integer(42);
        let bytes = encode_data(&v).unwrap();
        assert_eq!(
            bytes,
            vec![
                0x01, 0x00, 0x00, 0x00, 0x00, 0x09, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x2A
            ]
        );
        assert_eq!(decode_data_value(&bytes).unwrap(), v);
    }

    #[test]
    fn capref_standalone_rejected_by_data_path() {
        let cap = CapRef::from_kernel_parts(5, 2);
        let bytes = encode_cap_ref_kernel(&cap).unwrap();
        assert_eq!(
            bytes,
            vec![
                0x01, 0x30, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x02
            ]
        );
        assert_eq!(
            decode_data_value(&bytes),
            Err(CanonicalError::CapabilityInData)
        );
        // Kernel path still decodes it.
        assert_eq!(decode_cap_ref_kernel(&bytes).unwrap(), cap);
    }

    #[test]
    fn capability_discriminant_rejected() {
        // Manually craft Value envelope with TAG_CAPABILITY payload.
        let cap_env = encode_cap_ref_kernel(&CapRef::from_kernel_parts(1, 1)).unwrap();
        let mut payload = vec![Value::TAG_CAPABILITY];
        payload.extend_from_slice(&cap_env);
        let bytes = crate::canonical::envelope(TAG_VALUE, &payload).unwrap();
        assert_eq!(
            decode_data_value(&bytes),
            Err(CanonicalError::CapabilityInData)
        );
    }

    #[test]
    fn duplicate_map_key_rejected() {
        // Two entries with Symbol(1).
        let key = Symbol(1).encode_canonical().unwrap();
        let val = encode_data(&Value::Bool(true)).unwrap();
        let mut map_payload = Vec::new();
        map_payload.push(Value::TAG_MAP);
        map_payload.extend_from_slice(&2u32.to_be_bytes());
        map_payload.extend_from_slice(&key);
        map_payload.extend_from_slice(&val);
        map_payload.extend_from_slice(&key);
        map_payload.extend_from_slice(&val);
        let bytes = crate::canonical::envelope(TAG_VALUE, &map_payload).unwrap();
        assert_eq!(
            decode_data_value(&bytes),
            Err(CanonicalError::DuplicateMapKey)
        );
    }

    #[test]
    fn map_semantic_order_and_round_trip() {
        let mut map = BTreeMap::new();
        map.insert(Symbol(2), Value::Bool(true));
        map.insert(Symbol(1), Value::Bool(false));
        let v = Value::Map(map);
        let bytes = encode_data(&v).unwrap();
        // Expected from R-CANON-11 sketch (Symbol keys, Bool values).
        // Value envelope (tag 0x00). Payload = disc(1)+count(4)+2*(sym_env 10 + bool_env 8) = 41.
        // (The narrative sketch's standalone tag-0x07 / length-0x28 form is non-normative;
        // R-CANON-04 requires nested values inside a Value envelope.)
        let expect: Vec<u8> = vec![
            0x01, 0x00, 0x00, 0x00, 0x00, 0x29, // Value envelope, payload len 41
            0x07, // MAP discriminant
            0x00, 0x00, 0x00, 0x02, // count 2
            // Symbol(1) complete envelope
            0x01, 0x20, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01,
            // Bool(false) complete envelope
            0x01, 0x00, 0x00, 0x00, 0x00, 0x02, 0x01, 0x00, // Symbol(2)
            0x01, 0x20, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x02, // Bool(true)
            0x01, 0x00, 0x00, 0x00, 0x00, 0x02, 0x01, 0x01,
        ];
        assert_eq!(bytes, expect);
        assert_eq!(decode_data_value(&bytes).unwrap(), v);
    }

    #[test]
    fn le_length_rejected() {
        // LE length for Integer(42) would put length bytes reversed.
        // Valid: 01 00 00 00 00 09 ...
        // LE-ish: 01 00 09 00 00 00 ... → length = 0x09000000, then UnexpectedEof.
        let le = vec![
            0x01, 0x00, 0x09, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x2A,
        ];
        assert!(decode_data_value(&le).is_err());
    }

    #[test]
    fn trailing_bytes_rejected() {
        let mut bytes = encode_data(&Value::Integer(1)).unwrap();
        bytes.push(0xFF);
        assert!(matches!(
            decode_data_value(&bytes),
            Err(CanonicalError::TrailingBytes { .. })
        ));
    }

    #[test]
    fn invalid_version_rejected() {
        let mut bytes = encode_data(&Value::Unit).unwrap();
        bytes[0] = 0x02;
        assert!(matches!(
            decode_data_value(&bytes),
            Err(CanonicalError::InvalidVersion { .. })
        ));
    }

    #[test]
    fn encode_refuses_capability_value() {
        let v = Value::Capability(CapRef::from_kernel_parts(0, 0));
        assert_eq!(encode_data(&v), Err(CanonicalError::CapabilityInData));
    }
}
