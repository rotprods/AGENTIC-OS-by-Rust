export type JsonPrimitive = null | boolean | number | string;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };

const MAX_SAFE_INTEGER = Number.MAX_SAFE_INTEGER;

function assertWellFormedUnicode(value: string): void {
  for (let i = 0; i < value.length; i += 1) {
    const code = value.charCodeAt(i);
    if (code >= 0xd800 && code <= 0xdbff) {
      const next = value.charCodeAt(i + 1);
      if (!(next >= 0xdc00 && next <= 0xdfff)) throw new TypeError("unpaired high surrogate");
      i += 1;
    } else if (code >= 0xdc00 && code <= 0xdfff) {
      throw new TypeError("unpaired low surrogate");
    }
  }
}

function canonicalNumber(value: number): string {
  if (!Number.isFinite(value)) throw new TypeError("non-finite number");
  if (Number.isInteger(value) && Math.abs(value) > MAX_SAFE_INTEGER) throw new TypeError("unsafe integer");
  if (Object.is(value, -0)) return "0";
  return JSON.stringify(value);
}

export function canonicalize(value: JsonValue): string {
  if (value === null) return "null";
  if (typeof value === "string") {
    assertWellFormedUnicode(value);
    return JSON.stringify(value);
  }
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") return canonicalNumber(value);
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(",")}]`;

  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => {
    assertWellFormedUnicode(key);
    return `${JSON.stringify(key)}:${canonicalize(value[key]!)}`;
  }).join(",")}}`;
}
