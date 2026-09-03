//! Digest helpers over canonical bytes (R-CANON-09).
//!
//! `StateDigest = SHA-256(canonical_bytes)`;
//! `EffectDigest = SHA-256(canonical_bytes(effect))`.
//!
//! Implemented with a pure-Rust SHA-256 so M1 has no third-party crate
//! dependency (R-CANON-01: no external serializer defines the format; digests
//! are defined over our bytes alone).

use crate::canonical::{CanonicalEncode, CanonicalError};

/// 32-byte SHA-256 digest.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Digest(pub [u8; 32]);

/// State digest over arbitrary canonical bytes (R-CANON-09).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct StateDigest(pub [u8; 32]);

/// Effect digest over the canonical encoding of an effect (R-CANON-09).
///
/// Constructed from already-canonical effect bytes until the `Effect` type
/// itself is frozen (U-21).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct EffectDigest(pub [u8; 32]);

impl StateDigest {
    pub fn of_bytes(bytes: &[u8]) -> Self {
        StateDigest(sha256(bytes))
    }

    pub fn of_encoded<T: CanonicalEncode>(value: &T) -> Result<Self, CanonicalError> {
        let bytes = value.encode_canonical()?;
        Ok(Self::of_bytes(&bytes))
    }
}

impl EffectDigest {
    pub fn of_bytes(bytes: &[u8]) -> Self {
        EffectDigest(sha256(bytes))
    }
}

impl Digest {
    pub fn of_bytes(bytes: &[u8]) -> Self {
        Digest(sha256(bytes))
    }
}

/// SHA-256 (FIPS 180-4), pure Rust, no external crates.
pub fn sha256(message: &[u8]) -> [u8; 32] {
    // Initial hash values (first 32 bits of the fractional parts of the square
    // roots of the first 8 primes).
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
        0x5be0cd19,
    ];

    // Round constants (first 32 bits of the fractional parts of the cube roots
    // of the first 64 primes).
    const K: [u32; 64] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4,
        0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe,
        0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f,
        0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc,
        0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
        0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116,
        0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7,
        0xc67178f2,
    ];

    // Pre-processing (padding).
    let bit_len = (message.len() as u64)
        .checked_mul(8)
        .expect("message length overflow");
    let mut data = message.to_vec();
    data.push(0x80);
    while (data.len() % 64) != 56 {
        data.push(0x00);
    }
    data.extend_from_slice(&bit_len.to_be_bytes());

    // Process each 512-bit chunk.
    for chunk in data.chunks_exact(64) {
        let mut w = [0u32; 64];
        for (i, word) in chunk.chunks_exact(4).enumerate().take(16) {
            w[i] = u32::from_be_bytes([word[0], word[1], word[2], word[3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }

        let mut a = h[0];
        let mut b = h[1];
        let mut c = h[2];
        let mut d = h[3];
        let mut e = h[4];
        let mut f = h[5];
        let mut g = h[6];
        let mut hh = h[7];

        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let temp1 = hh
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(K[i])
                .wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let temp2 = s0.wrapping_add(maj);

            hh = g;
            g = f;
            f = e;
            e = d.wrapping_add(temp1);
            d = c;
            c = b;
            b = a;
            a = temp1.wrapping_add(temp2);
        }

        h[0] = h[0].wrapping_add(a);
        h[1] = h[1].wrapping_add(b);
        h[2] = h[2].wrapping_add(c);
        h[3] = h[3].wrapping_add(d);
        h[4] = h[4].wrapping_add(e);
        h[5] = h[5].wrapping_add(f);
        h[6] = h[6].wrapping_add(g);
        h[7] = h[7].wrapping_add(hh);
    }

    let mut out = [0u8; 32];
    for (i, word) in h.iter().enumerate() {
        out[i * 4..(i + 1) * 4].copy_from_slice(&word.to_be_bytes());
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Independent FIPS 180-4 / NIST-published known-answer vectors.
    /// These are not derived from this implementation.
    #[test]
    fn sha256_empty() {
        assert_eq!(
            sha256(b""),
            hex_to_bytes("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        );
    }

    #[test]
    fn sha256_abc() {
        assert_eq!(
            sha256(b"abc"),
            hex_to_bytes("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        );
    }

    #[test]
    fn sha256_two_block_nist() {
        // FIPS 180-4 multi-block example ("abcdbcde…nopq").
        let msg = b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq";
        assert_eq!(
            sha256(msg),
            hex_to_bytes("248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1")
        );
    }

    #[test]
    fn sha256_quick_brown_fox() {
        assert_eq!(
            sha256(b"The quick brown fox jumps over the lazy dog"),
            hex_to_bytes("d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592")
        );
    }

    #[test]
    fn sha256_boundary_lengths() {
        // Padding boundary: 55 bytes → single block; 56 → two blocks; 64; 65.
        let cases: &[(usize, &str)] = &[
            (
                55,
                "9f4390f8d30c2dd92ec9f095b65e2b9ae9b0a925a5258e241c9f1e910f734318",
            ),
            (
                56,
                "b35439a4ac6f0948b6d6f9e3c6af0f5f590ce20f1bde7090ef7970686ec6738a",
            ),
            (
                64,
                "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb",
            ),
            (
                65,
                "635361c48bb9eab14198e76ea8ab7f1a41685d6ad62aa9146d301d4f17eb0ae0",
            ),
        ];
        for &(n, expect) in cases {
            let msg = vec![b'a'; n];
            assert_eq!(sha256(&msg), hex_to_bytes(expect), "len={n}");
        }
    }

    fn hex_to_bytes(s: &str) -> [u8; 32] {
        let mut out = [0u8; 32];
        for i in 0..32 {
            out[i] = u8::from_str_radix(&s[i * 2..i * 2 + 2], 16).unwrap();
        }
        out
    }
}
