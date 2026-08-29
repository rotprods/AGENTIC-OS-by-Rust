use rot_contracts::ContractError;
use rot_id::EvidenceId;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum EpistemicClass {
    Fact,
    Observation,
    Inference,
    Proposal,
    Decision,
    Prediction,
    Unknown,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum AuthorityClass {
    Constitutional,
    ProviderEvidence,
    IdentityAuthority,
    EventAuthority,
    DerivedProjection,
    IntelligenceProposal,
    None,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct Confidence(f64);

impl Confidence {
    pub fn new(value: f64) -> Result<Self, ContractError> {
        if !value.is_finite() || !(0.0..=1.0).contains(&value) {
            return Err(ContractError::InvalidConfidence);
        }
        Ok(Self(value))
    }

    pub fn get(self) -> f64 {
        self.0
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Provenance {
    pub epistemic_class: EpistemicClass,
    pub authority_class: AuthorityClass,
    pub evidence_ids: Vec<EvidenceId>,
    pub confidence: Option<Confidence>,
}

impl Provenance {
    pub fn authoritative_fact(
        authority_class: AuthorityClass,
        evidence_ids: Vec<EvidenceId>,
    ) -> Self {
        Self {
            epistemic_class: EpistemicClass::Fact,
            authority_class,
            evidence_ids,
            confidence: None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn inference_is_not_fact() {
        assert_ne!(EpistemicClass::Inference, EpistemicClass::Fact);
    }

    #[test]
    fn confidence_is_bounded_and_finite() {
        assert_eq!(Confidence::new(0.0).unwrap().get(), 0.0);
        assert_eq!(Confidence::new(1.0).unwrap().get(), 1.0);
        assert!(Confidence::new(-0.01).is_err());
        assert!(Confidence::new(1.01).is_err());
        assert!(Confidence::new(f64::NAN).is_err());
        assert!(Confidence::new(f64::INFINITY).is_err());
    }
}
