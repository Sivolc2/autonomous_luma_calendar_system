# Deployment Guide

This guide covers deploying the Autonomous Luma Calendar System to various platforms.

## Heroku Deployment

### Prerequisites

1. [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. [Git](https://git-scm.com/downloads)
3. Heroku account
4. Luma API key
5. Slack App credentials (if using Slack integration)

### Steps

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```
   OR if it's already created:
   ```bash
   heroku git:remote -a the-commons-events
   ```

4. **Configure Environment Variables**
   ```bash
   heroku config:set LUMA_API_KEY=your_api_key
   heroku config:set SLACK_BOT_TOKEN=your_slack_bot_token
   heroku config:set SLACK_SIGNING_SECRET=your_slack_signing_secret
   ```

5. **Deploy to Heroku**
   ```bash
   git push heroku main
   ```

6. **Verify Deployment**
   ```bash
   heroku open
   ```

7. **View Logs (if needed)**
   ```bash
   heroku logs --tail
   ```

### Updating Slack App Configuration

After deploying to Heroku, update your Slack App configuration:

1. Go to your [Slack Apps](https://api.slack.com/apps)
2. Select your app
3. Under "Slash Commands", update the command URL to:
   ```
   https://your-app-name.herokuapp.com/slack/events
   ```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LUMA_API_KEY` | Your Luma Calendar API key | Yes |
| `SLACK_BOT_TOKEN` | Slack Bot User OAuth Token | For Slack integration |
| `SLACK_SIGNING_SECRET` | Slack App Signing Secret | For Slack integration |
| `PORT` | Port for the web server | Set by Heroku |

## Health Checks

The application provides a health check endpoint:
```
GET /health
Response: {"status": "healthy", "timestamp": "2024-03-20T14:00:00Z"}
```

## Common Issues

1. **Application Error (H10)**
   - Check logs: `heroku logs --tail`
   - Verify environment variables are set
   - Ensure Procfile is properly configured

2. **Slack Integration Issues**
   - Verify Slack App endpoints are correctly configured
   - Check Slack App permissions and scopes
   - Ensure environment variables are set

3. **Timeout Issues**
   - Heroku has a 30-second timeout for web requests
   - Consider implementing background jobs for long-running tasks

## Monitoring

1. **Heroku Dashboard**
   - Monitor application metrics
   - View resource usage
   - Check error rates

2. **Logging**
   ```bash
   # View recent logs
   heroku logs

   # Real-time log streaming
   heroku logs --tail
   ```

## Scaling

To scale your application on Heroku:
```bash
# Scale to multiple dynos
heroku ps:scale web=2

# Scale back to one dyno
heroku ps:scale web=1
```

## Backup and Recovery

1. **Database Backups** (if using Heroku Postgres)
   ```bash
   # Create backup
   heroku pg:backups:capture

   # Download backup
   heroku pg:backups:download
   ```

2. **Environment Variables Backup**
   ```bash
   # Export current config
   heroku config -s > .env.backup
   ```

## Security Considerations

1. Enable Heroku SSL:
   ```bash
   heroku certs:auto:enable
   ```

2. Configure security headers in FastAPI:
   ```python
   from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
   app.add_middleware(HTTPSRedirectMiddleware)
   ```

## Maintenance

1. **Update Dependencies**
   ```bash
   pip freeze > requirements.txt
   git commit -am "Update dependencies"
   git push heroku main
   ```

2. **Restart Application**
   ```bash
   heroku restart
   ``` 
