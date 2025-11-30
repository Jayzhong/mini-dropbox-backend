Every time you run as the Coding Agent, you MUST follow this workflow:

1. **Read context:**
    
    - `PRODUCT_CONTEXT.md`
        
    - `ARCHITECTURE_RULES.md`
        
    - `TASKS.md`
        
    - `PROGRESS_LOG.md`
        
    - The current repository tree (especially files related to your chosen task).
        
2. **Pick exactly ONE task** from `TASKS.md` with status TODO and mark it as your focus for this session.
    
    - Prefer tasks under the “Walking Skeleton & Infrastructure” section until the baseline app is running.
        
3. **Plan briefly**:
    
    - Write a short implementation plan in your response.
        
    - List expected files to be created/modified.
        
4. **Implement**:
    
    - Modify the codebase to complete the chosen task end-to-end.
        
    - Add or update tests if applicable.
        
5. **Verify**:
    
    - Run tests or at least compile/build the project.
        
    - If something is failing and cannot be fixed within this session, clearly document it.
        
6. **Update artifacts**:
    
    - Update `TASKS.md`: change the status of the task (to Done or Blocked).
        
    - Append a new entry to `PROGRESS_LOG.md` summarizing:
        
        - The task you worked on.
            
        - Changes you made.
            
        - Test commands you ran and their results.
            
        - Any follow-up work needed.
            
7. **Leave the repo clean**:
    
    - No half-implemented features without notes.
        
    - Code should build; if not, explicitly mark the task as Blocked and explain why.