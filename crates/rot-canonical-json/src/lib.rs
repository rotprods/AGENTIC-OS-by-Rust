use rot_contracts::ContractError;
use serde::Serialize;
use serde_json::{Map, Value};

pub fn canonical_value<T: Serialize>(value: &T) -> Result<Value, ContractError> {
    let value = serde_json::to_value(value).map_err(|_| ContractError::NonFiniteNumber)?;
    normalize(value)
}

pub fn canonical_bytes<T: Serialize>(value: &T) -> Result<Vec<u8>, ContractError> {
    let normalized = canonical_value(value)?;
    serde_json::to_vec(&normalized).map_err(|_| ContractError::NonFiniteNumber)
}

fn normalize(value: Value) -> Result<Value, ContractError> {
    match value {
        Value::Object(object) => {
            let mut keys: Vec<_> = object.keys().cloned().collect();
            keys.sort();
            let mut sorted = Map::new();
            for key in keys {
                let child = object.get(&key).expect("key came from map").clone();
                sorted.insert(key, normalize(child)?);
            }
            Ok(Value::Object(sorted))
        }
        Value::Array(items) => Ok(Value::Array(
            items
                .into_iter()
                .map(normalize)
                .collect::<Result<_, _>>()?,
        )),
        Value::Number(number) => {
            if number.as_f64().is_some_and(|n| !n.is_finite()) {
                return Err(ContractError::NonFiniteNumber);
            }
            Ok(Value::Number(number))
        }
        scalar => Ok(scalar),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn sorts_nested_object_keys() {
        let bytes = canonical_bytes(&json!({"z":1,"a":{"y":2,"b":3}})).unwrap();
        assert_eq!(
            String::from_utf8(bytes).unwrap(),
            r#"{"a":{"b":3,"y":2},"z":1}"#
        );
    }

    #[test]
    fn preserves_array_order() {
        let bytes = canonical_bytes(&json!([{"b":1,"a":2},3,2,1])).unwrap();
        assert_eq!(
            String::from_utf8(bytes).unwrap(),
            r#"[{"a":2,"b":1},3,2,1]"#
        );
    }
}
