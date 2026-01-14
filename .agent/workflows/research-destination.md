---
description: Execute Phases 1-3 (Essentials, Knowledge, Logistics) for a destination.
---

# `research-destination` Workflow

This workflow automates the first three phases of travel planning.

## Steps

1. **Phase 1: Essentials**: Use `destination-expert` to fill:
    - `0_visa_legal.md`
    - `0_financial_services.md`
    - `0_communications.md`
2. **Phase 2: Knowledge Base**:
    - Use `market-analyst` for `1_business_market_analysis.md`.
    - Use `destination-expert` for `1_attractions.md` and `1_lodging_food.md`.
3. **Phase 3: Logistics**: Use `destination-expert` for:
    - `2_international_transportation.md`
    - `3_projects_providers.md`
    - `1_local_transportation.md`

4. **Update Status**: Change status to `**状态**: 编制中` for these files.
