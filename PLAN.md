## Solution plan

**Issue:** API docs don't include example curl commands  (https://github.com/codepath/pathreview-ai201-fa26-howard/issues/47)

### Understand
What is the root cause of this issue? What behavior is expected vs. actual?

The root cause of the issue is that the documentaiton files are missing curl commands, which makes it difficult for future potential collaborators to interact with the API for PathReview. The expected behavior is being able to see the curl commands and they actually work for when collaborators may want to test it out. The actual behavior is that the curl commands are completely nonexistent and there isn't a way for collaborators to effectively interact with the API endpoints.

### Map
Which files, functions, or modules are involved?
List the specific files you expect to touch.

The files that are involved were the docs folder,specifically the API.md file, and the README.md file. I expected to go through all of the documentation to ensure that the commands were not hidden somewhere and weren't able to be visible. 

### Plan
What are the steps to fix this issue?
Break it into 3–5 concrete sub-tasks.

To fix the issue, my plan is to: 
1) Ensure that the curl commands are completely nonexistent within the database
2) Look through the endpoints and start to build what commands are easy to understand and are tailored to the project 
3) Implement the commands in the documentation and make sure they are visible. 

### Inputs & outputs
What does your fix take as input? What should it produce or change?

The fix should produce curl commands that should be visible and easy to find within the documentation, and also be found when you run Linux commands. 


### Risks & unknowns
What could go wrong? What are you still unsure about?

Things that can go wrong are using unclear or "bad" curl commands that can be confusing for collaborators.  

### Edge cases
What inputs or states should your fix handle gracefully?

My fix should be visible and easy to understand for those who are looking at this database for the first time. 