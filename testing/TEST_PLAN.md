
# Mini-LMS — Test Plan

## 1. Introduction

This document describes the testing activities
for the Mini-LMS project.

The purpose of testing is to identify errors,
verify database integrity, and ensure that
the application works according to requirements.

## 2. Testing Objectives

- Verify database structure.
- Check data integrity.
- Verify database constraints.
- Check relationships between tables.
- Identify database errors.
- Evaluate query performance.

## 3. Testing Scope

The testing activities include:

- Database schema validation.
- Database constraints validation.
- Duplicate data validation.
- Foreign key validation.
- Data deletion behavior.
- SQL query validation.
- Database performance checks.

## 4. Test Cases

| ID | Test description | Expected result |
|---|---|---|
| DBT-01 | Check database tables | All required tables exist |
| DBT-02 | Check database schema | Schema matches project models |
| DBT-03 | Check seed data execution | Repeated execution does not create unwanted duplicates |
| DBT-04 | Check duplicate user email | Duplicate email is rejected |
| DBT-05 | Check user role constraint | Invalid roles are rejected |
| DBT-07 | Check user deletion | Related profile is deleted according to database rules |
| DBT-09 | Check SQL queries | Queries return correct results |
| DBT-10 | Check query performance | Queries execute within acceptable time |

## 5. Testing Methodology

Testing will include:

- Manual database testing.
- SQL query validation.
- Constraint testing.
- Data integrity testing.
- Performance testing.

## 6. Test Environment

Database: PostgreSQL

Backend: Python / FastAPI

ORM: SQLAlchemy

Migration tool: Alembic

## 7. Test Status

Tests are documented and awaiting execution.

No test is considered passed until its result
has been verified.

## 8. Conclusion

This test plan defines the initial database
testing activities for the Mini-LMS project.
