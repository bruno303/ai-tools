---
name: architectural-guidelines
description: Enforces Clean Architecture and project-specific design patterns.
---

## 1. Project Philosophy
- **Separation of Concerns**: Keep Business Logic (Domain/Usecase) strictly separated from Infrastructure (DB, API, External Services).
- **Go Pattern**: Use the "Internal" directory for private logic. Prefer interfaces for dependencies to allow mocking.
- **Kotlin Pattern**: Use Sealed Classes for state management and Result types for error handling.

## 2. Structural Rules
- **Infrastructure**: All external API calls must live in `internal/infrastructure/` (Go).
- **Domain**: Business rules must not import any framework-specific libraries (no `gin`).
- **Dependency Injection**: 
  - Go: Use constructor injection (e.g., `NewService(repo Repository)`).

## 3. Data Transfer
- Never expose Database Entities/Models directly to the API. 
- Always map to a DTO/Response struct before returning to the customer.

## 4. Onboarding Protocol (Agent Task)
- Before writing any code, the agent MUST:
  1. Scan the existing directory structure.
  2. Identify the "Source of Truth" for existing patterns (e.g., look at an existing Service).
  3. Propose the file location to the user and explain how it fits the architecture.
