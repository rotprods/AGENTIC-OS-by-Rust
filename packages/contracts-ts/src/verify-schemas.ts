import * as Ajv2020Module from "ajv/dist/2020.js";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

type Case = { name: string; schema: string; schema_valid: boolean; semantic_valid: boolean; value: unknown };
type Corpus = { cases: Case[] };

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../../..");
const corpus = JSON.parse(readFileSync(resolve(root, "fixtures/schema/g1-contract-corpus.v1.json"), "utf8")) as Corpus;
const ajv = new Ajv2020Module.default({ allErrors: true, strict: true, validateFormats: false });
const validators = new Map<string, ReturnType<typeof ajv.compile>>();

for (const schemaName of ["source-identity-key.v1.schema.json", "event-append-request.v1.schema.json"] as const) {
  const schema = JSON.parse(readFileSync(resolve(root, "schemas", schemaName), "utf8"));
  validators.set(schemaName, ajv.compile(schema));
}

function semanticValid(schemaName: string, value: unknown): boolean {
  if (schemaName === "source-identity-key.v1.schema.json") return true;
  if (schemaName !== "event-append-request.v1.schema.json" || typeof value !== "object" || value === null) return false;
  const request = value as { stream?: { tenant_id?: unknown }; caller?: { tenant_id?: unknown } };
  return typeof request.stream?.tenant_id === "string" && request.stream.tenant_id === request.caller?.tenant_id;
}

for (const testCase of corpus.cases) {
  const validator = validators.get(testCase.schema);
  if (!validator) throw new Error(`${testCase.name}: unknown schema ${testCase.schema}`);
  const actualSchema = validator(testCase.value) === true;
  if (actualSchema !== testCase.schema_valid) {
    throw new Error(`${testCase.name}: schema mismatch ${JSON.stringify(validator.errors)}`);
  }
  const actualSemantic = actualSchema && semanticValid(testCase.schema, testCase.value);
  if (actualSemantic !== testCase.semantic_valid) throw new Error(`${testCase.name}: semantic mismatch`);
}

console.log(`TypeScript schema parity PASS (${corpus.cases.length} cases)`);
