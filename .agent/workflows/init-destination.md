---
description: Initialize a new travel destination with the standard 8-step file structure.
---

# `init-destination` Workflow

Use this workflow to quickly set up the directory and necessary files for a new country/destination.

## Steps

1. **Create Directory**: `mkdir -p destinations/[CountryName]`
2. **Generate Files**: Create the following empty/skeleton files in the new directory:
    - `README.md`
    - `0_visa_legal.md`
    - `0_financial_services.md`
    - `0_communications.md`
    - `1_business_market_analysis.md`
    - `1_attractions.md`
    - `1_lodging_food.md`
    - `1_local_transportation.md`
    - `2_international_transportation.md`
    - `3_projects_providers.md`
    - `4_notes.md`
    - `5_itinerary.md`
    - `6_budget.md`

3. **Add Status Line**: Ensure every file starts with `**状态**: 草稿`.
4. **Confirm Structure**: Verify all 13 files are present.
