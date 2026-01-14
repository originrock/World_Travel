---
description: Fully automate the 9-step planning process for a new country in one request.
---

# `/auto-plan` Workflow

This workflow triggers the `destination-expert` Master Orchestrator to complete a full destination plan.

## Usage

`/auto-plan [Country] [Duration] [Optional: Priority/Budget Tier]`

## Steps

1. **Initialize**: Triggers `init-destination` to create the standard folder `destinations/[Country]`.
2. **Execute Research**:
    - Runs `visa-consultant`, `business-inspection` (Market), and `logistics-expert`.
    - Populates `0_visa_legal.md`, `1_business_market_analysis.md`, `2_international_transportation.md`, etc.
3. **Build Knowledge & Providers**:
    - Researches `1_attractions.md` using `attractions-expert` and `experience-expert`.
    - Researches `1_lodging_food.md` using `foodie-expert`.
    - Runs `business-inspection` to synthesize all findings into `3_projects_providers.md`.
4. **Synthesize Plan**:
    - Runs `itinerary-architect` to build `5_itinerary.md`.
    - Runs `cultural-safety-advisor` to build `4_notes.md`.
5. **Finalize Budget**:
    - Runs `budget-wizard` to build `6_budget.md`.
6. **Deliver & Export**:
    - Generates the country-level `README.md`.
    - Triggers `markdown-to-pdf` to export the full planning package as a PDF.
    - Marks all files as `**状态**: 已完成`.

## Post-Condition

A complete, 13-file planning package ready for user review.
