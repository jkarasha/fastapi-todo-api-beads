# Capability: Todos

## Overview
Complete CRUD operations for todo items with status tracking, priority levels, due dates, and category assignment.

## ADDED Requirements

### Requirement: Create Todo
Authenticated users MUST be able to create new todos.

#### Scenario: Create todo with required fields only
- **Given** an authenticated user
- **When** they submit `POST /todos` with:
  ```json
  {"title": "Buy groceries"}
  ```
- **Then** response is 201 with created todo including:
  - `id` (auto-generated)
  - `title`: "Buy groceries"
  - `status`: "pending" (default)
  - `priority`: null
  - `due_date`: null
  - `category_id`: null
  - `created_at`, `updated_at` (timestamps)

#### Scenario: Create todo with all fields
- **Given** an authenticated user with category id=1
- **When** they submit `POST /todos` with:
  ```json
  {
    "title": "Finish report",
    "description": "Q4 sales report for management",
    "priority": 1,
    "due_date": "2024-12-31",
    "category_id": 1
  }
  ```
- **Then** response is 201 with all fields populated

#### Scenario: Create todo with invalid priority
- **Given** an authenticated user
- **When** they submit with `"priority": 5`
- **Then** response is 422 with validation error (must be 0-4)

#### Scenario: Create todo with non-existent category
- **Given** an authenticated user
- **When** they submit with `"category_id": 999` (doesn't exist or belongs to another user)
- **Then** response is 404 with `{"detail": "Category not found", "code": "CATEGORY_NOT_FOUND"}`

---

### Requirement: List Todos
Authenticated users MUST be able to list their todos with filtering options.

#### Scenario: List all user's todos
- **Given** an authenticated user with 3 todos
- **When** they call `GET /todos`
- **Then** response is 200 with array of their 3 todos
- **And** todos from other users are not included

#### Scenario: Filter by status
- **Given** an authenticated user with todos in various statuses
- **When** they call `GET /todos?status=pending`
- **Then** response includes only todos with status "pending"

#### Scenario: Filter by category
- **Given** an authenticated user with todos in different categories
- **When** they call `GET /todos?category_id=1`
- **Then** response includes only todos in category 1

#### Scenario: Filter by due date range
- **Given** an authenticated user with todos having various due dates
- **When** they call `GET /todos?due_before=2024-12-31&due_after=2024-01-01`
- **Then** response includes only todos with due_date in that range

#### Scenario: Filter by priority
- **Given** an authenticated user with todos of various priorities
- **When** they call `GET /todos?priority=0`
- **Then** response includes only todos with priority 0 (highest)

#### Scenario: Empty result
- **Given** an authenticated user with no todos matching filter
- **When** they call `GET /todos?status=completed`
- **Then** response is 200 with empty array `[]`

---

### Requirement: Get Todo by ID
Authenticated users MUST be able to retrieve a specific todo.

#### Scenario: Get existing todo
- **Given** an authenticated user owns todo with id=1
- **When** they call `GET /todos/1`
- **Then** response is 200 with the todo details

#### Scenario: Get non-existent todo
- **Given** an authenticated user
- **When** they call `GET /todos/999` (doesn't exist)
- **Then** response is 404 with `{"detail": "Todo not found", "code": "TODO_NOT_FOUND"}`

#### Scenario: Get another user's todo
- **Given** user A owns todo id=1, user B is authenticated
- **When** user B calls `GET /todos/1`
- **Then** response is 404 with `{"detail": "Todo not found", "code": "TODO_NOT_FOUND"}`
- **And** response does not reveal the todo exists (security)

---

### Requirement: Update Todo
Authenticated users MUST be able to update their todos.

#### Scenario: Update todo title
- **Given** an authenticated user owns todo id=1
- **When** they call `PATCH /todos/1` with `{"title": "New title"}`
- **Then** response is 200 with updated todo
- **And** `updated_at` timestamp is refreshed
- **And** other fields remain unchanged

#### Scenario: Update todo status to completed
- **Given** an authenticated user owns todo id=1 with status "pending"
- **When** they call `PATCH /todos/1` with `{"status": "completed"}`
- **Then** response is 200 with status "completed"
- **And** `completed_at` is set to current timestamp

#### Scenario: Update todo status from completed to pending
- **Given** an authenticated user owns todo id=1 with status "completed"
- **When** they call `PATCH /todos/1` with `{"status": "pending"}`
- **Then** response is 200 with status "pending"
- **And** `completed_at` is set to null

#### Scenario: Update todo category
- **Given** an authenticated user owns todo id=1 and category id=2
- **When** they call `PATCH /todos/1` with `{"category_id": 2}`
- **Then** response is 200 with category_id=2

#### Scenario: Remove todo from category
- **Given** an authenticated user owns todo id=1 in category id=1
- **When** they call `PATCH /todos/1` with `{"category_id": null}`
- **Then** response is 200 with category_id=null

#### Scenario: Update non-existent todo
- **Given** an authenticated user
- **When** they call `PATCH /todos/999` with any updates
- **Then** response is 404 with `{"detail": "Todo not found", "code": "TODO_NOT_FOUND"}`

---

### Requirement: Delete Todo
Authenticated users MUST be able to delete their todos.

#### Scenario: Delete existing todo
- **Given** an authenticated user owns todo id=1
- **When** they call `DELETE /todos/1`
- **Then** response is 204 No Content
- **And** todo is permanently removed from database

#### Scenario: Delete non-existent todo
- **Given** an authenticated user
- **When** they call `DELETE /todos/999`
- **Then** response is 404 with `{"detail": "Todo not found", "code": "TODO_NOT_FOUND"}`

#### Scenario: Delete another user's todo
- **Given** user A owns todo id=1, user B is authenticated
- **When** user B calls `DELETE /todos/1`
- **Then** response is 404 with `{"detail": "Todo not found", "code": "TODO_NOT_FOUND"}`
- **And** todo is not deleted

## Dependencies
- `core-infrastructure` - database, exceptions
- `auth` - get_current_user dependency
- `categories` - category validation

## Related Capabilities
- `categories` - todos can be assigned to categories
