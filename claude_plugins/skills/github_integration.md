# GitHub Integration Skill

**Auto-activated when**: Working with GitHub repositories, PRs, issues, commits, or CI/CD workflows

## Description
This skill enables Claude to interact with GitHub's REST API seamlessly. It provides comprehensive access to repositories, issues, pull requests, actions, and security features without requiring manual tool switching.

## Capabilities

### Repository Management
- Read and analyze repository structure
- Access file contents and history
- Search across repositories
- Clone and fork repositories

### Issue Management
- Create, read, update issues
- Add labels and assignees
- Search issues by filters
- Track issue status and milestones

### Pull Request Operations
- Create and manage PRs
- Review code changes
- Merge and close PRs
- Analyze PR comments and reviews
- Check CI/CD status

### CI/CD Integration
- Trigger workflow runs
- Monitor action status
- Access workflow logs
- Analyze build failures

### Commit Analysis
- Review commit history
- Analyze code changes
- Track authors and contributions
- Generate commit reports

## When to Use

Claude will automatically activate this skill when you:
- Mention GitHub URLs or repository names
- Ask to create/review PRs
- Request issue tracking or creation
- Need CI/CD workflow analysis
- Want to analyze commits or code changes

## Setup Required

To enable this skill, the GitHub MCP server must be connected:

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

## Examples

"Create a PR for the feature branch"
"Show me all open issues labeled 'bug'"
"What failed in the latest CI run?"
"Analyze commits from the last week"
"Review PR #123"

## Source
Based on GitHub MCP Server (25,100+ GitHub stars)
Repository: https://github.com/github/github-mcp-server
