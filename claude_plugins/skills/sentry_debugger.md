# Sentry Error Debugger Skill

**Auto-activated when**: Debugging errors, analyzing crash reports, or tracking application issues

## Description
This skill connects Claude to Sentry's error monitoring platform, providing real-time access to error context, stack traces, user impact data, and resolution suggestions. It enables AI-powered debugging without leaving the development environment.

## Capabilities

### Error Analysis
- Fetch error details and stack traces
- Analyze error frequency and trends
- Identify affected users and sessions
- Track error resolution status

### Issue Context
- Access full issue context from Sentry
- Review breadcrumbs and user actions
- Analyze environment and device data
- Check related errors and patterns

### Debugging Assistance
- Suggest fixes based on error patterns
- Identify root causes
- Recommend preventive measures
- Generate bug fix PRs

### Monitoring
- Track error rates over time
- Monitor release health
- Alert on new error types
- Analyze performance issues

## When to Use

Claude will automatically activate this skill when you:
- Encounter runtime errors or exceptions
- Ask about application crashes
- Need to debug production issues
- Want to analyze error trends
- Request error impact assessment

## Setup Required

To enable this skill, the Sentry MCP server must be connected:

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
```

## Examples

"What's causing the 500 errors in production?"
"Show me the stack trace for issue #12345"
"How many users are affected by this error?"
"Analyze errors from the last deployment"
"Suggest a fix for this crash"

## Source
Based on Sentry MCP Server (Official)
Repository: https://github.com/getsentry/sentry-mcp
Documentation: https://docs.sentry.io/product/sentry-mcp/
