# Capability: Authentication

## Overview
User registration, login, and JWT-based authentication for securing API endpoints.

## ADDED Requirements

### Requirement: User Registration
Users MUST be able to create an account with email and password.

#### Scenario: Successful registration
- **Given** a user submits `POST /auth/register` with:
  ```json
  {"email": "user@example.com", "password": "securepass123"}
  ```
- **When** the email is not already registered
- **Then** response is 201 with user data (id, email, created_at)
- **And** password is stored as bcrypt hash (never plaintext)
- **And** response does not include password or hash

#### Scenario: Registration with existing email
- **Given** email "user@example.com" is already registered
- **When** a user submits `POST /auth/register` with the same email
- **Then** response is 409 with `{"detail": "Email already registered", "code": "EMAIL_EXISTS"}`

#### Scenario: Registration with invalid email
- **Given** a user submits registration with `email: "not-an-email"`
- **When** validation runs
- **Then** response is 422 with validation error details

#### Scenario: Registration with weak password
- **Given** a user submits registration with `password: "123"`
- **When** validation runs
- **Then** response is 422 with error indicating minimum 8 characters required

---

### Requirement: User Login
Registered users MUST be able to obtain a JWT access token.

#### Scenario: Successful login
- **Given** a registered user with email "user@example.com"
- **When** they submit `POST /auth/login` with correct credentials
- **Then** response is 200 with:
  ```json
  {"access_token": "eyJ...", "token_type": "bearer"}
  ```
- **And** token expires in 24 hours (configurable)
- **And** token payload contains `sub` (user id) and `exp` (expiration)

#### Scenario: Login with wrong password
- **Given** a registered user
- **When** they submit login with incorrect password
- **Then** response is 401 with `{"detail": "Invalid credentials", "code": "INVALID_CREDENTIALS"}`

#### Scenario: Login with unregistered email
- **Given** email "unknown@example.com" is not registered
- **When** login is attempted with that email
- **Then** response is 401 with `{"detail": "Invalid credentials", "code": "INVALID_CREDENTIALS"}`
- **And** response does not reveal whether email exists (security)

---

### Requirement: Current User Retrieval
Authenticated users MUST be able to retrieve their profile.

#### Scenario: Get current user with valid token
- **Given** a valid JWT token in `Authorization: Bearer <token>` header
- **When** `GET /auth/me` is called
- **Then** response is 200 with user data (id, email, created_at)

#### Scenario: Get current user without token
- **Given** no `Authorization` header is present
- **When** `GET /auth/me` is called
- **Then** response is 401 with `{"detail": "Not authenticated", "code": "NOT_AUTHENTICATED"}`

#### Scenario: Get current user with expired token
- **Given** an expired JWT token
- **When** `GET /auth/me` is called
- **Then** response is 401 with `{"detail": "Token expired", "code": "TOKEN_EXPIRED"}`

#### Scenario: Get current user with invalid token
- **Given** a malformed or tampered JWT token
- **When** `GET /auth/me` is called
- **Then** response is 401 with `{"detail": "Invalid token", "code": "INVALID_TOKEN"}`

---

### Requirement: Authentication Dependency
Protected endpoints MUST use a reusable dependency to validate authentication.

#### Scenario: Dependency injection for protected routes
- **Given** an endpoint uses `Depends(get_current_user)`
- **When** a valid token is provided
- **Then** the dependency returns the `User` object
- **And** the user is available in the endpoint function

#### Scenario: Dependency with invalid authentication
- **Given** an endpoint uses `Depends(get_current_user)`
- **When** token is missing, expired, or invalid
- **Then** appropriate 401 error is raised before endpoint executes

## Dependencies
- `core-infrastructure` - database, config, exceptions

## Related Capabilities
- `todos` - uses `get_current_user` for authorization
- `categories` - uses `get_current_user` for authorization
