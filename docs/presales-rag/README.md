# Presales RAG Documentation

This directory contains documentation for the presales service system with RAGFlow integration and slot-based alignment.

## Current Documentation

1. [Design & Architecture](./design-decision-record.md)
   - Overall design of the presales business layer
   - State machine architecture
   - Service directory structure
   - Code organization
   - Test records

2. [Runtime Configuration](./runtime-config.md)
   - Service directory structure
   - `proposal.md` and `slots.yaml` file locations
   - How changes take effect

3. [Template Writing Guide](./TEMPLATE_GUIDE.md)
   - Explanation of `slot/sys/rag/ai/ext` placeholder types
   - Boundaries and best practices
   - Template writing recommendations

## Current Business File Locations

Business configurations are not stored in the documentation directory but are driven by the service directory:

```text
presales_services/
  example-fashion-service/
    proposal.md    # Proposal template
    slots.yaml     # Slot configuration
```

## Documentation Principles

1. For architecture design and decision changes, update `design-decision-record.md`
2. For user-facing information about "where files go, how to modify, how to restart", update `runtime-config.md`
3. For template variables, placeholders, and template writing rules, update `TEMPLATE_GUIDE.md`
4. Do not add new temporary documents; if it's a short-term plan, put it in `plans/` or task records, not in this directory
