# Getting Started with AI Features

## Quick Setup Guide

### Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key (it will look like: `AIzaSyD1234567890abcdefghijk...`)

### Step 2: Configure Your API Key

1. Open the `.env` file in your ResourcePro project root
2. Find this line:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
3. Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSyD1234567890abcdefghijk...
   ```
4. Save the file

### Step 3: Test the Setup

Run the test command to verify everything is working:

```bash
python manage.py test_ai_features --feature skills
```

If successful, you should see AI-powered skill recommendations!

### Step 4: Start Using AI Features

1. Start the Django server:
   ```bash
   python manage.py runserver
   ```

2. Visit the AI Analytics Dashboard:
   ```
   http://localhost:8000/analytics/ai/
   ```

3. Try out the three AI features:
   - **Smart Skill Recommendations**: Get AI insights on team skill development
   - **Resource Allocation Advisor**: Get optimal resource suggestions for tasks  
   - **AI-Enhanced Forecasting**: Generate business-context-aware resource forecasts

## API Endpoints for Integration

### Skill Recommendations
```http
GET /analytics/ai/skill-recommendations/
GET /analytics/ai/skill-recommendations/?refresh=true
```

### Resource Allocation Suggestions  
```http
GET /analytics/ai/resource-allocation/{task_id}/
GET /analytics/ai/resource-allocation/{task_id}/?refresh=true
```

### Enhanced Forecasting
```http
GET /analytics/ai/enhanced-forecasts/?days_ahead=30
POST /analytics/ai/enhanced-forecasts/
Content-Type: application/json
{
    "business_context": "Launching new product in Q2"
}
```

### Strategic Recommendations
```http
POST /analytics/ai/strategic-recommendations/
Content-Type: application/json
{
    "enhanced_forecasts": { ... }
}
```

## Troubleshooting

### "Gemini AI not available"
- Check that your API key is correctly set in the `.env` file
- Verify the API key is valid at [Google AI Studio](https://aistudio.google.com/app/apikey)
- Ensure you have API quota remaining

### "No recommendations generated"  
- Make sure you have:
  - Resources with assigned skills
  - Projects with tasks that require specific skills
  - Some historical data (time entries, assignments)

### Import Errors
- Run: `pip install -r requirements.txt` to install all dependencies
- Restart the Django server after installing new packages

## Cost Management

- Recommendations are cached (24h for skills, 4h for allocation)
- Use `refresh=false` (default) to avoid unnecessary API calls
- Each AI feature call uses ~1000-3000 tokens
- Gemini 1.5 Flash pricing: ~$0.075 per 1M input tokens

## Need Help?

Check the full documentation in:
- `AI_FEATURES_README.md` - Detailed technical documentation
- `AI_IMPLEMENTATION_SUMMARY.md` - Implementation overview
