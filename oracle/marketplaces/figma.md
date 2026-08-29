# Figma Community — Source Reference

**URL:** https://www.figma.com/community
**Status:** LIVE
**Revenue Share:** Varies (plugins, templates, widgets)
**Agent-friendly:** Partial (Community API, MCP integration)

## Overview

Figma Community supports:
- Templates (design files)
- Plugins (code extensions)
- Widgets (interactive components)
- Other resources (icons, kits)

## API Overview

### Community Resources
```
GET /api/community/resources           — List community resources
GET /api/community/resources/{id}     — Get resource details
```

### Plugins
```
GET /api/plugins                       — List plugins
GET /api/plugins/{id}                  — Get plugin details
```

## Authentication
- Figma account
- OAuth 2.0 for API access

## MCP Integration
Figma now exposes MCP functionality for agents to interact with designs programmatically.

## Data Fields Available

| Field | Available | Notes |
|-------|-----------|-------|
| id | ✅ | Resource ID |
| name | ✅ | Resource name |
| description | ✅ | Full description |
| type | ✅ | Plugin, Widget, Template |
| price | ✅ | In USD |
| installs | ✅ | Install count |
| rating | ✅ | User rating |
| created_at | ✅ | Publication date |

## Limitations
- Requires Figma account
- Limited API for publishing
- MCP integration available for consumption
