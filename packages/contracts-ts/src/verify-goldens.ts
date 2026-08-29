import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { canonicalize, type JsonValue } from "./canonical-json.js";
import {
  deriveCanonicalEntityId,
  deriveSourceRecordId,
  normalizeStrictSourceIdentity,
  type CanonicalEntityCreationCommand,
  type SourceIdentityKeyInput,
} from "./identity-kernel.js";

type CanonicalVector = { name: string; value: JsonValue; expected_canonical: string; expected_sha256: string };
type CanonicalFixture = { vectors: CanonicalVector[] };
type SourceVector = {
  name: string;
  input: SourceIdentityKeyInput;
  expected: {
    schema_version: "1.0.0";
    normalization_profile_id: string;
    provider: string;
    account_id: string;
    workspace_id: string | null;
    resource_type: string;
    external_id: string;
    source_record_id: string;
  };
};
type EntityVector = { name: string; command: CanonicalEntityCreationCommand; expected_entity_id: string };
type IdentityFixture = { source_vectors: SourceVector[]; entity_vectors: EntityVector[] };

const here = dirname(fileURLToPath(import.meta.url));
const canonicalFixture = JSON.parse(
  readFileSync(resolve(here, "../../../fixtures/golden/canonical-json.v1.json"), "utf8"),
) as CanonicalFixture;

for (const vector of canonicalFixture.vectors) {
  const canonical = canonicalize(vector.value);
  if (canonical !== vector.expected_canonical) throw new Error(`${vector.name}: canonical mismatch: ${canonical}`);
  const hash = `sha256:${createHash("sha256").update(canonical, "utf8").digest("hex")}`;
  if (hash !== vector.expected_sha256) throw new Error(`${vector.name}: hash mismatch: ${hash}`);
}

const identityFixture = JSON.parse(
  readFileSync(resolve(here, "../../../fixtures/golden/identity.v1.json"), "utf8"),
) as IdentityFixture;

for (const vector of identityFixture.source_vectors) {
  const normalized = normalizeStrictSourceIdentity(vector.input);
  const { source_record_id: expectedId, ...expectedKey } = vector.expected;
  if (canonicalize(normalized as unknown as JsonValue) !== canonicalize(expectedKey as unknown as JsonValue)) {
    throw new Error(`${vector.name}: normalized identity mismatch`);
  }
  const actualId = deriveSourceRecordId(normalized);
  if (actualId !== expectedId) throw new Error(`${vector.name}: source id mismatch: ${actualId}`);
}

for (const vector of identityFixture.entity_vectors) {
  const actualId = deriveCanonicalEntityId(vector.command);
  if (actualId !== vector.expected_entity_id) throw new Error(`${vector.name}: entity id mismatch: ${actualId}`);
}

console.log(
  `TypeScript golden parity PASS (${canonicalFixture.vectors.length} canonical + ${identityFixture.source_vectors.length + identityFixture.entity_vectors.length} identity vectors)`,
);
