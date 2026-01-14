# Gemini Project: World Travel Planner

## Directory Overview

This directory is a personal travel planner for organizing a round-the-world trip. It uses Markdown files and an integrated AI Agent framework to document and track all aspects of the journey.

* **`.agent/`**: 存放 AI 智能规划助手的核心逻辑。
  * `skills/`: 专业领域的 AI 技能（如签证、美食、交通专家等）。
  * `workflows/`: 自动化执行流（如 `/auto-plan`, `/init-destination`）。
* **`global_plan/`**: 存放整个旅行的宏观计划和通用准备清单。
* **`destinations/`**: 存放每个具体目的地的详细旅行计划。
* **`README.md`**: 项目主入口，包含导航、进度总览及 AI 助手使用说明。
* **`GEMINI.md`**: 本文档，详述项目架构与规划流程规范。

## Planning Process & Status Management

### Status Tracking

每个目的地目录下的文件必须以状态行开头，以跟踪其进度：

* `**状态**: 草稿` (Draft): 文件已创建，但尚未开始详细调研。
* `**状态**: 编制中` (In Progress): AI 专家正在进行深度调研或编写。
* `**状态**: 已完成` (Completed): 该阶段规划已完成，并经过交叉校验。

### Planning Workflow (SOP)

目的地的规划遵循 9 步标准作业程序 (SOP)，由专一领域专家协作完成：

1. **Step 1: Essentials (基础调研)**: `0_visa_legal.md`, `0_financial_services.md`, `0_communications.md`。
2. **Step 2: Business & Market Study (商业调研)**: `1_business_inspection.md`。研究目的地经济、消费习惯与行业动态。
3. **Step 3: Knowledge Base (知识库构建)**: `1_attractions.md`, `1_lodging_food.md`。收集景点、特色体验及美食信息。
4. **Step 4: Logistics & Transport (物流与交通)**: `2_international_transportation.md`, `1_local_transportation.md`。
5. **Step 5: Provider Verification (供应商研判)**: `3_projects_providers.md`。确认预订官网、联系方式及信用度。
6. **Step 6: Synthesis & Synthesis (综合策划)**: `4_notes.md` (文化/安全策略)。
7. **Step 7: Itinerary Formulation (行程编排)**: `5_itinerary.md`。基于地理聚类逻辑设计每日日程。
8. **Step 8: Budgeting (财务预算)**: `6_budget.md`。基于供应商真实价格进行三波段核算。
9. **Step 9: Delivery (交付与归档)**: 更新 `README.md` 并导出 PDF。

## AI 智能规划框架

项目通过 `.agent/skills` 下的专家矩阵实现从调研到交付的全流程自动化：

* **Travel Orchestrator (中控台)**: 负责全局调度逻辑。
* **Specialized Agents**: 包含 `visa-consultant`, `logistics-expert`, `foodie-expert`, `attractions-expert`, `experience-expert`, `business-inspection`, `itinerary-architect`, `budget-wizard` 等。
* **Command Flow**: 使用 `/auto-plan [地点] [天数]` 触发完整规划闭环。

## Usage

本项目不仅是一个文档库，更是一个基于 Agent Skills 的自动化系统。用户通过调用特定工作流（Workflows），驱动多名 AI 专家通过实时搜索和地图校验，生成具有实操意义的专业旅行计划。
