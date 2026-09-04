//! Machine-checkable consumer of `mutations/registry.toml` (R-TEST-04).
//!
//! TOML is parsed with a minimal hand-written reader (no crates.io deps).

use std::collections::BTreeSet;

/// Expected registered count (final/04 M001–M042).
pub const EXPECTED_COUNT: usize = 42;

/// One registry row (derived consumer fields only).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MutantRecord {
    pub id: String,
    pub defect: String,
    pub obligations: Vec<String>,
    pub component: String,
    pub security: bool,
    pub differential: bool,
    pub equiv: bool,
    pub kind: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Registry {
    pub schema_version: u32,
    pub authority: String,
    pub mutants: Vec<MutantRecord>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RegistryError {
    Parse(String),
    MissingIds(Vec<String>),
    DuplicateIds(Vec<String>),
    WrongCount { expected: usize, got: usize },
    UnexpectedId(String),
}

impl std::fmt::Display for RegistryError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RegistryError::Parse(s) => write!(f, "parse: {s}"),
            RegistryError::MissingIds(v) => write!(f, "missing ids: {v:?}"),
            RegistryError::DuplicateIds(v) => write!(f, "duplicate ids: {v:?}"),
            RegistryError::WrongCount { expected, got } => {
                write!(f, "count expected {expected} got {got}")
            }
            RegistryError::UnexpectedId(s) => write!(f, "unexpected id {s}"),
        }
    }
}

/// Canonical expected ID list M001…M042.
pub fn expected_ids() -> Vec<String> {
    (1..=EXPECTED_COUNT).map(|i| format!("M{i:03}")).collect()
}

/// Load registry from TOML text (subset sufficient for our file).
pub fn load_registry_from_str(src: &str) -> Result<Registry, RegistryError> {
    let mut schema_version = 0u32;
    let mut authority = String::new();
    let mut mutants: Vec<MutantRecord> = Vec::new();
    let mut current: Option<MutantRecord> = None;

    let flush = |current: &mut Option<MutantRecord>, mutants: &mut Vec<MutantRecord>| {
        if let Some(m) = current.take() {
            mutants.push(m);
        }
    };

    for raw in src.lines() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        if line == "[[mutant]]" {
            flush(&mut current, &mut mutants);
            current = Some(MutantRecord {
                id: String::new(),
                defect: String::new(),
                obligations: Vec::new(),
                component: String::new(),
                security: false,
                differential: false,
                equiv: false,
                kind: "machine".to_string(),
            });
            continue;
        }
        if let Some(rest) = line.strip_prefix("schema_version") {
            schema_version = parse_assign_u32(rest)?;
            continue;
        }
        if let Some(rest) = line.strip_prefix("authority") {
            authority = parse_assign_string(rest)?;
            continue;
        }
        if current.is_none() {
            // top-level keys we ignore (requirement, kill_gate, method)
            continue;
        }
        let m = current.as_mut().unwrap();
        if let Some(rest) = line.strip_prefix("id") {
            m.id = parse_assign_string(rest)?;
        } else if let Some(rest) = line.strip_prefix("defect") {
            m.defect = parse_assign_string(rest)?;
        } else if let Some(rest) = line.strip_prefix("obligations") {
            m.obligations = parse_assign_string_array(rest)?;
        } else if let Some(rest) = line.strip_prefix("component") {
            m.component = parse_assign_string(rest)?;
        } else if let Some(rest) = line.strip_prefix("security") {
            m.security = parse_assign_bool(rest)?;
        } else if let Some(rest) = line.strip_prefix("differential") {
            m.differential = parse_assign_bool(rest)?;
        } else if let Some(rest) = line.strip_prefix("equiv") {
            m.equiv = parse_assign_bool(rest)?;
        } else if let Some(rest) = line.strip_prefix("kind") {
            m.kind = parse_assign_string(rest)?;
        }
    }
    flush(&mut current, &mut mutants);

    validate(&mutants)?;
    Ok(Registry {
        schema_version,
        authority,
        mutants,
    })
}

