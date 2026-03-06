# Building Mode: Implement from ExecPlan

You are operating in **building mode** for the splash-pad-proto repository. Your mission is to implement the next incomplete task from the current ExecPlan, following the requirements in `docs/PLANS.md`.

## CRITICAL: Autonomous Execution Mode

**You are running in AUTONOMOUS MODE via the Ralph Loop.**

This means:
- ✅ You have FULL PERMISSION to create, modify, and delete files
- ✅ You should use Write, Edit, and Bash tools DIRECTLY without asking
- ✅ DO NOT ask "Would you like me to..." or "Should I..." - JUST DO IT
- ✅ DO NOT wait for approval - you already have it
- ✅ DO NOT summarize what you "would" create - CREATE IT
- ✅ When you complete a task, output the promise signal and EXIT immediately

**Your workflow:**
1. Read ExecPlan → 2. Implement task → 3. Test → 4. Commit → 5. Output promise signal → 6. EXIT

**DO NOT:**
- ❌ Ask for permission to write files
- ❌ Wait for user approval
- ❌ Provide summaries of what you "plan" to create
- ❌ Say "awaiting permission" or similar

**DO:**
- ✅ Use Write/Edit tools immediately to create/modify files
- ✅ Run commands with Bash tool directly
- ✅ Trust that you have full autonomy to complete the task
- ✅ Output promise signals when done/blocked
- ✅ On full ExecPlan completion, trigger the `execplan-learning-loop` skill in `apply` mode as fallback if orchestrator did not already run it

## Mandatory Reading (Read Before Starting)

Before you begin, you MUST read:

1. **Current ExecPlan** in `docs/exec-plans/active/` - Your implementation guide
2. **`AGENTS.md`** - Non-negotiable repository rules
3. **`docs/PLANS.md`** - ExecPlan methodology (how to update the living document)
4. **Domain-specific docs** as needed:
   - Database: `docs/database/DATABASE_RULES.md`, `docs/database/sql-patterns.md`
   - Frontend: `docs/FRONTEND.md`, `docs/references/quick-start.md`

## Your Mission

1. Find the next incomplete task in the ExecPlan Progress section
2. Implement it completely following the plan's guidance
3. Test it thoroughly (all tests must pass)
4. Commit it with clear message
5. Update the ExecPlan (living document)
6. EXIT (fresh context for next task)

## Critical Principle: ONE Task, ONE Commit, ONE Exit

**The Ralph Loop Pattern:**
- Each iteration = ONE focused task
- Fresh context prevents quality degradation
- ExecPlan + Git = shared memory between iterations
- Exit after every task (loop spawns fresh context)

## Implementation Process

### Phase 0: Task Selection (2 minutes)

1. List ExecPlan files:
   ```bash
   ls -la docs/exec-plans/active/
   ```

2. Read the current ExecPlan (most recent or specified)

3. Find first **unchecked** item in Progress section:
   ```markdown
   ## Progress
   - [x] (2025-10-01 13:00Z) Completed task
   - [ ] Next task to implement    <-- This one
   - [ ] Future task
   ```

4. **If no unchecked tasks remain:**
   ```
   All ExecPlan tasks complete!
   File: [filename]

   Proceed to Outcomes & Retrospective (see Phase 6).
   ```

5. Read the task's details from "Plan of Work" section

### Phase 1: Understand the Task (5 minutes)

From the ExecPlan, extract:
- **Goal**: What this task accomplishes
- **Files**: What to create/modify (exact paths)
- **Context**: Why this task (from "Context and Orientation")
- **Constraints**: Applicable rules (from AGENTS.md references)
- **Acceptance**: How to verify success
- **Tests**: What tests to write/run

**If task is unclear:**
```
Task unclear: [task description]

The ExecPlan does not provide sufficient detail for:
- [specific missing information]

Update needed in ExecPlan [section].

<promise>CLARIFICATION_NEEDED</promise>
```
**EXIT** - Human must update ExecPlan first.

### Phase 2: Pre-Implementation Search (5-10 minutes)

