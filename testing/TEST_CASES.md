Mini-LMS – Test Cases
1. Purpose

This document contains test cases for checking the Mini-LMS application.

The testing focuses on application functionality, database requirements, API availability, and user experience.

2. Test Cases
TC-01: Application Availability
Objective: Check whether the Mini-LMS application opens.
Steps:
Open the application in a browser.
Check whether the main page loads.
Expected Result: The main page opens successfully.
Status: NOT TESTED
TC-02: User Interface
Objective: Check whether the interface displays correctly.
Steps:
Open the application.
Inspect the visible elements.
Check buttons, menus, and navigation.
Expected Result: Interface elements are displayed correctly.
Status: NOT TESTED
TC-03: Backend Availability
Objective: Check whether the backend API is accessible.
Steps:
Open the FastAPI documentation page at /docs.
Check whether the documentation loads.
Expected Result: API documentation is accessible.
Status: NOT TESTED
TC-04: Database Connection
Objective: Check whether the application connects to PostgreSQL.
Steps:
Start the application using the project instructions.
Observe whether database connection errors appear.
Expected Result: No database connection errors occur.
Status: NOT TESTED
TC-05: Database Structure
Objective: Check whether required database tables exist.
Steps:
Inspect the PostgreSQL database.
Compare the tables with project documentation.
Expected Result: Required tables are present.
Status: NOT TESTED
TC-06: Database Migrations
Objective: Check database migrations.
Steps:
Inspect the Alembic migration status.
Check whether migrations have been applied successfully.
Expected Result: Database migrations are applied without errors.
Status: NOT TESTED
TC-07: API Functionality
Objective: Check whether API endpoints respond correctly.
Steps:
Open /docs.
Inspect available endpoints.
Test appropriate endpoints.
Expected Result: API endpoints return expected responses.
Status: NOT TESTED
TC-08: Database Requirements (DBT-01 – DBT-10)
Objective: Verify database requirements from project documentation.
Steps:
Review DBT-01 through DBT-10.
Perform the required database checks.
Record the results.
Expected Result: Database requirements behave as documented.
Status: NOT TESTED
3. Test Status Legend
PASS: Test completed successfully.
FAIL: Test completed but the expected result was not achieved.
NOT TESTED: Test has not been performed yet.
4. Notes

All test results will be recorded after executing the test cases.

Any discovered defects will be documented in TEST_REPORT.md.
