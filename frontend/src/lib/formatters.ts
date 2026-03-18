export function resolveLocale(language: string): string {
  return language.toLowerCase().startsWith("tr") ? "tr-TR" : "en-US";
}

export function createNumberFormatter(language: string, options?: Intl.NumberFormatOptions): Intl.NumberFormat {
  return new Intl.NumberFormat(resolveLocale(language), options);
}

export function createCurrencyFormatter(
  language: string,
  currency = "EUR",
  options?: Intl.NumberFormatOptions
): Intl.NumberFormat {
  return new Intl.NumberFormat(resolveLocale(language), {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
    ...options,
  });
}
