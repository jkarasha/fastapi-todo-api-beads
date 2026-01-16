# Capability: Categories

## Overview
CRUD operations for user-defined categories to organize todos. Categories are scoped to individual users with unique names per user.

## ADDED Requirements

### Requirement: Create Category
Authenticated users MUST be able to create categories for organizing todos.

#### Scenario: Create category successfully
- **Given** an authenticated user
- **When** they submit `POST /categories` with:
  ```json
  {"name": "Work"}
  ```
- **Then** response is 201 with:
  ```json
  {"id": 1, "name": "Work", "created_at": "..."}
  ```

#### Scenario: Create category with duplicate name
- **Given** an authenticated user already has a category named "Work"
- **When** they submit `POST /categories` with `{"name": "Work"}`
- **Then** response is 409 with `{"detail": "Category already exists", "code": "CATEGORY_EXISTS"}`

#### Scenario: Create category with same name as another user
- **Given** user A has a category named "Work"
- **And** user B is authenticated
- **When** user B submits `POST /categories` with `{"name": "Work"}`
- **Then** response is 201 (categories are user-scoped)

#### Scenario: Create category with empty name
- **Given** an authenticated user
- **When** they submit `POST /categories` with `{"name": ""}`
- **Then** response is 422 with validation error

#### Scenario: Create category with name too long
- **Given** an authenticated user
- **When** they submit with name exceeding 100 characters
- **Then** response is 422 with validation error

---

### Requirement: List Categories
Authenticated users MUST be able to list their categories.

#### Scenario: List all user's categories
- **Given** an authenticated user with 3 categories
- **When** they call `GET /categories`
- **Then** response is 200 with array of their 3 categories
- **And** categories from other users are not included

#### Scenario: List categories when none exist
- **Given** an authenticated user with no categories
- **When** they call `GET /categories`
- **Then** response is 200 with empty array `[]`

---

### Requirement: Get Category by ID
Authenticated users MUST be able to retrieve a specific category.

#### Scenario: Get existing category
- **Given** an authenticated user owns category id=1
- **When** they call `GET /categories/1`
- **Then** response is 200 with category details

#### Scenario: Get non-existent category
- **Given** an authenticated user
- **When** they call `GET /categories/999`
- **Then** response is 404 with `{"detail": "Category not found", "code": "CATEGORY_NOT_FOUND"}`

#### Scenario: Get another user's category
- **Given** user A owns category id=1, user B is authenticated
- **When** user B calls `GET /categories/1`
- **Then** response is 404 with `{"detail": "Category not found", "code": "CATEGORY_NOT_FOUND"}`

---

### Requirement: Update Category
Authenticated users MUST be able to update their categories.

#### Scenario: Update category name
- **Given** an authenticated user owns category id=1 named "Work"
- **When** they call `PATCH /categories/1` with `{"name": "Office"}`
- **Then** response is 200 with updated name "Office"

#### Scenario: Update to duplicate name
- **Given** an authenticated user has categories "Work" (id=1) and "Personal" (id=2)
- **When** they call `PATCH /categories/1` with `{"name": "Personal"}`
- **Then** response is 409 with `{"detail": "Category already exists", "code": "CATEGORY_EXISTS"}`

#### Scenario: Update non-existent category
- **Given** an authenticated user
- **When** they call `PATCH /categories/999` with any update
- **Then** response is 404 with `{"detail": "Category not found", "code": "CATEGORY_NOT_FOUND"}`

---

### Requirement: Delete Category
Authenticated users MUST be able to delete their categories.

#### Scenario: Delete category with no todos
- **Given** an authenticated user owns category id=1 with no associated todos
- **When** they call `DELETE /categories/1`
- **Then** response is 204 No Content
- **And** category is permanently removed

#### Scenario: Delete category with associated todos
- **Given** an authenticated user owns category id=1 with 3 associated todos
- **When** they call `DELETE /categories/1`
- **Then** response is 204 No Content
- **And** category is deleted
- **And** associated todos have `category_id` set to null (not deleted)

#### Scenario: Delete non-existent category
- **Given** an authenticated user
- **When** they call `DELETE /categories/999`
- **Then** response is 404 with `{"detail": "Category not found", "code": "CATEGORY_NOT_FOUND"}`

---

### Requirement: Category Validation Dependency
A reusable dependency MUST validate category ownership for todo assignment.

#### Scenario: Valid category for todo assignment
- **Given** user A owns category id=1
- **When** user A creates/updates a todo with `category_id: 1`
- **Then** the category is valid and operation succeeds

#### Scenario: Invalid category for todo assignment
- **Given** user B owns category id=1, user A is authenticated
- **When** user A creates/updates a todo with `category_id: 1`
- **Then** response is 404 with `{"detail": "Category not found", "code": "CATEGORY_NOT_FOUND"}`

## Dependencies
- `core-infrastructure` - database, exceptions
- `auth` - get_current_user dependency

## Related Capabilities
- `todos` - uses category validation when assigning todos
