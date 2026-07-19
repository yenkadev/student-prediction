# Early Risk Warning

Web application layer for the Early Academic Risk Warning System — lets staff
assess a single student's dropout risk via a natural-language chat, or
upload a CSV/Excel file to assess a batch of students. Built with
React + TypeScript + Vite.

## Getting started

```bash
npm install
npm run dev
```

## Project structure

- `src/api/` — `RiskWarningApiClient` interface plus a mock implementation
  (`mockClient.ts`) that stands in for the BE Service described in
  `POST /predict/chat` and `POST /predict/batch` (see
  `uploads/context_thiet_ke_application_layer.md` in the design handoff for
  the proposed contract). Swap `apiClient` in `src/api/client.ts` for a real
  HTTP client once the backend is available — no other file needs to change.
- `src/components/` — page components: `Dashboard` (overview), `NewAssessment`
  (chat + file upload), `BatchResults` (filterable/sortable table with CSV
  export).
- `src/types.ts` — shared domain types (`Student`, `RiskAssessment`, `RiskLevel`).

## Scripts

- `npm run dev` — start the dev server
- `npm run build` — typecheck and build for production
- `npm run preview` — preview the production build
- `npm run lint` — run Oxlint
