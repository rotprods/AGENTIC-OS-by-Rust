import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

type Case = { name: string; schema: string; schema_valid: boolean; value: unknown };
type Corpus = { cases: Case[] };
type Validator = ((value: unknown) => boolean) & { errors?: unknown };
type AjvInstance = { compile(schema: unknown): Validator };
type AjvConstructor = new (options?: Record<string, unknown>) => AjvInstance;

const require = createRequire(import.meta.url);
const loaded = require("ajv/dist/2020") as { default?: unknown } | AjvConstructor;
const Ajv2020 = (("default" in loaded && loaded.default) || loaded) as AjvConstructor;
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../../..");
const corpus = JSON.parse(readFileSync(resolve(root, "fixtures/schema/survival-v2-corpus.json"), "utf8")) as Corpus;
const ajv = new Ajv2020({ allErrors: true, strict: true, validateFormats: true });
const validators = new Map<string, Validator>();

for (const schemaName of ["survival-project-state.v2.schema.json", "survival-checkpoint.v2.schema.json"] as const) {
  const schema = JSON.parse(readFileSync(resolve(root, "schemas", schemaName), "utf8")) as unknown;
  validators.set(schemaName, ajv.compile(schema));
}

for (const testCase of corpus.cases) {
  const validator = validators.get(testCase.schema);
  if (!validator) throw new Error(`${testCase.name}: unknown Survival schema ${testCase.schema}`);
  const actual = validator(testCase.value) === true;
  if (actual !== testCase.schema_valid) {
    throw new Error(`${testCase.name}: schema mismatch ${JSON.stringify(validator.errors)}`);
  }
}

console.log(`TypeScript Survival V2 schema parity PASS (${corpus.cases.length} cases)`);
