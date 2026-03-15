import { zh } from "./zh";
import { en } from "./en";
import type { Dictionary } from "./zh";

export type Locale = "zh" | "en";

export const DEFAULT_LOCALE: Locale = "zh";

export const dictionaries: Record<Locale, Dictionary> = { zh, en };

export type { Dictionary };
export { zh, en };
