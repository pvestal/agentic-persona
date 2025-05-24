# Firebase Deployment Guide for Agentic Persona

This guide walks you through deploying the Agentic Persona system to Firebase.

## Prerequisites

1. **Node.js** (v18 or higher)
2. **Python** (v3.11)
3. **Firebase CLI** installed globally
4. **Google Cloud account** with billing enabled
5. **API Keys** for OpenAI/Anthropic

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Create Project"
3. Name it: `agentic-persona`
4. Enable Google Analytics (optional)
5. Wait for project creation

## Step 2: Enable Required Services

In Firebase Console:

1. **Authentication**
   - Go to Authentication > Sign-in method
   - Enable "Google" provider
   - Add your domain to authorized domains

2. **Firestore Database**
   - Go to Firestore Database
   - Click "Create database"
   - Start in production mode
   - Choose your region (us-central1 recommended)

3. **Cloud Functions**
   - Go to Functions
   - Click "Get started"
   - Upgrade to Blaze plan (required for external API calls)

## Step 3: Install Firebase CLI

```bash
npm install -g firebase-tools
firebase login
```

## Step 4: Initialize Firebase Project

```bash
cd /workspaces/agentic-persona
firebase init

# Select:
# - Firestore
# - Functions (Python)
# - Hosting
# - Emulators (optional for local testing)

# Use existing project: agentic-persona
# Accept default options
```

## Step 5: Configure Environment Variables

### Frontend (.env.production)

```bash
cd echo-frontend
cp .env.example .env.production
# Edit .env.production with your Firebase config
```

Get Firebase config from:
- Firebase Console > Project Settings > General > Your apps > Web app

### Backend Functions (.env.yaml)

```bash
cd ../firebase-functions
cp .env.yaml.example .env.yaml
# Edit .env.yaml with your API keys
```

Deploy environment variables:
```bash
firebase functions:config:set \
  openai.key="your-key" \
  anthropic.key="your-key" \
  google.client_id="your-id" \
  google.client_secret="your-secret"
```

## Step 6: Set Up OAuth Providers

### Google OAuth (Gmail Integration)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your Firebase project
3. Enable Gmail API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: 
     - `https://your-project.firebaseapp.com/auth/gmail/callback`
     - `https://us-central1-your-project.cloudfunctions.net/api/integrations/gmail/callback`

### Slack OAuth

1. Go to [Slack API](https://api.slack.com/apps)
2. Create New App > From scratch
3. Add OAuth Scopes (see `slack.py` for list)
4. Add Redirect URLs:
   - `https://your-project.firebaseapp.com/auth/slack/callback`
   - `https://us-central1-your-project.cloudfunctions.net/api/integrations/slack/callback`

## Step 7: Build Frontend

```bash
cd echo-frontend
npm install
npm run build
```

## Step 8: Deploy

### Deploy everything:
```bash
cd ..
firebase deploy
```

### Deploy individually:
```bash
# Firestore rules
firebase deploy --only firestore:rules

# Cloud Functions
firebase deploy --only functions

# Hosting
firebase deploy --only hosting
```

## Step 9: Post-Deployment Setup

1. **Test Authentication**
   - Visit `https://your-project.firebaseapp.com`
   - Click "Sign in with Google"
   - Verify user document created in Firestore

2. **Test Functions**
   ```bash
   curl https://us-central1-your-project.cloudfunctions.net/api/agents
   ```

3. **Configure Domain (Optional)**
   - Firebase Console > Hosting
   - Add custom domain

## Step 10: Set Up Monitoring

1. **Firebase Console**
   - Performance Monitoring
   - Crashlytics
   - Analytics

2. **Google Cloud Console**
   - Cloud Functions logs
   - Error reporting
   - Uptime checks

## Security Checklist

- [ ] Enable App Check for API protection
- [ ] Review Firestore Security Rules
- [ ] Enable Cloud Armor for DDoS protection
- [ ] Set up budget alerts
- [ ] Configure CORS properly
- [ ] Rotate API keys regularly
- [ ] Enable audit logging

## Troubleshooting

### Functions not deploying
- Ensure Python 3.11 is installed
- Check `.env.yaml` format
- Verify billing is enabled

### Authentication issues
- Check authorized domains
- Verify OAuth redirect URIs
- Check Firebase Auth settings

### Performance issues
- Enable Cloud CDN
- Optimize Firestore queries
- Use Firebase Performance Monitoring

## Cost Optimization

1. **Set budget alerts** in Google Cloud Console
2. **Use Firestore efficiently**:
   - Batch writes
   - Compound queries
   - Proper indexing
3. **Optimize Functions**:
   - Set appropriate memory/timeout
   - Use minimum instances wisely
4. **Monitor usage**:
   - Firebase Console > Usage & billing

## Production Checklist

- [ ] Environment variables set
- [ ] OAuth providers configured
- [ ] Firestore indexes created
- [ ] Security rules tested
- [ ] Error reporting enabled
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] SSL certificates valid
- [ ] CORS configured
- [ ] Rate limiting enabled

## Next Steps

1. **Connect messaging platforms**:
   - Complete Gmail OAuth flow
   - Add Slack workspace
   - Configure SMS (Twilio)

2. **Enable features**:
   - Turn on autonomous responses
   - Configure learning system
   - Set up evolution cycles

3. **Monitor and optimize**:
   - Watch performance metrics
   - Analyze user behavior
   - Iterate on agent responses

## Support

- Firebase Documentation: https://firebase.google.com/docs
- Project Issues: https://github.com/your-username/agentic-persona/issues
- Community Discord: [Coming Soon]