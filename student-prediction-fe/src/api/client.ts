import { HttpRiskWarningApiClient } from "./httpClient";
import type { RiskWarningApiClient } from "./types";

export const apiClient: RiskWarningApiClient = new HttpRiskWarningApiClient();

export type { RiskWarningApiClient } from "./types";
