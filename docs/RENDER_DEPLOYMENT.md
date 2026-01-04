# Deployment Guide for Render.com

This guide walks you through deploying the AI Hackathon Judge on Render.com with all video analysis features enabled.

## Prerequisites

- A Render.com account (free tier works)
- A Google Gemini API key
- A GitHub personal access token (optional but recommended)

## Step 1: Fork/Clone Repository

1. Fork or clone this repository to your GitHub account
2. Make sure your repository is accessible to Render.com

## Step 2: Create a Web Service on Render.com

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure the service:

### Basic Settings
- **Name**: `ai-hackathon-judge` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main` (or your deployment branch)
- **Root Directory**: Leave empty (use repository root)
- **Runtime**: `Docker`
- **Instance Type**: Free (or paid for better performance)

### Build & Deploy Settings
- **Dockerfile Path**: `./Dockerfile`
- Render will automatically detect and use the Dockerfile

## Step 3: Configure Environment Variables

In the Render dashboard, add the following environment variables:

### Required Variables
```
GEMINI_API_KEY=your_gemini_api_key_here
```
Get your key from: https://makersuite.google.com/app/apikey

### Recommended Variables
```
GITHUB_TOKEN=your_github_token_here
```
Get your token from: https://github.com/settings/tokens
- Required scopes: `repo` (read access)

### Video Analysis Variables (Optional)
```
TRANSCRIPT_CACHE_DIR=/tmp/transcript_cache
TRANSCRIPT_CACHE_EXPIRY=86400
```

### Port Configuration
```
PORT=8000
```
Note: Render automatically sets this, but you can override if needed.

## Step 4: Deploy

1. Click **Create Web Service**
2. Render will:
   - Build the Docker image (frontend + backend)
   - Deploy the application
   - Assign a URL (e.g., `https://ai-hackathon-judge.onrender.com`)

## Step 5: Verify Deployment

1. Wait for the deployment to complete (5-10 minutes for first build)
2. Visit your assigned URL
3. Test the application:
   - Submit a GitHub repository
   - Add a YouTube video URL
   - Verify video analysis works

## Performance Optimization

### Free Tier Considerations
- **Cold Starts**: Free tier services spin down after 15 minutes of inactivity
  - First request after idle may take 30-60 seconds
  - Video caching helps subsequent requests
  
- **Build Time**: First build takes ~5-10 minutes
  - Subsequent builds are faster with Docker layer caching

- **Memory**: Free tier has 512MB RAM
  - Sufficient for most use cases
  - Video transcript caching uses minimal memory

### Upgrade Options
For production use, consider upgrading to:
- **Starter Plan** ($7/month): No cold starts, 512MB RAM
- **Standard Plan** ($25/month): 2GB RAM, better performance

## Troubleshooting

### Build Failures

**Issue**: Docker build fails
```
Solution: Check Dockerfile syntax and ensure all dependencies are listed in requirements.txt
```

**Issue**: Frontend build fails
```
Solution: Verify Node.js version compatibility (requires Node 20+)
```

### Runtime Errors

**Issue**: "GEMINI_API_KEY not found"
```
Solution: Verify environment variable is set in Render dashboard
```

**Issue**: Video transcripts fail
```
Solution: 
1. Check YouTube API is not blocked
2. Verify video has captions enabled
3. Check logs for rate limiting errors
```

**Issue**: High latency on video analysis
```
Solution:
1. Enable transcript caching (should be enabled by default)
2. Use shorter videos for demos
3. Consider upgrading to paid tier
```

### Cache Issues

**Issue**: Transcripts not caching
```
Solution:
1. Verify TRANSCRIPT_CACHE_DIR=/tmp/transcript_cache is set
2. Check logs for cache write errors
3. Ensure /tmp directory has write permissions (it should by default)
```

## Monitoring

### View Logs
1. Go to Render dashboard
2. Select your service
3. Click **Logs** tab
4. Monitor for errors or warnings

### Key Metrics to Watch
- Response time for video analysis
- Cache hit rate (check logs)
- Error rate for transcript fetching
- YouTube API rate limit warnings

## Scaling

### Horizontal Scaling
- Free tier: 1 instance only
- Paid tiers: Configure auto-scaling based on traffic

### Vertical Scaling
- Upgrade instance type for more RAM/CPU
- Useful for handling concurrent requests

## Security Best Practices

1. **Never commit API keys** to git
2. Use Render's environment variables for secrets
3. Rotate API keys periodically
4. Monitor API usage on Google Cloud Console
5. Set up rate limiting if needed

## Custom Domain

1. Go to service settings
2. Click **Custom Domain**
3. Add your domain
4. Configure DNS records as instructed

## Cost Estimation

### Free Tier
- Cost: $0/month
- Limitations: Cold starts, 750 hours/month
- Good for: Testing, personal projects

### Paid Tier (Starter)
- Cost: $7/month
- Benefits: No cold starts, 24/7 uptime
- Good for: Production use, demos

## Support

- **Render Docs**: https://render.com/docs
- **Project Issues**: https://github.com/Daku3011/AI-Hackathon-Judge/issues
- **Video Analysis Docs**: See `docs/VIDEO_ANALYSIS_IMPROVEMENTS.md`

## Next Steps

After successful deployment:
1. Test all features thoroughly
2. Monitor logs for any issues
3. Share your deployment URL
4. Consider setting up a custom domain
5. Enable monitoring/alerting for production use
