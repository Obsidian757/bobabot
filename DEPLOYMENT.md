# 🚀 BobaBot Deployment Guide

Complete guide to deploying BobaBot to production.

---

## 📋 Prerequisites

### Required Accounts
- [ ] Google Account (for Sheets, Vertex AI)
- [ ] Zapier Account (Professional plan recommended)
- [ ] Cloudflare Account (for Workers deployment)
- [ ] GitHub Account (for version control)
- [ ] Canva Pro Account (for design automation)

### Required MCP Connectors
- [ ] Zapier MCP configured
- [ ] Google Sheets connected to Zapier
- [ ] Vertex AI enabled in Zapier
- [ ] Canva connected to Zapier
- [ ] Gmail connected to Zapier

---

## 🛠️ Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/Obsidian757/bobabot.git
cd bobabot
```

### Step 2: Install Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file:

```bash
# MCP Configuration
MCP_SERVER=zapier

# Google Sheets
GOOGLE_SHEETS_CUSTOMER_DB=BobaBot Customer Database
GOOGLE_SHEETS_REPORTS=BobaBot Reports

# Store Configuration
STORE_ID=STORE-001
STORE_NAME=Boba Tea Hanoi Central
STORE_LOCATION=Hanoi, Vietnam

# Campaign Settings
INACTIVE_DAYS_THRESHOLD=30
LOYALTY_POINTS_PER_DOLLAR=1
WELCOME_BONUS_POINTS=100

# AI Model Selection
PRIMARY_AI_MODEL=vertex_ai
SECONDARY_AI_MODEL=openrouter_claude

# Notification Settings
MANAGER_EMAIL=manager@bobatea.vn
MANAGER_PHONE=+84901234567
```

### Step 4: Set Up Google Sheets Database

Create two Google Sheets:

#### Sheet 1: "BobaBot Customer Database"

**Worksheet: "Customers"**

| Column | Type | Description |
|--------|------|-------------|
| customer_id | Text | Unique ID (CUST-XXXXXXXX) |
| name | Text | Customer name |
| phone | Text | Phone number |
| email | Text | Email address |
| favorite_drink | Text | Preferred drink |
| signup_date | Date | Registration date |
| total_visits | Number | Visit count |
| total_spent | Number | Total $ spent |
| loyalty_points | Number | Current points |
| last_visit | Date | Last visit date |
| status | Text | active/inactive |

#### Sheet 2: "BobaBot Reports"

**Worksheet: "Sales Reports"**

| Column | Type | Description |
|--------|------|-------------|
| report_id | Text | Unique ID |
| store_id | Text | Store identifier |
| period | Text | daily/weekly/monthly |
| generated_at | DateTime | Report timestamp |
| total_revenue | Number | Total revenue |
| total_transactions | Number | Transaction count |
| average_transaction | Number | Avg transaction value |
| loyalty_percentage | Number | % from loyalty members |

### Step 5: Configure Zapier Integrations

#### Integration 1: Customer Sign-up Webhook

1. Create a Zap: "Webhook → Google Sheets"
2. Trigger: Catch Hook (for QR code sign-ups)
3. Action: Create Spreadsheet Row in "Customers"
4. Test with sample data

#### Integration 2: Vertex AI Sentiment Analysis

1. Create a Zap: "Google Sheets → Vertex AI → Gmail"
2. Trigger: New Row in "Customer Feedback"
3. Action 1: Analyze Text Sentiment (Vertex AI)
4. Action 2: Send Email if sentiment < -0.5

#### Integration 3: Canva Marketing Materials

1. Create a Zap: "Google Sheets → Canva → Google Drive"
2. Trigger: New Row in "Marketing Campaigns"
3. Action 1: Create Design (Canva)
4. Action 2: Save to Drive

### Step 6: Test the Agent

```bash
python3.11 agent.py
```

Expected output:
```
🧋 BobaBot Agent v1.0.0-alpha
==================================================
📝 Demo: Capturing new customer...
✅ Customer created: CUST-XXXXXXXX
📧 Demo: Running marketing campaigns...
✅ We Miss You: 0 sent
✅ Birthday Rewards: 0 sent
📊 Demo: Generating sales report...
✅ Report generated: $0.00 revenue
==================================================
🎉 BobaBot Agent demo complete!
```

---

## 🌐 Deploy to Cloudflare Workers

### Step 1: Install Wrangler CLI

```bash
npm install -g wrangler
wrangler login
```

### Step 2: Create Worker Project

```bash
wrangler init bobabot-worker
cd bobabot-worker
```

### Step 3: Configure wrangler.toml

```toml
name = "bobabot-worker"
main = "src/index.js"
compatibility_date = "2025-11-14"

[env.production]
name = "bobabot-production"
route = "bobabot.yourdomain.com/*"

[[d1_databases]]
binding = "DB"
database_name = "bobabot-db"
database_id = "your-database-id"

