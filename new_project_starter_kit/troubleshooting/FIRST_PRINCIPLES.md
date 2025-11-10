# Troubleshooting First Principles

## Core Philosophy

**STOP. THINK. UNDERSTAND. THEN ACT.**

Every bug fix should follow this systematic approach. Rushing to "fix" things creates more problems than it solves.

---

## The First Principles Framework

### 1. UNDERSTAND THE PROBLEM (Before Any Code)

#### Ask These Questions First:
- ❓ **What is the actual problem?** (Not symptoms, the real issue)
- ❓ **What was the expected behavior?**
- ❓ **What is the current behavior?**
- ❓ **When did this start happening?** (What changed?)
- ❓ **Can I reproduce it reliably?**
- ❓ **What environment?** (Local, staging, production?)

#### Gather Complete Information:
```bash
# Don't assume - verify everything
✅ Check logs (backend.log, scheduler.log)
✅ Check database state (actual data, not assumptions)
✅ Check API responses (curl the actual endpoint)
✅ Check recent commits (git log --oneline -10)
✅ Check deployment status (Railway/Vercel logs)
```

**🚫 NEVER skip this step to start coding faster.**

---

### 2. IDENTIFY ROOT CAUSE (Not Symptoms)

#### The "5 Whys" Technique:

**Example: "Last scrape timestamp not showing"**

1. **Why?** → API returns `null` for `last_updated`
2. **Why?** → No trades in database today
3. **Why?** → Query only returns timestamp if trades exist
4. **Why?** → We're querying the trades table, not scrape attempts
5. **Root Cause:** No dedicated table to track scrape attempts

**Wrong approach:** "Add a marker trade to the trades table" (treats symptom)
**Right approach:** "Create a scrape_logs table" (solves root cause)

#### Red Flags of Treating Symptoms:
- 🚩 Adding special case handling (`if marker != "_MARKER_"`)
- 🚩 Filtering out fake data in queries
- 🚩 Using magic strings or constants
- 🚩 Comments that say "workaround" or "hack"
- 🚩 Solution makes the codebase more complex

---

### 3. DESIGN THE COMPLETE SOLUTION

#### Before Writing ANY Code:

**A. Consider All Constraints:**
```yaml
Database:
  - Column size limits (VARCHAR lengths)
  - Foreign key constraints
  - Unique constraints
  - Performance implications

Deployment:
  - Will migrations run automatically?
  - What happens on rollback?
  - Different databases (SQLite local, PostgreSQL prod)?
  - Environment variables needed?

Code:
  - TypeScript/Python type safety
  - API contract changes
  - Backward compatibility
  - Error handling
```

**B. Ask: "What Could Go Wrong?"**
- What if database is empty?
- What if migration fails?
- What if old data exists?
- What if API call times out?
- What if user has no permissions?

**C. Design for Scalability:**
```
❌ BAD: Quick fix that creates tech debt
✅ GOOD: Proper architecture that's maintainable

Example:
❌ Add marker records to trades table
   - Pollutes data
   - Requires filtering everywhere
   - Fragile and error-prone

✅ Create dedicated scrape_logs table
   - Clean separation of concerns
   - Easy to query
   - Can add metadata later
   - No special cases needed
```

---

### 4. VALIDATE THE APPROACH

#### Before Implementing:

