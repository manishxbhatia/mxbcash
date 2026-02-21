/**
 * Parse a decimal string to integer minor units.
 * e.g. "12.34" with fraction=100 → 1234
 */
export function parseCents(value: string, fraction: number): number {
  const decimals = Math.log10(fraction);
  const [intPart, decPart = ""] = value.replace(/,/g, "").split(".");
  const dec = decPart.padEnd(decimals, "0").slice(0, decimals);
  return parseInt(intPart, 10) * fraction + parseInt(dec || "0", 10) * Math.sign(parseInt(intPart, 10) || 1);
}

/**
 * Format integer minor units as a decimal string.
 * e.g. 1234 with fraction=100 → "12.34"
 */
export function formatCents(minor: number, fraction: number): string {
  if (fraction === 1) return minor.toString();
  const decimals = Math.log10(fraction);
  const abs = Math.abs(minor);
  const major = Math.floor(abs / fraction);
  const frac = (abs % fraction).toString().padStart(decimals, "0");
  return `${minor < 0 ? "-" : ""}${major}.${frac}`;
}

/**
 * Returns true if the sum of value_minor across splits is zero.
 */
export function isBalanced(splits: Array<{ value_minor: number }>): boolean {
  return splits.reduce((sum, s) => sum + s.value_minor, 0) === 0;
}

/**
 * Format for display with currency symbol.
 */
export function formatMoney(minor: number, fraction: number, mnemonic: string): string {
  return `${mnemonic} ${formatCents(minor, fraction)}`;
}
