import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { canonicalize, type JsonValue } from "./canonical-json.js";

type Vector = { name: string; value: JsonValue; expected_canonical: string; expected_sha256: string };
type Fixture = { vectors: Vector[] };

const here = dirname(fileURLToPath(import.meta.url));
const fixturePath = resolve(here, "../../../fixtures/golden/canonical-json.v1.json");
const fixture = JSON.parse(readFileSync(fixturePath, "utf8")) as Fixture;

for (const vector of fixture.vectors) {
  const canonical = canonicalize(vector.value);
  if (canonical !== vector.expected_canonical) {
    throw new Error(`${vector.name}: canonical mismatch: ${canonical}`);
  }
  const hash = `sha256:${createHash("sha256").update(canonical, "utf8").digest("hex")}`;
  if (hash !== vector.expected_sha256) throw new Error(`${vector.name}: hash mismatch: ${hash}`);
}
console.log(`TypeScript golden parity PASS (${fixture.vectors.length} vectors)`);