**Checklist:**
- [ ] Does this solve the root cause? (Not just symptoms)
- [ ] Is this the simplest solution? (Occam's Razor)
- [ ] Will this work in all environments? (Local, staging, prod)
- [ ] Does this create technical debt?
- [ ] Can this be extended later?
- [ ] Are there existing patterns in the codebase to follow?

**Ask Clarifying Questions:**
```
Instead of assuming:
❓ "Should timestamps be in UTC or PT?"
❓ "Do we need to track scrape failures?"
❓ "What's the retention policy for logs?"
❓ "How will this scale with more scrape types?"
```

---

### 5. IMPLEMENT SYSTEMATICALLY

#### Development Order:

**A. Data Layer First:**
```python
1. Database schema/models
2. Migration scripts
3. Test migration locally
```

**B. Backend Logic:**
```python
4. Update scraper to log attempts
5. Update API to read from new source
6. Add error handling
7. Test locally with curl
```

**C. Frontend:**
```typescript
8. Update API calls
9. Update UI display
10. Test in browser
```

**D. Deployment:**
```bash
11. Ensure migrations run on deployment
12. Test in staging (if available)
13. Deploy to production
14. Verify with real API calls
```

**🚫 NEVER deploy all changes at once without testing each layer.**

---

### 6. TEST THOROUGHLY

#### Test Matrix:

```
Environment | Database | Expected Behavior
------------|----------|------------------
Local       | SQLite   | ✅ Tables created, data correct
Local       | Empty DB | ✅ Migration runs, no errors
Production  | PostgreSQL | ✅ Auto-migration on startup
Production  | Existing data | ✅ Backward compatible
```

#### Edge Cases to Always Test:
- Empty database
- Missing environment variables
- Network failures
- Timezone differences (UTC vs PT)
- Large datasets
- Old/stale data

---

## Common Anti-Patterns to Avoid

### 1. The "Quick Fix" Trap
```python
# ❌ BAD: Quick hack
if trade_number == "_MARKER_":
    continue  # Skip fake marker

# ✅ GOOD: Proper solution
# Use dedicated scrape_logs table
```

### 2. The "It Works On My Machine"
```bash
# ❌ BAD: Only testing locally
$ python test_locally.py
# Looks good! Deploy!

# ✅ GOOD: Test deployment flow
$ # Test with production database
$ # Test migration scripts
$ # Test environment variables
$ # Test error scenarios
```

### 3. The "Assume It Will Work"
```python
# ❌ BAD: Assuming migration runs
# Just push code that needs new table

# ✅ GOOD: Ensure migration runs
# Add migration to app startup
# Test in staging first
# Verify table exists before using
```

### 4. The "Patch Over Patch"
```python
# ❌ BAD: Fixing symptoms repeatedly
v1: Add marker record
v2: Fix marker length issue
v3: Clean up old markers
v4: Fix count issue with markers

# ✅ GOOD: Fix root cause once
v1: Create scrape_logs table
# No more patches needed
```

---

## Real-World Example: Value-Trades Timestamp Issue

### ❌ What Went Wrong:

```
1. Problem: "Last scrape" not showing
   ↓
2. Quick fix: Add marker trade
   ↓
3. Issue: Marker too long for VARCHAR(10)
   ↓
4. Patch: Shorten marker
   ↓
5. Issue: Table doesn't exist in prod
   ↓
6. Patch: Add auto-migration
   ↓
7. Issue: Old markers still in database
   ↓
8. Patch: Add cleanup code
   ↓
9. Issue: Wrong timezone
   ↓
10. Patch: Add timezone conversion
```

**Result:** 10 commits, 3 deployments, multiple bugs

### ✅ What Should Have Happened:

```
1. Problem: "Last scrape" not showing
   ↓
2. Root cause analysis:
   - Need to track scrape attempts
   - Trades table is wrong place
   ↓
3. Complete solution design:
   - Create scrape_logs table
   - Track all attempts (success/failure)
   - Store in UTC, display in PT
   - Auto-migration on startup
   - Test locally and in prod
   ↓
4. One implementation, one deployment
```

**Result:** 1 commit, 1 deployment, clean solution

---

## Decision-Making Framework

### When Faced With a Problem:

```
┌─────────────────────────────────────┐
│  Can I fix root cause in <30 min?  │
└─────────────┬───────────────────────┘
              │
        ┌─────┴─────┐
        │    YES    │
        └─────┬─────┘
              │
    ┌─────────▼──────────┐
    │ Design complete    │
    │ solution properly  │
    └─────────┬──────────┘
              │
        ┌─────┴─────┐
        │    NO     │
        └─────┬─────┘
              │
    ┌─────────▼──────────┐
    │ Break into phases  │
    │ or ask for help    │
    └────────────────────┘
```

### Red Flags to STOP and Rethink:

- 🚩 "I'll just add a quick check here..."
- 🚩 "This is a temporary workaround..."
- 🚩 "I'll fix it properly later..."
- 🚩 "It works, I don't know why..."
- 🚩 "Let me try this and see what happens..."
- 🚩 "I fixed it in one place, that should be enough..."

### Green Flags to Proceed:

- ✅ "I understand why this happens..."
- ✅ "This solves the root cause..."
- ✅ "This is maintainable long-term..."
- ✅ "I've tested all edge cases..."
- ✅ "This follows existing patterns..."
- ✅ "I've searched for ALL instances of this pattern..."

---

## Systematic vs. Reactive Debugging

### ❌ The "Whack-a-Mole" Anti-Pattern:

**What it looks like:**
```
Bug appears → Fix in one file → Deploy
Same bug appears elsewhere → Fix that file → Deploy
Same bug appears again → Fix another file → Deploy
Repeat 4-5 times...
```

**Real example from today:**
```
1. Trade Priorities: No Barchart trades (4 PM PT)
   → Fix timezone bug in trade_prioritization.py
2. Manual rescrape: Finds 0 trades (5 PM PT)
   → Fix timezone bug in options.py
3. Barchart page: Internal server error
   → Fix timezone bug in stats endpoint
4. Trade Priorities: STILL no Barchart trades
   → Fix timezone bug AGAIN in trade_prioritization.py (different line!)
```

**Why it happens:**
- Treating each symptom as a separate bug
- Not looking for the underlying pattern
- Rushing to "fix it and move on"

**Cost:**
- 4 separate commits
- 4 separate deployments
- Multiple hours of debugging
- User frustration

---

### ✅ The Systematic Approach:

**What it looks like:**
```
Bug appears → Identify pattern → Search entire codebase → Fix ALL instances → Deploy ONCE
```

**How to do it:**
1. **Identify the pattern** (not just the instance)
   ```bash
   # Example: First bug was timezone-naive datetime.now()
   # Don't just fix that ONE line...
   ```

2. **Search the ENTIRE codebase**
   ```bash
   # Find ALL instances of the pattern
   grep -r "datetime.now()" backend/

   # Or use more specific patterns
   grep -r "datetime.now() -" backend/  # Comparisons
   grep -r "datetime.now().replace" backend/  # Filtering
   ```

3. **Categorize by criticality**
   ```
   CRITICAL (business logic):
   - Date filtering queries
   - Cache timestamp comparisons
   - Data expiry checks

   NON-CRITICAL (display only):
   - Logging timestamps
   - Response metadata
   - Debug output
   ```

4. **Fix ALL critical instances at once**
   ```python
   # Not just the one that broke
   # But EVERY place that could break
   ```

5. **Document the pattern in commit message**
   ```
   Fix: Replace all datetime.now() with datetime.now(PT)

   Root cause: timezone-naive datetimes throughout codebase
   Impact: 4 API routes, 12 instances
   Pattern: Any datetime.now() used for business logic
   ```

---

### Decision Tree: Reactive vs. Systematic

```
Bug found
    ↓
Is this the first time I'm fixing this type of bug?
    ↓
├─→ YES: Is it a pattern that could exist elsewhere?
│       ↓
│   ├─→ YES: STOP! Search entire codebase
│   │           Fix ALL instances
│   │           Document the pattern
│   │
│   └─→ NO: Fix this instance
│               Document why it's unique
│
└─→ NO: You're in whack-a-mole mode!
        ↓
    STOP AND RESTART:
    1. What's the underlying pattern?
    2. Where else could this exist?
    3. Fix comprehensively THIS TIME

```

---

### Questions to Ask When Fixing Bugs:

#### 1. "Is this an isolated bug or a pattern?"
```
Isolated: "Typo in variable name"
Pattern: "timezone-naive datetime.now()"
```

#### 2. "Could this exist elsewhere in the codebase?"
```
If YES → Search before fixing
If NO → Explain why in commit message
```

#### 3. "Have I fixed something similar recently?"
```
If YES → You're in reactive mode!
         Search for all instances NOW
```

#### 4. "What would I search for to find similar issues?"
```
# Be specific with your search
❌ grep "now()"  # Too broad
✅ grep "datetime.now()" # Specific pattern
✅ grep -E "datetime\.now\(\)\s*[-+]" # Even more specific
```

#### 5. "If I deploy this, could the same bug appear tomorrow?"
```
If YES → You're fixing symptoms
         Find and fix root pattern
```

---

### The "Search-First" Protocol

**Before fixing ANY bug that could be a pattern:**

1. **Pause and ask:** "Could this exist elsewhere?"

2. **Search systematically:**
   ```bash
   # Example: Found timezone bug
   grep -r "datetime.now()" backend/api/
   grep -r "datetime.now()" backend/services/
   grep -r "datetime.now()" backend/scheduler/
   ```

3. **Create a checklist of ALL instances**
   ```
   Found 47 instances of datetime.now()

   CRITICAL (must fix):
   - [ ] backend/api/routes/daily_brief.py (7 instances)
   - [ ] backend/api/routes/trade_prioritization.py (2 instances)
   - [ ] backend/api/routes/recommendations.py (3 instances)
   - [ ] backend/api/routes/trades.py (2 instances)

   NON-CRITICAL (can defer):
   - [ ] backend/services/logging.py (33 instances - display only)
   ```

4. **Fix comprehensively**
   - Don't just fix the one that broke
   - Fix ALL critical instances
   - Document the pattern

5. **One commit, one deployment**
   ```
   ✅ "Fix all timezone bugs across API routes (4 files, 14 instances)"

   NOT:
   ❌ "Fix timezone bug"
   ❌ "Fix timezone bug again"
   ❌ "Fix another timezone bug"
   ❌ "Fix yet another timezone bug"
   ```

---

### Real-World Comparison

#### ❌ Reactive Debugging (What We Did):
```
5:00 PM - Fix trade_prioritization.py line 79
5:10 PM - Fix options.py lines 304, 326
5:20 PM - Fix options.py stats endpoint
5:30 PM - Fix trade_prioritization.py line 91 (missed this!)
```
**Total time:** 30+ minutes, 3 commits, user frustration

#### ✅ Systematic Debugging (What We Should Have Done):
```
5:00 PM - Bug found in trade_prioritization.py
5:01 PM - Search: grep -r "datetime.now()" backend/api/
5:03 PM - Categorize: 14 critical, 33 non-critical
5:05 PM - Fix ALL 14 critical instances
5:10 PM - Test, commit, deploy
```
**Total time:** 10 minutes, 1 commit, complete fix

**Time saved:** 20+ minutes
**Bugs prevented:** 3 additional bug reports
**User experience:** Fixed on first try

---

## Deployment Checklist

### Before Pushing to Production:

```bash
# 1. Local Testing
[ ] All tests pass
[ ] Database migration works
[ ] API returns expected data
[ ] Frontend displays correctly
[ ] Error cases handled

# 2. Environment Verification
[ ] Environment variables documented
[ ] Migration runs on app startup
[ ] Works with production database type
[ ] Timezone handling correct
[ ] Logging in place

# 3. Rollback Plan
[ ] Can revert migration safely?
[ ] Will old code work with new schema?
[ ] What's the recovery procedure?

# 4. Documentation
[ ] Code comments explain "why"
[ ] README updated if needed
[ ] Breaking changes noted
[ ] Migration instructions clear
```

---

## Questions to Ask Before EVERY Fix

### The Fundamental Questions:

1. **Do I fully understand the problem?**
   - If no → Gather more information

2. **Do I know the root cause?**
   - If no → Do deeper analysis

3. **Is this the simplest solution?**
   - If no → Find simpler approach

4. **Will this create new problems?**
   - If yes → Redesign solution

5. **Can I test this completely?**
   - If no → Break into smaller pieces

6. **Is this maintainable?**
   - If no → Choose different approach

---

## Summary: The Golden Rules

### 🥇 Rule #1: Understand Before Acting
**Never write code without understanding the root cause.**

### 🥇 Rule #2: Design Complete Solutions
**Fix the problem, not the symptoms.**

### 🥇 Rule #3: Consider All Implications
**Think through deployment, edge cases, and scalability.**

### 🥇 Rule #4: Test Thoroughly
**Verify the complete flow, not just happy path.**

### 🥇 Rule #5: Document Your Reasoning
**Future you (or others) need to understand why.**

---

## When In Doubt

**STOP. ASK. CLARIFY.**

It's always better to:
- ✅ Ask a clarifying question
- ✅ Take time to design properly
- ✅ Admit you don't know something
- ✅ Request help on complex issues

Than to:
- ❌ Rush to a quick fix
- ❌ Assume you understand
- ❌ Create technical debt
- ❌ Deploy broken code

---

**Remember: The fastest way to solve a problem is to solve it correctly the first time.**

