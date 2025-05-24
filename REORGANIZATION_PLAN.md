# Project Reorganization Plan

## Current Issues
1. Inconsistent naming: "echo-" vs root level files
2. Documentation scattered across multiple locations
3. Redundant directories (evolution/, agents/)
4. Demo/test files at root level

## Proposed Structure

```
/agentic-persona/ (or rename to /echo/)
├── README.md
├── LICENSE
├── .gitignore
├── package.json (workspace root)
├── firebase.json
├── firestore.rules
├── firestore.indexes.json
│
├── /docs/
│   ├── /architecture/
│   │   ├── system-design.md
│   │   ├── framework-analysis.md
│   │   ├── security-roadmap.md
│   │   └── architecture-decisions.md
│   ├── /development/
│   │   ├── contributing.md
│   │   ├── testing.md
│   │   ├── known-issues.md
│   │   └── naming-conventions.md
│   ├── /deployment/
│   │   ├── firebase-setup.md
│   │   ├── quick-start.md
│   │   └── environment-variables.md
│   └── /api/
│       └── endpoints.md
│
├── /backend/ (rename from echo-backend)
│   ├── requirements.txt
│   ├── main.py
│   ├── /agents/
│   ├── /services/
│   ├── /api/
│   └── /integrations/
│
├── /frontend/ (rename from echo-frontend)
│   ├── package.json
│   ├── vite.config.js
│   ├── /src/
│   └── /public/
│
├── /functions/ (rename from firebase-functions)
│   ├── requirements.txt
│   ├── main.py
│   ├── /integrations/
│   └── package.json
│
├── /shared/
│   ├── /types/
│   ├── /constants/
│   └── /utils/
│
├── /scripts/
│   ├── setup-dev.sh
│   ├── setup-firebase.sh
│   └── reorganize.sh
│
├── /tests/
│   ├── /backend/
│   ├── /frontend/
│   └── /integration/
│
└── /examples/
    ├── demo-echo.py
    ├── test-echo.py
    └── /configs/
        └── user-preferences.json
```

## Benefits
1. **Clearer organization** - Each directory has a single purpose
2. **Better scalability** - Easy to add new components
3. **Consistent naming** - All lowercase with hyphens
4. **Centralized docs** - All documentation in one place
5. **Shared resources** - Common code in /shared/

## Migration Steps
1. Create new directory structure
2. Move files to appropriate locations
3. Update all import paths
4. Update configuration files
5. Test everything still works
6. Remove old directories

## Considerations
- Keep git history intact
- Update all relative paths
- Update CI/CD configurations
- Update deployment scripts