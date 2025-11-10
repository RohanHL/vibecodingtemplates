# Troubleshooting Guides

Systematic debugging guides and common issue resolution.

## Available Guides

### [First Principles Debugging](FIRST_PRINCIPLES.md)
Comprehensive guide for systematic troubleshooting:
- Root cause analysis methodology
- Common patterns and anti-patterns
- Timezone debugging (major source of bugs)
- Database query debugging
- API endpoint debugging
- Frontend data flow debugging

**When to Use:**
- Production bugs with unclear cause
- Intermittent issues
- "It worked yesterday" problems
- Multiple failed quick fixes

**Approach:**
1. Reproduce the issue consistently
2. Isolate the component (frontend/backend/database)
3. Test assumptions systematically
4. Fix root cause, not symptoms

---

## Troubleshooting Philosophy

> "Don't guess. Don't throw random fixes at the wall. Understand the system first, then fix it properly."

### Key Principles

1. **Reproduce First** - Can't fix what you can't see
2. **Isolate Components** - Frontend vs Backend vs Database
3. **Check Assumptions** - "It should work" often means "I assume it works"
4. **Test Systematically** - Binary search through possibilities
5. **Fix Root Cause** - Not symptoms

### Common Mistakes

❌ Changing multiple things at once
❌ Not testing after each change
❌ Assuming caching is the problem
❌ Fixing symptoms instead of root cause
❌ Not checking logs before debugging

✅ Change one thing at a time
✅ Test immediately after change
✅ Verify data exists before assuming cache issue
✅ Trace issue back to source
✅ Read logs first, guess second

---

## Related Documentation

- **[Fixes Log](../fixes/)** - Historical bug fixes
- **[Common Issues](COMMON_ISSUES.md)** - FAQ-style troubleshooting (coming soon)

---

**Last Updated:** November 5, 2025
