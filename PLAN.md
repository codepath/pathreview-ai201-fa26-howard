## Solution plan

**Issue:** API docs don't include example curl commands  (https://github.com/codepath/pathreview-ai201-fa26-howard/issues/47)

### Understand
What is the root cause of this issue? What behavior is expected vs. actual?

The root cause of this issue is that the project's documentation files are missing example curl commands. This makes it difficult for future contributors and collaborators to interact with and test the PathReview API. The expected behavior is for the documentation to include clear, working curl examples that demonstrate how to make requests to the API endpoints. The actual behavior is that these examples are currently missing, making it harder for developers to understand how to interact with the API.

### Map
Which files, functions, or modules are involved?
List the specific files you expect to touch.

The files that are involved were the docs/API.md and the README.md file. I expected to go through all of the documentation to ensure that the commands were not hidden somewhere and weren't able to be visible. These files were reviewed to understand what information was needed to start to plan a solution. 

### Plan
To fix the issue, my plan is to: 
1) Review API documentation and confirm where curl exampels are missing. 
2) Look through existing endpoints, identify HTTP methods and other parameters. 
3) Create clear commands in the documentation tailored to PathReview. 
4) Add examples to appropiate docs/API.md and update README.md if necessary. 
5) Test commands locally to ensure they work as expected. 

### Inputs & outputs
The inputs will include the existing API endpoints, their request requirements, and the project's local development environment. The expected output is updated documentation containing visible, understandable, and functional curl examples that allow contributors to interact with and test the API endpoints.


### Risks & unknowns
One potential risk is writing curl commands with incorrect URLs, headers, authentication details, or request bodies. This could cause confusion for contributors or result in commands that do not work. I will need to verify each example against the actual API implementation before adding it to the documentation.

### Edge cases
The examples should account for endpoints that require authentication, different HTTP methods, request bodies, and query parameters. They should also be easy to understand for contributors who may be interacting with the PathReview API for the first time.