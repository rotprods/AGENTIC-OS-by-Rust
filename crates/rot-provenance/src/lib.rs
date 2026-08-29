use rot_id::EvidenceId;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum EpistemicClass { Fact, Observation, Inference, Proposal, Decision, Prediction, Unknown }

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum AuthorityClass { Constitutional, ProviderEvidence, IdentityAuthority, EventAuthority, DerivedProjection, IntelligenceProposal, None }

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Provenance {
    pub epistemic_class: EpistemicClass,
    pub authority_class: AuthorityClass,
    pub evidence_ids: Vec<EvidenceId>,
    pub confidence: Option<f64>,
}

impl Provenance {
    pub fn authoritative_fact(authority_class: AuthorityClass, evidence_ids: Vec<EvidenceId>) -> Self {
        Self { epistemic_class: EpistemicClass::Fact, authority_class, evidence_ids, confidence: None }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn inference_is_not_fact() { assert_ne!(EpistemicClass::Inference, EpistemicClass::Fact); }
}
