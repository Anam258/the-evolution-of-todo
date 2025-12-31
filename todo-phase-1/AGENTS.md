# AGENTS.md

## Purpose
This project uses Spec-Driven Development (SDD).
No agent is allowed to write code until the specification is complete and approved.

Workflow:
Specify → Plan → Tasks → Implement

## Mandatory Rules
1. Never write code without an approved Task ID.
2. Never change architecture without updating speckit.plan.
3. Never invent requirements — update speckit.specify instead.
4. Every implementation must reference Task IDs.
5. If something is unclear, stop and request clarification.

## Source of Truth Order
1. speckit.constitution
2. speckit.specify
3. speckit.plan
4. speckit.tasks

## Agent Behavior
Agents must strictly follow specs.
No freestyle coding.
