# Skill Update + HTTP Client Tool

## Date
2026-03-28

## Summary
Added general-purpose HTTP client tool and updated skills 03/04 for new template structure.

## Changes

### HTTP Client Tool
- `tools/http_client.py`: Reference implementation with lazy config, URL alias resolution, stdlib urllib
- `templates/tools/http_client.py.tmpl`: Template version with {{component_name}}, {{http_endpoints}} placeholders
- `templates/config/agent.yaml.tmpl`: Added optional `http` section (base_urls, default_timeout)
- `tests/test_checker.py`: Guard test for http_client tool

### Skill Updates
- `skills/03-generate-agent/SKILL.md`: Added models.py to structure, lazy config guidance, http_client reference, agent.py features (middleware/checkpointer/--once/--diagnose), updated handoff
- `skills/04-validate-structure/SKILL.md`: Updated quick start with new run modes, lazy config pattern in tool guide
- `CLAUDE.md`: Added HTTP Client to Default Tools

## Tests
- 18 guard tests pass
