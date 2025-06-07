# Music Service Proxy Integration

This directory contains the integration components for connecting AgenticPersona with the Music Service Proxy application.

## Structure

```
music-service-proxy/
├── migrations/          # Database migration files
│   ├── 001_add_agentic_tables.sql  # SQL version
│   └── 001_add_agentic_tables.js   # JS version for Node migration tools
├── INTEGRATION_GUIDE.md # Detailed integration instructions
└── README.md           # This file
```

## Quick Start

1. **Database Migration**
   ```bash
   # Copy migration to Music Service Proxy
   cp migrations/001_add_agentic_tables.js /home/patrick/music-service-proxy/migrations/
   
   # Run migration
   cd /home/patrick/music-service-proxy
   npm run migrate
   ```

2. **Backend Integration**
   See INTEGRATION_GUIDE.md for detailed backend implementation steps.

3. **Frontend Integration**
   Vue components and Pinia stores need to be added to the Music Service Proxy frontend.

## Key Features

- **Board Consultations**: Get AI-powered recommendations for music decisions
- **Preference Learning**: Automatically learn and store user preferences with confidence tracking
- **Verbose Logging**: Complete activity trail for all AgenticPersona interactions

## Related Documentation

- [Integration Guide](./INTEGRATION_GUIDE.md)
- [AgenticPersona Docs](../../docs/)
- [Music Service Proxy](../../../music-service-proxy/)