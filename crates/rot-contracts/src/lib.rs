use serde::{Deserialize, Serialize};
use thiserror::Error;

pub const CONTRACT_VERSION: &str = "rot.contracts.v1";

#[derive(Debug, Error, PartialEq, Eq)]
pub enum ContractError {
    #[error("field `{0}` must not be empty")]
    EmptyField(&'static str),
    #[error("invalid identifier: {0}")]
    InvalidIdentifier(String),
    #[error("invalid timestamp: {0}")]
    InvalidTimestamp(String),
    #[error("non-finite JSON number is forbidden")]
    NonFiniteNumber,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct TenantId(String);

impl TenantId {
    pub fn new(value: impl Into<String>) -> Result<Self, ContractError> {
        let value = value.into();
        if value.is_empty() { return Err(ContractError::EmptyField("tenant_id")); }
        Ok(Self(value))
    }
    pub fn as_str(&self) -> &str { &self.0 }
}

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Scope(String);

impl Scope {
    pub fn new(value: impl Into<String>) -> Result<Self, ContractError> {
        let value = value.into();
        if value.is_empty() { return Err(ContractError::EmptyField("scope")); }
        Ok(Self(value))
    }
    pub fn as_str(&self) -> &str { &self.0 }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn rejects_empty_tenant() { assert_eq!(TenantId::new(""), Err(ContractError::EmptyField("tenant_id"))); }
    #[test]
    fn preserves_scope_bytes() { assert_eq!(Scope::new("repo:Rot/X").unwrap().as_str(), "repo:Rot/X"); }
}
