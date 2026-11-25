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
What does your fix take as input? What should it produce or change?

The fix should produce curl commands that should be visible and easy to find within the documentation, and also be found when you run Linux commands. 


### Risks & unknowns
What could go wrong? What are you still unsure about?

Things that can go wrong are using unclear or "bad" curl commands that can be confusing for collaborators.  

### Edge cases
What inputs or states should your fix handle gracefully?

My fix should be visible and easy to understand for those who are looking at this database for the first time. 