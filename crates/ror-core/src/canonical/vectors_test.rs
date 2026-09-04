//! Golden-vector loader and M1 acceptance tests (R-CANON-11/13).

#[cfg(test)]
mod golden {
    use crate::canonical::data_decode::{decode_cap_ref_kernel, decode_data_value, encode_data};
    use crate::canonical::CanonicalError;
    use crate::types::{CapRef, Symbol, Value};
    use std::collections::BTreeMap;
    use std::path::PathBuf;

    fn vectors_dir() -> PathBuf {
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("vectors/canonical")
    }

    fn load_hex_file(name: &str) -> Vec<u8> {
        let text = std::fs::read_to_string(vectors_dir().join(name))
            .unwrap_or_else(|e| panic!("read {name}: {e}"));
        let mut hex = String::new();
        for line in text.lines() {
            let line = line.split('#').next().unwrap_or("").trim();
            for ch in line.chars() {
                if !ch.is_whitespace() {
                    hex.push(ch);
                }
            }
        }
        assert!(hex.len() % 2 == 0, "{name}: odd hex length");
        (0..hex.len())
            .step_by(2)
            .map(|i| u8::from_str_radix(&hex[i..i + 2], 16).expect("hex"))
            .collect()
    }

    /// Flip multi-byte big-endian integer fields to little-endian where the
    /// sketch would have used LE — used as a negative fixture (R-CANON-13).
    fn le_permute_length(bytes: &[u8]) -> Vec<u8> {
        // version, tag, then 4-byte length — reverse the length word.
        assert!(bytes.len() >= 6);
        let mut out = bytes.to_vec();
        out[2..6].reverse();
        out
    }

    #[test]
    fn golden_integer_42() {
        let bytes = load_hex_file("integer_42.bin.hex");
        assert_eq!(decode_data_value(&bytes).unwrap(), Value::Integer(42));
        assert_eq!(encode_data(&Value::Integer(42)).unwrap(), bytes);
        assert!(decode_data_value(&le_permute_length(&bytes)).is_err());
    }

    #[test]
    fn golden_unit() {
        let bytes = load_hex_file("unit.bin.hex");
        assert_eq!(decode_data_value(&bytes).unwrap(), Value::Unit);
        assert_eq!(encode_data(&Value::Unit).unwrap(), bytes);
    }

    #[test]
    fn golden_bool_true() {
        let bytes = load_hex_file("bool_true.bin.hex");
        assert_eq!(decode_data_value(&bytes).unwrap(), Value::Bool(true));
        assert_eq!(encode_data(&Value::Bool(true)).unwrap(), bytes);
    }

    #[test]
    fn golden_capref_kernel_only() {
        let bytes = load_hex_file("capref_5_2.bin.hex");
        let cap = CapRef::from_kernel_parts(5, 2);
        assert_eq!(decode_cap_ref_kernel(&bytes).unwrap(), cap);
        assert_eq!(
            decode_data_value(&bytes),
            Err(CanonicalError::CapabilityInData)
        );
    }

    #[test]
    fn golden_map_sym_bool() {
        let bytes = load_hex_file("map_sym_bool.bin.hex");
        let mut map = BTreeMap::new();
        map.insert(Symbol(1), Value::Bool(false));
        map.insert(Symbol(2), Value::Bool(true));
        let v = Value::Map(map);
        assert_eq!(decode_data_value(&bytes).unwrap(), v);
        assert_eq!(encode_data(&v).unwrap(), bytes);
        assert!(decode_data_value(&le_permute_length(&bytes)).is_err());
    }

    #[test]
    fn determinism_same_value_same_bytes() {
        let v = Value::List(vec![
            Value::Integer(-1),
            Value::String("hi".into()),
            Value::Symbol(Symbol(7)),
        ]);
        let a = encode_data(&v).unwrap();
        let b = encode_data(&v).unwrap();
        assert_eq!(a, b);
        assert_eq!(decode_data_value(&a).unwrap(), v);
    }

    #[test]
    fn digest_stable_for_integer_42() {
        use crate::digest::StateDigest;
        let bytes = encode_data(&Value::Integer(42)).unwrap();
        let d1 = StateDigest::of_bytes(&bytes);
        let d2 = StateDigest::of_bytes(&bytes);
        assert_eq!(d1, d2);
        // Different value ⇒ different digest (over this distribution).
        let other = encode_data(&Value::Integer(43)).unwrap();
        assert_ne!(StateDigest::of_bytes(&other), d1);
    }
}
