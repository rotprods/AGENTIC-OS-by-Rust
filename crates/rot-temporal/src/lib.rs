use rot_contracts::ContractError;
use serde::{Deserialize, Serialize};
use time::{OffsetDateTime, format_description::well_known::Rfc3339};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Rfc3339Timestamp(String);

impl Rfc3339Timestamp {
    pub fn parse(value: impl Into<String>) -> Result<Self, ContractError> {
        let value = value.into();
        OffsetDateTime::parse(&value, &Rfc3339)
            .map_err(|_| ContractError::InvalidTimestamp(value.clone()))?;
        Ok(Self(value))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }

    fn instant(&self) -> OffsetDateTime {
        OffsetDateTime::parse(&self.0, &Rfc3339).expect("validated at construction")
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BitemporalWindow {
    pub valid_from: Rfc3339Timestamp,
    pub valid_to: Option<Rfc3339Timestamp>,
    pub recorded_at: Rfc3339Timestamp,
}

impl BitemporalWindow {
    pub fn new(
        valid_from: Rfc3339Timestamp,
        valid_to: Option<Rfc3339Timestamp>,
        recorded_at: Rfc3339Timestamp,
    ) -> Result<Self, ContractError> {
        if valid_to
            .as_ref()
            .is_some_and(|end| end.instant() < valid_from.instant())
        {
            return Err(ContractError::InvalidTimestamp(
                "valid_to precedes valid_from".into(),
            ));
        }
        Ok(Self {
            valid_from,
            valid_to,
            recorded_at,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_naive_or_calendar_invalid_time() {
        assert!(Rfc3339Timestamp::parse("2026-08-29T19:00:00").is_err());
        assert!(Rfc3339Timestamp::parse("2026-02-31T19:00:00Z").is_err());
    }

    #[test]
    fn accepts_utc_and_offset_time() {
        assert!(Rfc3339Timestamp::parse("2026-08-29T17:00:00Z").is_ok());
        assert!(Rfc3339Timestamp::parse("2026-08-29T19:00:00+02:00").is_ok());
    }

    #[test]
    fn rejects_inverted_validity_window_across_offsets() {
        let start = Rfc3339Timestamp::parse("2026-08-29T19:00:00+02:00").unwrap();
        let end = Rfc3339Timestamp::parse("2026-08-29T16:59:59Z").unwrap();
        assert!(BitemporalWindow::new(start.clone(), Some(end), start).is_err());
    }
}
