import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { assertFresh, reduceEvents, SurvivalContractError, type FreshnessSeal } from "./survival.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../..");
const fixture = JSON.parse(fs.readFileSync(path.join(root, "fixtures/golden/survival-behavior-v2.json"), "utf8")) as {
  seed: Record<string, unknown>;
  cases: Array<Record<string, unknown>>;
};

let passed = 0;
for (const vector of fixture.cases) {
  const expect = vector["expect"] as Record<string, unknown>;
  const expectedStatus = expect["status"];
  try {
    let result: Record<string, unknown> = {};
    if (vector["operation"] === "reduce_events") {
      result = reduceEvents(fixture.seed, vector["events"] as Parameters<typeof reduceEvents>[1]) as unknown as Record<string, unknown>;
    } else if (vector["operation"] === "assert_fresh") {
      assertFresh(vector["local"] as FreshnessSeal, vector["live"] as FreshnessSeal);
    } else {
      throw new Error(`unknown fixture operation ${String(vector["operation"])}`);
    }
    if (expectedStatus !== "PASS") throw new Error(`${String(vector["name"])} expected rejection but passed`);
    for (const [key, value] of Object.entries(expect)) {
      if (key === "status") continue;
      if (JSON.stringify(result[key]) !== JSON.stringify(value)) throw new Error(`${String(vector["name"])} mismatch for ${key}`);
    }
    passed += 1;
  } catch (error) {
    if (expectedStatus !== "REJECT") throw error;
    if (!(error instanceof SurvivalContractError)) throw error;
    if (error.code !== expect["error_code"]) throw new Error(`${String(vector["name"])} expected ${String(expect["error_code"])} got ${error.code}`);
    passed += 1;
  }
}

console.log(`survival behavioral parity: ${passed}/${fixture.cases.length} PASS`);
