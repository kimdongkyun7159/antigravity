# Database Query Assistant Skill

**Auto-activated when**: Working with databases, writing SQL queries, or analyzing data

## Description
This skill enables Claude to interact with various databases (PostgreSQL, MySQL, SQLite, etc.) through secure connections. It provides intelligent query generation, schema analysis, optimization suggestions, and data exploration capabilities.

## Capabilities

### Query Generation
- Write optimized SQL queries
- Generate complex JOIN operations
- Create aggregation and analytical queries
- Build dynamic queries based on requirements

### Schema Analysis
- Explore database structure
- Analyze table relationships
- Review indexes and constraints
- Generate ER diagrams (textual)

### Data Operations
- Execute SELECT queries safely
- Analyze query results
- Export data in various formats
- Validate data integrity

### Performance Optimization
- Suggest query optimizations
- Identify missing indexes
- Analyze slow queries
- Recommend schema improvements

### Database Management
- Generate migration scripts
- Create backup queries
- Design table structures
- Write stored procedures

## When to Use

Claude will automatically activate this skill when you:
- Ask about database queries or data
- Need to analyze database schema
- Request SQL query writing
- Want to optimize database performance
- Mention table names or data operations

## Setup Required

To enable this skill, connect to your database via MCP:

### PostgreSQL
```bash
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub --dsn "postgresql://user:password@host:5432/database"
```

### MySQL
```bash
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub --dsn "mysql://user:password@host:3306/database"
```

### SQLite
```bash
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub --dsn "sqlite://path/to/database.db"
```

## Examples

"Show me all users who registered last month"
"Optimize this slow query"
"What's the schema of the orders table?"
"Write a JOIN to get customer order history"
"Generate a migration to add an index"

## Security Notes

- Read-only connections are recommended for production databases
- Use environment variables for credentials
- Never commit connection strings to git
- Validate queries before execution on production data

## Source
Based on popular database MCP servers
Compatible with: PostgreSQL, MySQL, SQLite, MongoDB, and more