[[kv_namespaces]]
binding = "CACHE"
id = "your-kv-namespace-id"
```

### Step 4: Deploy

```bash
wrangler deploy
```

---

## 📱 Mobile Web App Setup

### Frontend Structure

```
bobabot-frontend/
├── index.html          # Landing page
├── signup.html         # Customer registration
├── loyalty.html        # Loyalty dashboard
├── menu.html           # Product menu
├── css/
│   └── styles.css      # Tailwind CSS
├── js/
│   ├── app.js          # Main app logic
│   ├── qr-scanner.js   # QR code scanner
│   └── api.js          # API client
└── assets/
    ├── logo.png
    └── qr-code.png
```

### QR Code Integration

```html
<!-- signup.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Join Boba Club</title>
    <script src="https://unpkg.com/html5-qrcode"></script>
</head>
<body>
    <div id="qr-reader"></div>
    <script>
        const html5QrCode = new Html5Qrcode("qr-reader");
        html5QrCode.start(
            { facingMode: "environment" },
            { fps: 10, qrbox: 250 },
            (decodedText) => {
                // Send to BobaBot API
                fetch('/api/signup', {
                    method: 'POST',
                    body: JSON.stringify({ qr_code: decodedText })
                });
            }
        );
    </script>
</body>
</html>
```

---

## 🔄 Automated Campaign Scheduling

### Daily Campaign Execution

Create a cron job or use Cloudflare Workers Cron Triggers:

```javascript
// wrangler.toml
[triggers]
crons = ["0 9 * * *"]  // Run at 9 AM daily

// src/index.js
export default {
    async scheduled(event, env, ctx) {
        // Run marketing campaigns
        const agent = new BobaBotAgent();
        await agent.run_marketing_campaigns();
    }
}
```

---

## 📊 Monitoring & Analytics

### Key Metrics to Track

1. **Customer Metrics**
   - Daily sign-ups
   - Loyalty program adoption rate
   - Average customer lifetime value

2. **Campaign Metrics**
   - Email open rates
   - Offer redemption rates
   - Campaign ROI

3. **Operational Metrics**
   - System uptime
   - API response times
   - Error rates

### Recommended Tools

- **Cloudflare Analytics**: Built-in metrics
- **Google Sheets**: Custom dashboards
- **Notion**: Operations manual and logs

---

## 🔐 Security Best Practices

1. **API Keys**: Store in Cloudflare Workers secrets
2. **Customer Data**: Encrypt PII in Google Sheets
3. **Access Control**: Limit Zapier integration permissions
4. **Audit Logs**: Track all customer data access

---

## 🐛 Troubleshooting

### Issue: MCP Tool Calls Failing

**Solution**: Verify Zapier authentication
```bash
manus-mcp-cli tool list --server zapier
```

### Issue: Google Sheets Not Updating

**Solution**: Check Zapier Zap status and test manually

### Issue: Vertex AI Errors

**Solution**: Verify Google Cloud project has Vertex AI API enabled

---

## 📈 Scaling to 100+ Franchises

### Database Migration

When scaling beyond pilot:
1. Migrate from Google Sheets to Cloudflare D1 (SQL)
2. Implement proper database indexing
3. Set up automated backups

### Multi-Store Management

```python
# Add store_id to all operations
agent = BobaBotAgent(store_id="STORE-042")
agent.run_marketing_campaigns()
```

### Franchise Dashboard

Create a central dashboard for franchise owners:
- Real-time sales across all locations
- Customer analytics
- Campaign performance
- Inventory alerts

---

## 💰 Cost Optimization

### Estimated Monthly Costs (100 Stores)

| Service | Cost | Notes |
|---------|------|-------|
| Cloudflare Workers | $25 | Includes D1, KV, R2 |
| Vertex AI | $150 | Optimized with OpenRouter |
| Zapier Professional | $50 | Unlimited Zaps |
| Canva Pro | $13 | Single account |
| **Total** | **$238/month** | **$2.38 per store** |

### Cost Reduction Tips

1. Use OpenRouter for simple tasks (cheaper than Vertex AI)
2. Cache frequently used AI responses
3. Batch process marketing campaigns
4. Use Cloudflare's free tier maximally

---

## 🎓 Training Materials

### For Store Staff

1. **QR Code Sign-up Process** (2-minute video)
2. **Processing Loyalty Transactions** (3-minute video)
3. **Handling Customer Questions** (5-minute video)

### For Franchise Owners

1. **Dashboard Overview** (10-minute video)
2. **Reading Analytics Reports** (15-minute video)
3. **Customizing Marketing Campaigns** (20-minute video)

**Generate training videos using HeyGen MCP integration!**

---

## 📞 Support

For technical support or questions:
- GitHub Issues: https://github.com/Obsidian757/bobabot/issues
- Email: support@12thhouseai.com

---

**Version**: 1.0.0-alpha
**Last Updated**: November 14, 2025
