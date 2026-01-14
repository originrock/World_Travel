---
description: Execute Phases 4-6 (Itinerary, Budget, Summary) to complete a destination plan.
---

# `finalize-plan` Workflow

This workflow completes the planning process for a destination.

## Steps

1. **Phase 4: Synthesis**: Use `destination-expert` to create `5_itinerary.md` based on previous research.
2. **Phase 5: Budgeting**: Use `budget-wizard` to generate `6_budget.md` (Survival, Recommended, Luxury tiers).
3. **Phase 6: Delivery**:
    - Update `README.md` in the destination folder.
    - Update the global `README.md` if necessary.
4. **Mark Completed**: Change all file statuses to `**状态**: 已完成`.
