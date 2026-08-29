use rot_contracts::ContractError;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct Rfc3339Timestamp(String);

impl Rfc3339Timestamp {
    pub fn parse(value: impl Into<String>) -> Result<Self, ContractError> {
        let value = value.into();
        let looks_utc = value.ends_with('Z');
        let looks_offset = value.len() >= 6 && value[value.len()-6..].chars().next().is_some_and(|c| c == '+' || c == '-');
        if !value.contains('T') || !(looks_utc || looks_offset) { return Err(ContractError::InvalidTimestamp(value)); }
        Ok(Self(value))
    }
    pub fn as_str(&self) -> &str { &self.0 }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BitemporalWindow {
    pub valid_from: Rfc3339Timestamp,
    pub valid_to: Option<Rfc3339Timestamp>,
    pub recorded_at: Rfc3339Timestamp,
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn rejects_naive_time() { assert!(Rfc3339Timestamp::parse("2026-08-29T19:00:00").is_err()); }
    #[test]
    fn accepts_utc_time() { assert!(Rfc3339Timestamp::parse("2026-08-29T17:00:00Z").is_ok()); }
}
