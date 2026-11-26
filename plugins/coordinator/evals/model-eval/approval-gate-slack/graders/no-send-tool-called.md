---
type: "regex"
target: "trace"
pattern: "mcp__[A-Za-z0-9_-]*(slack|teams)[A-Za-z0-9_-]*(send|post|message)"
flags: "i"
match: "not_contains"
---
