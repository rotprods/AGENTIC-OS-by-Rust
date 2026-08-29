use rot_contracts::ContractError;
use serde::Serialize;
use serde_json::Value;

const MAX_SAFE_INTEGER: f64 = 9_007_199_254_740_991.0;

pub fn canonical_value<T: Serialize>(value: &T) -> Result<Value, ContractError> {
    let value = serde_json::to_value(value).map_err(|_| ContractError::NonFiniteNumber)?;
    validate_i_json(&value)?;
    Ok(value)
}

pub fn canonical_bytes<T: Serialize>(value: &T) -> Result<Vec<u8>, ContractError> {
    let value = canonical_value(value)?;
    serde_jcs::to_vec(&value).map_err(|_| ContractError::NonFiniteNumber)
}

fn validate_i_json(value: &Value) -> Result<(), ContractError> {
    match value {
        Value::Object(object) => {
            for child in object.values() {
                validate_i_json(child)?;
            }
        }
        Value::Array(items) => {
            for child in items {
                validate_i_json(child)?;
            }
        }
        Value::Number(number) => {
            if let Some(integer) = number.as_i64() {
                if integer.unsigned_abs() > MAX_SAFE_INTEGER as u64 {
                    return Err(ContractError::UnsafeInteger);
                }
            } else if let Some(integer) = number.as_u64() {
                if integer > MAX_SAFE_INTEGER as u64 {
                    return Err(ContractError::UnsafeInteger);
                }
            } else if let Some(float) = number.as_f64() {
                if !float.is_finite() {
                    return Err(ContractError::NonFiniteNumber);
                }
                if float.fract() == 0.0 && float.abs() > MAX_SAFE_INTEGER {
                    return Err(ContractError::UnsafeInteger);
                }
            } else {
                return Err(ContractError::NonFiniteNumber);
            }
        }
        Value::Null | Value::Bool(_) | Value::String(_) => {}
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn canonical(value: Value) -> String {
        String::from_utf8(canonical_bytes(&value).unwrap()).unwrap()
    }

    #[test]
    fn sorts_nested_object_keys() {
        assert_eq!(
            canonical(json!({"z":1,"a":{"y":2,"b":3}})),
            r#"{"a":{"b":3,"y":2},"z":1}"#
        );
    }

    #[test]
    fn preserves_array_order() {
        assert_eq!(
            canonical(json!([{"b":1,"a":2},3,2,1])),
            r#"[{"a":2,"b":1},3,2,1]"#
        );
    }

    #[test]
    fn sorts_object_keys_by_utf16_code_units() {
        assert_eq!(canonical(json!({"\u{e000}":2,"😀":1})), "{\"😀\":1,\"\":2}");
    }

    #[test]
    fn matches_ecmascript_number_boundaries() {
        assert_eq!(canonical(json!({"n": 1e-6})), "{\"n\":0.000001}");
        assert_eq!(canonical(json!({"n": 1e-7})), "{\"n\":1e-7}");
        assert_eq!(canonical(json!({"n": 1e20})), "{\"n\":100000000000000000000}");
        assert_eq!(canonical(json!({"n": 1e21})), "{\"n\":1e+21}");
        assert_eq!(canonical(json!({"n": -0.0})), "{\"n\":0}");
    }

    #[test]
    fn rejects_unsafe_integers() {
        assert_eq!(
            canonical_bytes(&json!({"n": 9_007_199_254_740_992_i64})),
            Err(ContractError::UnsafeInteger)
        );
    }
}
