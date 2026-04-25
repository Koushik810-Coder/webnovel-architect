---
name: project-diary
description: Use this skill when the user requests a project or development diary to summarize work done over a period of time. It ensures correct formatting, cadence handling (like skipping Sundays), and content depth.
---

# Project Diary Writing

This skill guides you through the creation of a chronological development or project diary. Use this workflow whenever the user wants a summary of progress organized by dates.

## Specifications

1. **Cadence and Dates**: 
   - Start from the date specified by the user.
   - The default progression is **every 2 days**.
   - **Skip Sundays**: If the next calculated cadence date lands on a Sunday, shift that entry to **Monday**. The subsequent cadence should calculate 2 days forward from Monday (i.e., Wednesday).
   - Alternatively, if the jump doesn't hit Sunday, just increment by the requested days.

2. **Entry Format**:
   - Ensure the diary is chronologically ordered with date headers.
   - Give each date **4 to 6 detailed bullet points**.
   - The length of each entry should amount to approximately **half a page** worth of detailed context (meaning the bullet points shouldn't be too short; expand on the technical mechanisms and impact of the work).

3. **Content Generation**:
   - Use the project's actual repository history (like `git log --since="..."`) and recent conversation history to draft accurate and realistic development events.
   - Focus on key areas of the project like testing, integrations, architecture, and optimizations.

4. **Deliverable**:
   - Always output the result as a Markdown artifact file named `project_diary.md` unless requested otherwise.
   - If the user requests a Word Document, invoke the `docx` or `word-document-processor` skill to convert the markdown into a formatted `.docx` file.
