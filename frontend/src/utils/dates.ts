/**
 * Format a date string (YYYY-MM-DD) for display.
 */
export function formatDate(date: string): string {
  if (!date) return "";
  const [year, month, day] = date.split("-");
  return `${month}/${day}/${year}`;
}

/**
 * Get today's date as YYYY-MM-DD.
 */
export function today(): string {
  return new Date().toISOString().slice(0, 10);
}

/**
 * Get the first day of a month N months ago.
 */
export function monthsAgo(n: number): string {
  const d = new Date();
  d.setMonth(d.getMonth() - n, 1);
  return d.toISOString().slice(0, 10);
}

/**
 * Get the last day of the current month.
 */
export function endOfMonth(): string {
  const d = new Date();
  d.setMonth(d.getMonth() + 1, 0);
  return d.toISOString().slice(0, 10);
}
