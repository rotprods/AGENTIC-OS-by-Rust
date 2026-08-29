use serde::Deserialize;
use serde_json::Value;
use std::collections::BTreeMap;

#[derive(Debug, Deserialize)]
struct Corpus {
    cases: Vec<CorpusCase>,
}

#[derive(Debug, Deserialize)]
struct CorpusCase {
    name: String,
    schema: String,
    schema_valid: bool,
    semantic_valid: bool,
    value: Value,
}

pub fn validate_schema(schema: &Value, value: &Value) -> Result<bool, String> {
    let validator = jsonschema::validator_for(schema).map_err(|error| error.to_string())?;
    Ok(validator.is_valid(value))
}

pub fn validate_semantics(schema_name: &str, value: &Value) -> bool {
    match schema_name {
        "event-append-request.v1.schema.json" => {
            let stream_tenant = value.pointer("/stream/tenant_id").and_then(Value::as_str);
            let caller_tenant = value.pointer("/caller/tenant_id").and_then(Value::as_str);
            stream_tenant.is_some() && stream_tenant == caller_tenant
        }
        "source-identity-key.v1.schema.json" => true,
        _ => false,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn g1_schema_and_semantic_corpus_matches() {
        let corpus: Corpus = serde_json::from_str(include_str!(
            "../../../fixtures/schema/g1-contract-corpus.v1.json"
        ))
        .unwrap();
        let schemas = BTreeMap::from([
            (
                "source-identity-key.v1.schema.json",
                serde_json::from_str::<Value>(include_str!(
                    "../../../schemas/source-identity-key.v1.schema.json"
                ))
                .unwrap(),
            ),
            (
                "event-append-request.v1.schema.json",
                serde_json::from_str::<Value>(include_str!(
                    "../../../schemas/event-append-request.v1.schema.json"
                ))
                .unwrap(),
            ),
        ]);

        for case in corpus.cases {
            let schema = schemas.get(case.schema.as_str()).unwrap();
            let actual_schema = validate_schema(schema, &case.value).unwrap();
            assert_eq!(actual_schema, case.schema_valid, "schema: {}", case.name);
            let actual_semantic = actual_schema && validate_semantics(&case.schema, &case.value);
            assert_eq!(
                actual_semantic, case.semantic_valid,
                "semantic: {}",
                case.name
            );
        }
    }
}