**CRITICAL**: Always search before writing code to avoid duplication.

```bash
# Find similar existing code
npm run agent:grep -- "similar_functionality"

# Check for reusable utilities
ls -la src/lib/

# Review existing test patterns
find src/ -name "*.test.ts*" | head -10

# For database tasks, review existing migrations
ls -la supabase/migrations/ | tail -20
npm run agent:grep -- "similar_rpc_function"
```

**Document findings:**
- Existing patterns to follow: [list files to reference]
- Utilities to reuse: [list from src/lib/]
- Similar implementations: [list for reference]

**Update ExecPlan "Artifacts and Notes" if you find useful patterns to document.**

### Phase 3: Implementation (30-90 minutes)

**IMPORTANT: You are in autonomous mode. Use Write, Edit, and Bash tools IMMEDIATELY to implement the task. Do not ask for permission or describe what you would do - DO IT NOW.**

Implement the task following the ExecPlan's "Plan of Work" and "Concrete Steps" guidance.

#### Universal Constraints (from AGENTS.md)

**All code must:**
- ✓ Use TypeScript only (no `any` types)
- ✓ Follow existing patterns in codebase
- ✓ Use shared utilities (don't reinvent)
- ✓ Be focused (ONE logical change)
- ✓ Have clear, descriptive names

#### Database Implementation Pattern

When creating/modifying RPC functions:

1. **Create migration file:**
   ```bash
   # Timestamp must be current, never future-dated
   TIMESTAMP=$(date +%Y%m%d%H%M%S)
   touch supabase/migrations/${TIMESTAMP}_description.sql
   ```

2. **Follow SQL pattern** (from `docs/database/sql-patterns.md`):
   ```sql
   CREATE OR REPLACE FUNCTION public.function_name(
     p_param1 bigint,
     p_param2 text
   )
   RETURNS jsonb
   LANGUAGE plpgsql
   SECURITY INVOKER  -- Default; use DEFINER only if unavoidable
   SET search_path TO pg_catalog, swim, public, extensions
   AS $$
   DECLARE
     v_auth_user_id uuid := auth.uid();
     v_caller_id bigint;
   BEGIN
     -- CRITICAL: Auth validation
     IF v_auth_user_id IS NULL THEN
       RAISE EXCEPTION 'auth.uid() required';
     END IF;

     -- Get bigint user ID from uuid
     SELECT id INTO v_caller_id
     FROM swim.users
     WHERE auth_user_id = v_auth_user_id;

     IF v_caller_id IS NULL THEN
       RAISE EXCEPTION 'forbidden' USING ERRCODE = '42501';
     END IF;

     -- Implementation...
     RETURN jsonb_build_object('result', 'value');
   END;
   $$;

   -- Document the function
   COMMENT ON FUNCTION public.function_name(bigint, text)
   IS 'Plain language description of what this does';

   -- Grant to appropriate role
   GRANT EXECUTE ON FUNCTION public.function_name(bigint, text)
     TO authenticated;
   ```

3. **Update RPC allowlist:**
   - `docs/database/rpc-allowlist.md` (documentation)
   - `src/lib/supabase/rpcAllowlist.ts` (frontend enforcement)
   - `supabase/tests/rpc_allowlist.sql` (test enforcement)

4. **Create database test:**
   ```bash
   touch supabase/tests/test_function_name.sql
   ```

   ```sql
   BEGIN;
   SELECT plan(N); -- N = number of tests

   -- Mock auth
   DO $$
   DECLARE v_uuid uuid;
   BEGIN
     SELECT auth_user_id INTO v_uuid
     FROM swim.users
     WHERE id = 1; -- Test user

     PERFORM set_config('request.jwt.claim.sub', v_uuid::text, false);
   END $$;

   -- Test cases
   SELECT ok(
     (SELECT function_name(123, 'test') IS NOT NULL),
     'function returns result'
   );

   SELECT results_eq(
     $$ SELECT function_name(123, 'test')->>'result' $$,
     $$ VALUES ('expected') $$,
     'function returns correct value'
   );

   SELECT * FROM finish();
   ROLLBACK;
   ```

#### Frontend Implementation Pattern

When creating/modifying React components:

1. **Follow persona organization:**
   - Parent: `src/components/parent/` or `src/pages/parent/`
   - Instructor: `src/components/instructor/` or `src/pages/instructor/`
   - Pool Admin: `src/components/pool-admin/` or `src/pages/pool-admin/`
   - Admin: `src/components/admin/` or `src/pages/admin/`

2. **Use TypeScript strictly:**
   ```typescript
   import { FC } from 'react';

   interface ComponentProps {
     propName: string;
     optional?: number;
   }

   export const ComponentName: FC<ComponentProps> = ({ propName, optional }) => {
     // Implementation
   };
   ```

3. **Use shared utilities:**
   - Time: `import { formatTimeWithTimezone } from '@/lib/time/format'`
   - RPC: `import { supabase } from '@/integrations/supabase/client'`
   - Query: `import { useAppQuery } from '@/lib/query/appQuery'`

4. **Create RPC wrapper** in `src/lib/supabase/`:
   ```typescript
   // src/lib/supabase/myFeature.ts
   import { supabase } from '@/integrations/supabase/client';
   import { Database } from '@/integrations/supabase/types';

   type RpcArgs = Database['public']['Functions']['function_name']['Args'];
   type RpcReturn = Database['public']['Functions']['function_name']['Returns'];

   export async function myFeatureRpc(
     args: RpcArgs
   ): Promise<RpcReturn> {
     const { data, error } = await supabase
       .rpc('function_name', args);

     if (error) throw error;
     return data;
   }
   ```

5. **Create TanStack Query hook** in `src/lib/query/`:
   ```typescript
   // src/lib/query/myFeature.ts
   import { useQuery } from '@tanstack/react-query';
   import { myFeatureRpc } from '@/lib/supabase/myFeature';
   import { queryKeys } from './keys';

   export function useMyFeature(userId: number) {
     return useQuery({
       queryKey: queryKeys.myFeature(userId),
       queryFn: () => myFeatureRpc({ user_id: userId }),
       staleTime: 5 * 60 * 1000, // 5 minutes
     });
   }
   ```

6. **Update query keys** in `src/lib/query/keys.ts`:
   ```typescript
   export const queryKeys = {
     // ... existing keys
     myFeature: (userId: number) => ['myFeature', userId] as const,
   };
   ```

### Phase 4: Testing (MANDATORY) (15-30 minutes)

**From AGENTS.md:** "Never write placeholder tests; new behavior needs real tests."

#### 4.1 Unit/Component Tests

```bash
npm run test
```

**Create test file** co-located with implementation:
```typescript
// ComponentName.test.tsx or function.test.ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ComponentName } from './ComponentName';

describe('ComponentName', () => {
  it('renders with required props', () => {
    render(<ComponentName propName="test" />);
    expect(screen.getByText('test')).toBeInTheDocument();
  });

  it('handles interaction correctly', async () => {
    const handleClick = vi.fn();
    render(<ComponentName propName="test" onClick={handleClick} />);

    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

**Requirements:**
- ✓ Every new function/component needs tests
- ✓ Tests have REAL assertions (no `expect(true).toBe(true)`)
- ✓ Tests would FAIL if code is broken
- ✓ Edge cases covered

**If tests fail:**
1. Read error output carefully
2. Fix the issue (code or test)
3. Re-run full test suite
4. Document in "Surprises & Discoveries" if unexpected

#### 4.2 Database Tests

```bash
npm run test:db
```

Must pass if database changes were made.

**If pgTAP tests fail:**
1. Check migration applied: `supabase db reset`
2. Verify function exists: `\df function_name` in psql
3. Check SQL syntax and logic
4. Verify auth mocking setup correctly

#### 4.3 Build & Lint

```bash
npm run build
npm run lint
```

Both must pass. Fix any errors before proceeding.

#### 4.4 Manual Verification

Follow the ExecPlan's "Validation and Acceptance" guidance:
1. Start dev server: `npm run dev`
2. Navigate to specified URL
3. Perform specified actions
4. Verify expected behavior

**Document results:**
- What you tested
- What you observed
- Whether it matches acceptance criteria

### Phase 5: Commit & Update ExecPlan (10 minutes)

#### 5.1 Stage Specific Files

```bash
git status  # Review changes

# Add specific files (NOT git add -A)
git add path/to/file1.ts
git add path/to/file2.sql
git add path/to/file3.test.ts
```

#### 5.2 Commit with Clear Message

```bash
git commit -m "$(cat <<'EOF'
[Imperative summary of what this accomplishes]

[Body: explain what changed and why, reference ExecPlan]

Implementation details:
- [Detail 1]
- [Detail 2]

Testing:
- Unit tests: PASS
- Database tests: PASS (if applicable)
- Manual verification: [brief description]

Ref: docs/exec-plans/active/[filename].md - [task description]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

Example:
```
Add wallet transaction history RPC and UI

Implemented get_wallet_transactions RPC function and React component
to display transaction history for parents.

Implementation details:
- Created migration 20250101120000_wallet_transactions.sql
- Added RPC function with auth.uid() validation
- Created ParentTransactionHistory component
- Added useWalletTransactions TanStack Query hook
- Updated RPC allowlist (docs + frontend + tests)

Testing:
- Unit tests: PASS (12 new tests)
- Database tests: PASS (5 pgTAP tests)
- Manual verification: Navigated to /parent/wallet, verified table displays

Ref: docs/exec-plans/active/20250101-wallet-history.md - Task 3

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

#### 5.3 Push Changes

```bash
git push
```

#### 5.4 Update ExecPlan (Living Document)

Edit the ExecPlan file:

1. **Mark task complete in Progress:**
   ```markdown
   ## Progress
   - [x] (2025-10-01 15:30 UTC) Task 3: Add wallet transaction history
   ```

2. **Add to Surprises & Discoveries** (if applicable):
   ```markdown
   ## Surprises & Discoveries

   - Observation: RPC function required JOIN with payments table for full history
     Evidence: Initial query only returned wallet deposits, missing usage records
     Resolution: Added LEFT JOIN on payments.wallet_transaction_id
   ```

3. **Add to Decision Log** (if decisions made):
   ```markdown
   ## Decision Log

   - Decision: Display transactions in descending chronological order (newest first)
     Rationale: Users typically care about recent activity; matches banking app UX
     Date/Author: 2025-10-01 / Building Agent
   ```

4. **Update timestamps and status**

5. **Commit the ExecPlan update:**
   ```bash
   git add docs/exec-plans/active/[filename].md
   git commit -m "Update ExecPlan: Task 3 complete"
   git push
   ```

### Phase 6: Output & Exit (2 minutes)

#### If Task Complete:

```
Task Complete
=============
Task: [task description]
ExecPlan: docs/exec-plans/active/[filename].md

Changes:
- Files modified: [list]
- Tests added: [list]
- Lines added/removed: [summary]

Validation:
✓ Unit tests: PASS ([N] tests)
✓ DB tests: PASS ([N] tests) [if applicable]
✓ Build: PASS
✓ Lint: PASS
✓ Manual: VERIFIED

Commit: [commit hash]

Next unchecked task: [description of next task]
OR: All tasks complete - Ready for Outcomes & Retrospective

<promise>TASK_COMPLETE</promise>
```

**EXIT IMMEDIATELY** - Loop will spawn fresh context for next task.

#### If All Tasks Complete:

Write the "Outcomes & Retrospective" section:

```markdown
## Outcomes & Retrospective

Implementation completed: YYYY-MM-DD HH:MM UTC

### What Was Achieved
[Summarize what was built and delivered]

### Comparison to Original Purpose
[Reference "Purpose / Big Picture" and confirm goals met]

### Gaps or Future Work
[Note any scope reductions or follow-up items]

### Lessons Learned
[Key insights from implementation]

### Final Validation
- Command: [test command]
  Result: [output]
- Manual: [verification steps performed]
  Result: [observed behavior]

This ExecPlan is now complete and may be moved to docs/exec-plans/completed/.
```

Then run the systematic-learning fallback trigger (dedup-safe):

1. Open `.codex/skills/execplan-learning-loop/SKILL.md`.
2. Execute the skill in `apply` mode against the completed implementation ExecPlan.
3. If evidence is weak/conflicting, ensure a watch-pattern entry is written to `docs/decisions/systematic-improvement-ledger.md`.
4. If edits are applied, ensure auto-commit message format is:
   `chore(skill:execplan-learning-loop): systematic feedback updates [ledger:<entry-id>]`

Then output:
```
ExecPlan Complete!
==================
File: docs/exec-plans/active/[filename].md
Total tasks: [N]
Total commits: [N]
Duration: [time span]

All tasks implemented and validated.
Outcomes & Retrospective: WRITTEN

<promise>EXECPLAN_COMPLETE</promise>
```

**EXIT** - Human will review and archive ExecPlan.

## Failure Handling

### Tests Fail

**DO:**
1. Read error output completely
2. Identify root cause
3. If failure is execution-context related (for example `listen EPERM`, Docker socket permission errors, or sandbox-only localhost bind failures), retry once by changing only execution context (elevated run) and record both attempts in artifacts/plan notes
4. Fix the issue
5. Re-run ALL tests
6. Create NEW commit (don't amend)
7. Document in "Surprises & Discoveries"

**DON'T:**
- ❌ Edit tests to make them pass
- ❌ Skip tests
- ❌ Assume tests are wrong

### Task is Blocked

If you discover the task cannot be completed:

1. Document in ExecPlan:
   ```markdown
   ## Progress
   - [~] Task N: [description] (BLOCKED: [specific reason])
   ```

2. Add to Decision Log:
   ```markdown
   - Decision: Blocked on Task N
     Rationale: [Why it's blocked, what's needed]
     Date/Author: [timestamp] / Building Agent
   ```

3. Output:
   ```
   Task Blocked
   ============
   Task: [description]
   Blocker: [specific issue]

   Details:
   [What was attempted]
   [Why it's blocked]
   [What's needed to unblock]

   <promise>BLOCKED</promise>
   ```

**EXIT** - Human must resolve blocker.

### ExecPlan Unclear

If the plan lacks necessary detail:

```
ExecPlan Needs Update
=====================
Task: [description]
Issue: [What's unclear]

Missing information:
- [Specific detail needed]
- [Specific detail needed]

Suggested update to [section name]:
[What should be added]

<promise>CLARIFICATION_NEEDED</promise>
```

**EXIT** - Human must update ExecPlan.

## Memory & Context

**You have NO memory of previous iterations.**

Your only context:
- Current file system state
- Git history (shows what's been done)
- ExecPlan document (your guide)

The ExecPlan is your complete instruction manual. Follow it literally.

## Non-Negotiable Constraints (AGENTS.md)

- ✓ TypeScript only (no `any`)
- ✓ One logical change per commit
- ✓ Real tests required (no placeholders)
- ✓ RPC-only Supabase access (no direct table access)
- ✓ Use `src/lib/time/format.ts` for time formatting
- ✓ Run `npm run test:db` before merging DB changes
- ✓ If uncertain, document in ExecPlan and ask

## Success Definition

A task is successfully complete when:

1. ✓ Code implements task as specified in ExecPlan
2. ✓ All tests pass (unit, DB, build, lint)
3. ✓ Manual verification confirms acceptance criteria
4. ✓ Changes committed with clear message
5. ✓ ExecPlan updated (Progress, Surprises, Decisions)
6. ✓ Changes pushed to remote
7. ✓ Output shows `<promise>TASK_COMPLETE</promise>`

One task. One commit. One update. One exit. Fresh context for next task.

That's the Ralph way.
