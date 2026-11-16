Mini-LMS — Test Cases

1. Purpose

This document contains 20 test cases for checking the Mini-LMS application.

Testing covers frontend, backend API, authentication, course functionality, and database connectivity.

2. Test Cases

ID	Test Case	Expected Result	Actual Result	Status
TC-01	Open application	Main page loads	Main page opened	PASS
TC-02	Open course catalog	Courses are displayed	Courses displayed	PASS
TC-03	Search for a course	Matching course appears	Calculus 1 found	PASS
TC-04	Open course without login	Access is restricted	Access restricted	PASS
TC-05	Open login page	Login form appears	Form displayed	PASS
TC-06	Open registration page	Registration form appears	Form displayed	PASS
TC-07	Submit empty registration form	Required fields validation appears	Validation appeared	PASS
TC-08	Register a new user	Account is created	Account created	PASS
TC-09	Open student dashboard	Dashboard is displayed	Dashboard opened	PASS
TC-10	Open user profile	User information is displayed	Profile displayed	PASS
TC-11	Save profile information	Changes are saved	Changes saved	PASS
TC-12	Open grades page	Grades page is displayed	No grades displayed	PASS
TC-13	Log out	User is logged out	Login required again	PASS
TC-14	Open API documentation	Swagger documentation loads	Documentation opened	PASS
TC-15	Check GET /health/live	HTTP 200 response	HTTP 200, status OK	PASS
TC-16	Check GET /health/ready	Database is reachable	HTTP 200, database reachable	PASS
TC-17	Check GET /api/demo/courses	Course list is returned	HTTP 200, courses returned	PASS
TC-18	Check GET /api/me without login	HTTP 401 response	HTTP 401 Unauthorized	PASS
TC-19	Log in again	User can log in successfully	Login successful	PASS
TC-20	Enroll in a course	User can access course lessons	Course opened, lessons available	PASS

3. Test Status

* PASS — Test completed successfully.
* FAIL — Test completed but expected result was not achieved.
* NOT TESTED — Test has not been performed.

4. Automated Test Results

Automated backend tests were executed using pytest.

Command: docker compose exec backend pytest -q

Results:

* 5 passed
* 76 skipped
* 1 warning

Skipped tests were not counted as passed.

5. Conclusion

The 20 manual test cases were completed. The main application functions, user registration, login, profile, course catalog, API health checks, and course enrollment were checked.

Additional automated backend tests reported 5 passed and 76 skipped. Further testing is required for the skipped tests.
