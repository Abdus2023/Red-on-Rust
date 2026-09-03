//! `Value` payload encode/decode (R-CANON-04/06/07/08/12).
//!
//! Nested values are complete envelopes. Map keys are `Symbol` envelopes ordered
//! by semantic `Ord` on the `u32` identity (BTreeMap iteration order). Duplicate
//! keys are rejected on decode.

use std::collections::BTreeMap;

use super::codec::{
    checked_length, CanonicalDecode, CanonicalEncode, CanonicalPayload, ReadCursor,
};
use super::error::CanonicalError;
use super::primitives::TAG_VALUE;
use crate::types::{CapRef, Symbol, Value};

impl CanonicalPayload for Value {
    const TYPE_TAG: u8 = TAG_VALUE;

    fn encode_payload(&self, out: &mut Vec<u8>) -> Result<(), CanonicalError> {
        match self {
            Value::Unit => out.push(Self::TAG_UNIT),
            Value::Bool(b) => {
                out.push(Self::TAG_BOOL);
                b.encode_payload(out)?;
            }
            Value::Integer(i) => {
                out.push(Self::TAG_INTEGER);
                i.encode_payload(out)?;
            }
            Value::String(s) => {
                out.push(Self::TAG_STRING);
                s.encode_payload(out)?;
            }
            Value::Symbol(sym) => {
                out.push(Self::TAG_SYMBOL);
                // Nested Symbol is a complete envelope (R-CANON-04).
                out.extend_from_slice(&sym.encode_canonical()?);
            }
            Value::Capability(_cap) => {
                // R-CANON-12: data-domain Value path never emits capability bytes.
                // Kernel path uses CapRef standalone codec only.
                return Err(CanonicalError::CapabilityInData);
            }
            Value::List(vec) => {
                out.push(Self::TAG_LIST);
                out.extend_from_slice(&checked_length(vec.len())?.to_be_bytes());
                for item in vec {
                    out.extend_from_slice(&item.encode_canonical()?);
                }
            }
            Value::Map(map) => {
                out.push(Self::TAG_MAP);
                out.extend_from_slice(&checked_length(map.len())?.to_be_bytes());
                // BTreeMap iterates in semantic Ord order on Symbol(u32).
                for (k, v) in map {
                    out.extend_from_slice(&k.encode_canonical()?);
                    out.extend_from_slice(&v.encode_canonical()?);
                }
            }
        }
        Ok(())
    }

    fn decode_payload(cursor: &mut ReadCursor<'_>) -> Result<Self, CanonicalError> {
        // Data-path decode: capability payloads are forbidden (R-CANON-12).
        decode_value_payload_data(cursor)
    }
}

impl CanonicalEncode for Value {}
impl CanonicalDecode for Value {}

/// Data-domain `Value` payload decoder (R-CANON-12): rejects capability.
pub(crate) fn decode_value_payload_data(
    cursor: &mut ReadCursor<'_>,
) -> Result<Value, CanonicalError> {
    let discriminant = cursor.read_byte()?;
    match discriminant {
        Value::TAG_UNIT => Ok(Value::Unit),
        Value::TAG_BOOL => Ok(Value::Bool(bool::decode_payload(cursor)?)),
        Value::TAG_INTEGER => Ok(Value::Integer(i64::decode_payload(cursor)?)),
        Value::TAG_STRING => Ok(Value::String(String::decode_payload(cursor)?)),
        Value::TAG_SYMBOL => {
            let sym_payload = cursor.read_envelope_payload(Symbol::TYPE_TAG)?;
            let mut sym_cursor = ReadCursor::new(sym_payload);
            let sym = Symbol::decode_payload(&mut sym_cursor)?;
            sym_cursor.expect_eof()?;
            Ok(Value::Symbol(sym))
        }
        Value::TAG_CAPABILITY => {
            // R-CANON-12: data decoder must not mint authority from bytes.
            // Consume the nested envelope for strictness, then reject.
            let _ = cursor.read_envelope_payload(CapRef::TYPE_TAG)?;
            Err(CanonicalError::CapabilityInData)
        }
        Value::TAG_LIST => {
            let count = cursor.read_u32_be()? as usize;
            // R-CANON-08: never preallocate from untrusted counts.
            let mut vec = Vec::new();
            for _ in 0..count {
                let elem_payload = cursor.read_envelope_payload(Value::TYPE_TAG)?;
                let mut elem_cursor = ReadCursor::new(elem_payload);
                let elem = decode_value_payload_data(&mut elem_cursor)?;
                elem_cursor.expect_eof()?;
                vec.push(elem);
            }
            Ok(Value::List(vec))
        }
        Value::TAG_MAP => {
            let count = cursor.read_u32_be()? as usize;
            let mut map: BTreeMap<Symbol, Value> = BTreeMap::new();
            for _ in 0..count {
                let key_payload = cursor.read_envelope_payload(Symbol::TYPE_TAG)?;
                let mut key_cursor = ReadCursor::new(key_payload);
                let key = Symbol::decode_payload(&mut key_cursor)?;
                key_cursor.expect_eof()?;

                let val_payload = cursor.read_envelope_payload(Value::TYPE_TAG)?;
                let mut val_cursor = ReadCursor::new(val_payload);
                let val = decode_value_payload_data(&mut val_cursor)?;
                val_cursor.expect_eof()?;

                // R-CANON-06: reject duplicate keys (injectivity).
                if map.insert(key, val).is_some() {
                    return Err(CanonicalError::DuplicateMapKey);
                }
            }
            Ok(Value::Map(map))
        }
        found => Err(CanonicalError::InvalidDiscriminant { found }),
    }
}

/// Encode a data-domain value. Refuses `Value::Capability` so the public data
/// path cannot emit authority bytes (symmetric with R-CANON-12 decode ban).
pub fn encode_data_value(value: &Value) -> Result<Vec<u8>, CanonicalError> {
    if contains_capability(value) {
        return Err(CanonicalError::CapabilityInData);
    }
    value.encode_canonical()
}

/// Total reachability predicate over the canonical data-domain `Value`
/// (R-MARSHAL-06 restricted to the data domain frozen at M1: List/Map only;
/// FunctionValue.env is out of scope until the machine domain lands).
pub fn contains_capability(value: &Value) -> bool {
    match value {
        Value::Capability(_) => true,
        Value::List(xs) => xs.iter().any(contains_capability),
        Value::Map(m) => m.values().any(contains_capability),
        Value::Unit | Value::Bool(_) | Value::Integer(_) | Value::String(_) | Value::Symbol(_) => {
            false
        }
    }
}
