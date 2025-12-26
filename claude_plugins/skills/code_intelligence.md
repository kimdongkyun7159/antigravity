# Code Intelligence Skill

**Auto-activated when**: Analyzing code, refactoring, or understanding complex codebases

## Description
This skill enhances Claude's code understanding through Language Server Protocol (LSP) integration. It provides real-time type checking, definition lookup, reference finding, and intelligent code navigation across your entire codebase.

## Capabilities

### Code Navigation
- Jump to definitions
- Find all references
- Navigate type hierarchies
- Explore symbol relationships

### Type Analysis
- Real-time type checking
- Infer missing types
- Detect type errors
- Suggest type annotations

### Code Intelligence
- Auto-complete suggestions
- Signature help for functions
- Hover documentation
- Symbol renaming with safety checks

### Refactoring Support
- Identify refactoring opportunities
- Suggest code improvements
- Detect code smells
- Recommend design patterns

### Cross-File Analysis
- Track dependencies
- Analyze import chains
- Detect circular dependencies
- Map module relationships

## When to Use

Claude will automatically activate this skill when you:
- Ask to understand complex code
- Request refactoring suggestions
- Need to find where code is used
- Want type safety improvements
- Analyze code structure and architecture

## Setup Required

LSP integration is typically built into Claude Code for major languages:
- TypeScript/JavaScript (tsserver)
- Python (Pyright, pylsp)
- Rust (rust-analyzer)
- Go (gopls)
- Java (jdtls)

No additional setup required for most projects!

## Examples

"Where is this function defined?"
"Find all usages of this variable"
"What's the type of this expression?"
"Refactor this code to use async/await"
"Show me all classes that implement this interface"

## Supported Languages

- JavaScript/TypeScript
- Python
- Rust
- Go
- Java
- C/C++
- Ruby
- PHP
- And many more through LSP

## Benefits

- Faster code comprehension
- Safer refactoring
- Reduced bugs from type errors
- Better code navigation
- Intelligent suggestions