fn validate(mutants: &[MutantRecord]) -> Result<(), RegistryError> {
    if mutants.len() != EXPECTED_COUNT {
        return Err(RegistryError::WrongCount {
            expected: EXPECTED_COUNT,
            got: mutants.len(),
        });
    }
    let expected: BTreeSet<String> = expected_ids().into_iter().collect();
    let mut seen = BTreeSet::new();
    let mut dups = Vec::new();
    for m in mutants {
        if m.id.is_empty() {
            return Err(RegistryError::Parse("empty mutant id".into()));
        }
        if !expected.contains(&m.id) {
            return Err(RegistryError::UnexpectedId(m.id.clone()));
        }
        if !seen.insert(m.id.clone()) {
            dups.push(m.id.clone());
        }
    }
    if !dups.is_empty() {
        return Err(RegistryError::DuplicateIds(dups));
    }
    let missing: Vec<String> = expected.difference(&seen).cloned().collect();
    if !missing.is_empty() {
        return Err(RegistryError::MissingIds(missing));
    }
    Ok(())
}

fn parse_assign_string(rest: &str) -> Result<String, RegistryError> {
    let rest = rest.trim().trim_start_matches('=').trim();
    if rest.starts_with('"') && rest.ends_with('"') && rest.len() >= 2 {
        Ok(rest[1..rest.len() - 1].to_string())
    } else {
        Err(RegistryError::Parse(format!("bad string: {rest}")))
    }
}

fn parse_assign_u32(rest: &str) -> Result<u32, RegistryError> {
    let rest = rest.trim().trim_start_matches('=').trim();
    rest.parse()
        .map_err(|_| RegistryError::Parse(format!("bad u32: {rest}")))
}

fn parse_assign_bool(rest: &str) -> Result<bool, RegistryError> {
    let rest = rest.trim().trim_start_matches('=').trim();
    match rest {
        "true" => Ok(true),
        "false" => Ok(false),
        _ => Err(RegistryError::Parse(format!("bad bool: {rest}"))),
    }
}

fn parse_assign_string_array(rest: &str) -> Result<Vec<String>, RegistryError> {
    let rest = rest.trim().trim_start_matches('=').trim();
    if !rest.starts_with('[') || !rest.ends_with(']') {
        return Err(RegistryError::Parse(format!("bad array: {rest}")));
    }
    let inner = &rest[1..rest.len() - 1];
    let mut out = Vec::new();
    for part in inner.split(',') {
        let p = part.trim();
        if p.is_empty() {
            continue;
        }
        if p.starts_with('"') && p.ends_with('"') && p.len() >= 2 {
            out.push(p[1..p.len() - 1].to_string());
        } else {
            return Err(RegistryError::Parse(format!("bad array elem: {p}")));
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = r#"
schema_version = 1
authority = "final/04"

[[mutant]]
id = "M001"
defect = "reverse argument evaluation"
obligations = ["R-CEK-05"]
component = "ror-runtime"
security = false
differential = true
equiv = false
"#;

    #[test]
    fn parse_one_row() {
        // incomplete registry must fail count
        let err = load_registry_from_str(SAMPLE).unwrap_err();
        assert!(matches!(err, RegistryError::WrongCount { .. }));
    }

    #[test]
    fn expected_ids_stable() {
        let ids = expected_ids();
        assert_eq!(ids.len(), 42);
        assert_eq!(ids[0], "M001");
        assert_eq!(ids[41], "M042");
    }

    #[test]
    fn loads_repo_registry_toml() {
        // Consumer of mutations/registry.toml at repo root (path relative to CARGO_MANIFEST_DIR).
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../mutations/registry.toml");
        let src = std::fs::read_to_string(path).expect("registry.toml present");
        let reg = load_registry_from_str(&src).expect("valid registry");
        assert_eq!(reg.mutants.len(), 42);
        assert_eq!(reg.mutants[0].id, "M001");
        assert_eq!(reg.mutants[41].id, "M042");
        assert!(reg.mutants.iter().all(|m| !m.equiv));
    }
}
