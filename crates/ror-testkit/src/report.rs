//! Mutation result taxonomy and kill-rate arithmetic (R-TEST-05).

/// Canonical classification (R-TEST-05/06; M9 preflight §8).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Classification {
    Killed,
    Survived,
    Equivalent,
    NotRun,
    Inconclusive,
}

impl Classification {
    pub fn as_str(self) -> &'static str {
        match self {
            Classification::Killed => "KILLED",
            Classification::Survived => "SURVIVED",
            Classification::Equivalent => "EQUIVALENT",
            Classification::NotRun => "NOT-RUN",
            Classification::Inconclusive => "INCONCLUSIVE",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "KILLED" => Some(Self::Killed),
            "SURVIVED" => Some(Self::Survived),
            "EQUIVALENT" => Some(Self::Equivalent),
            "NOT-RUN" => Some(Self::NotRun),
            "INCONCLUSIVE" => Some(Self::Inconclusive),
            _ => None,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MutantResult {
    pub id: String,
    pub classification: Classification,
    pub build_ok: bool,
    pub targeted_failed: bool,
    pub differential_failed: bool,
    pub kill_evidence: String,
    pub security: bool,
    pub obligations: Vec<String>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct KillRate {
    pub registered: usize,
    pub equivalent: usize,
    pub non_equivalent: usize,
    pub killed: usize,
    pub survived: usize,
    pub not_run: usize,
    pub inconclusive: usize,
}

impl KillRate {
    pub fn from_results(results: &[MutantResult]) -> Self {
        let registered = results.len();
        let mut equivalent = 0usize;
        let mut killed = 0usize;
        let mut survived = 0usize;
        let mut not_run = 0usize;
        let mut inconclusive = 0usize;
        for r in results {
            match r.classification {
                Classification::Equivalent => equivalent += 1,
                Classification::Killed => killed += 1,
                Classification::Survived => survived += 1,
                Classification::NotRun => not_run += 1,
                Classification::Inconclusive => inconclusive += 1,
            }
        }
        let non_equivalent = registered.saturating_sub(equivalent);
        Self {
            registered,
            equivalent,
            non_equivalent,
            killed,
            survived,
            not_run,
            inconclusive,
        }
    }

    /// Percentage over non-equivalent denominator (R-TEST-05).
    /// Returns None if denominator is zero.
    pub fn percent(&self) -> Option<u32> {
        if self.non_equivalent == 0 {
            return None;
        }
        // Only KILLED counts toward numerator; survivors/not-run/inconclusive do not.
        Some(((self.killed as u64) * 100 / (self.non_equivalent as u64)) as u32)
    }

    pub fn is_complete_100(&self) -> bool {
        self.percent() == Some(100)
            && self.survived == 0
            && self.not_run == 0
            && self.inconclusive == 0
            && self.killed == self.non_equivalent
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RunSummary {
    pub kill_rate: KillRate,
    pub critical_survived: bool,
    pub results: Vec<MutantResult>,
}

impl RunSummary {
    pub fn from_results(results: Vec<MutantResult>) -> Self {
        let critical_survived = results
            .iter()
            .any(|r| r.security && r.classification == Classification::Survived);
        let kill_rate = KillRate::from_results(&results);
        Self {
            kill_rate,
            critical_survived,
            results,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn r(id: &str, c: Classification, sec: bool) -> MutantResult {
        MutantResult {
            id: id.into(),
            classification: c,
            build_ok: true,
            targeted_failed: c == Classification::Killed,
            differential_failed: false,
            kill_evidence: String::new(),
            security: sec,
            obligations: vec![],
        }
    }

    #[test]
    fn kill_rate_100() {
        let rs = vec![
            r("M001", Classification::Killed, false),
            r("M002", Classification::Killed, true),
        ];
        let k = KillRate::from_results(&rs);
        assert_eq!(k.percent(), Some(100));
        assert!(k.is_complete_100());
    }

    #[test]
    fn survivor_blocks_100() {
        let rs = vec![
            r("M001", Classification::Killed, false),
            r("M002", Classification::Survived, true),
        ];
        let k = KillRate::from_results(&rs);
        assert_eq!(k.percent(), Some(50));
        assert!(!k.is_complete_100());
        let s = RunSummary::from_results(rs);
        assert!(s.critical_survived);
    }

    #[test]
    fn not_run_not_killed() {
        let rs = vec![r("M001", Classification::NotRun, false)];
        let k = KillRate::from_results(&rs);
        assert_eq!(k.percent(), Some(0));
        assert!(!k.is_complete_100());
    }

    #[test]
    fn equivalent_excluded_from_denominator() {
        let rs = vec![
            r("M001", Classification::Killed, false),
            r("M002", Classification::Equivalent, false),
        ];
        let k = KillRate::from_results(&rs);
        assert_eq!(k.non_equivalent, 1);
        assert_eq!(k.percent(), Some(100));
        assert!(k.is_complete_100());
    }

    #[test]
    fn taxonomy_labels_distinct() {
        assert_ne!(
            Classification::NotRun.as_str(),
            Classification::Killed.as_str()
        );
        assert_ne!(
            Classification::Survived.as_str(),
            Classification::Killed.as_str()
        );
        assert_ne!(
            Classification::Inconclusive.as_str(),
            Classification::Killed.as_str()
        );
    }
}
