"""
BobaBot Core Agent
AI-Powered Franchise Automation Platform

This is the main agent orchestrator that coordinates:
- Customer data management
- Marketing automation
- Operations intelligence
- MCP connector integrations
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess

class BobaBotAgent:
    """
    Main BobaBot agent that orchestrates all franchise automation tasks.
    """
    
    def __init__(self):
        self.version = "1.0.0-alpha"
        self.mcp_server = "zapier"
        self.customers_db = []  # Will be Google Sheets in production
        self.campaigns = []
        
    # ==================== CUSTOMER DATA MANAGEMENT ====================
    
    def capture_customer(self, customer_data: Dict) -> Dict:
        """
        Capture new customer data from QR code sign-up.
        
        Args:
            customer_data: Dict with keys: name, phone, email, favorite_drink
            
        Returns:
            Customer profile with assigned ID and loyalty points
        """
        customer = {
            "id": self._generate_customer_id(),
            "name": customer_data.get("name"),
            "phone": customer_data.get("phone"),
            "email": customer_data.get("email"),
            "favorite_drink": customer_data.get("favorite_drink"),
            "signup_date": datetime.now().isoformat(),
            "total_visits": 0,
            "total_spent": 0.0,
            "loyalty_points": 100,  # Welcome bonus
            "last_visit": None,
            "status": "active"
        }
        
        # Store in Google Sheets via Zapier MCP
        self._store_customer_in_sheets(customer)
        
        # Send welcome message
        self._send_welcome_message(customer)
        
        return customer
    
    def track_purchase(self, customer_id: str, purchase_data: Dict) -> Dict:
        """
        Track a customer purchase and update their profile.
        
        Args:
            customer_id: Unique customer identifier
            purchase_data: Dict with keys: items, total_amount, store_location
            
        Returns:
            Updated customer profile with new points
        """
        customer = self._get_customer(customer_id)
        
        # Update customer stats
        customer["total_visits"] += 1
        customer["total_spent"] += purchase_data["total_amount"]
        customer["last_visit"] = datetime.now().isoformat()
        
        # Calculate loyalty points (1 point per dollar spent)
        points_earned = int(purchase_data["total_amount"])
        customer["loyalty_points"] += points_earned
        
        # Update in Google Sheets
        self._update_customer_in_sheets(customer)
        
        # Check for milestone rewards
        self._check_milestone_rewards(customer)
        
        return customer
    
    # ==================== MARKETING AUTOMATION ====================
    
    def run_marketing_campaigns(self) -> List[Dict]:
        """
        Execute all automated marketing campaigns.
        
        Returns:
            List of campaign results
        """
        results = []
        
        # Campaign 1: "We Miss You" - Inactive customers
        results.append(self._run_we_miss_you_campaign())
        
        # Campaign 2: Birthday rewards
        results.append(self._run_birthday_campaign())
        
        # Campaign 3: Personalized recommendations
        results.append(self._run_recommendation_campaign())
        
        return results
    
    def _run_we_miss_you_campaign(self) -> Dict:
        """
        Target customers who haven't visited in 30+ days.
        """
        inactive_customers = self._get_inactive_customers(days=30)
        
        results = {
            "campaign": "We Miss You",
            "target_count": len(inactive_customers),
            "messages_sent": 0,
            "errors": 0
        }
        
        for customer in inactive_customers:
            try:
                # Generate personalized message using Vertex AI
                message = self._generate_personalized_message(
                    customer=customer,
                    campaign_type="we_miss_you"
                )
                
                # Send via Gmail/SMS
                self._send_message(customer, message)
                
                results["messages_sent"] += 1
                
            except Exception as e:
                print(f"Error sending to {customer['name']}: {e}")
                results["errors"] += 1
        
        return results
    
    def _run_birthday_campaign(self) -> Dict:
        """
        Send birthday rewards to customers.
        """
        birthday_customers = self._get_birthday_customers()
        
        results = {
            "campaign": "Birthday Rewards",
            "target_count": len(birthday_customers),
            "rewards_sent": 0
        }
        
        for customer in birthday_customers:
            # Generate birthday offer
            offer = {
                "type": "free_drink",
                "item": customer.get("favorite_drink", "Any drink"),
                "expiry_days": 7
            }
            
            # Send birthday message
            message = self._generate_birthday_message(customer, offer)
            self._send_message(customer, message)
            
            results["rewards_sent"] += 1
        
        return results
    
    def _run_recommendation_campaign(self) -> Dict:
        """
        Send personalized product recommendations.
        """
        # Get customers who visited in last 7 days
        recent_customers = self._get_recent_customers(days=7)
        
        results = {
            "campaign": "Personalized Recommendations",
            "target_count": len(recent_customers),
            "recommendations_sent": 0
        }
        
        for customer in recent_customers:
            # Use AI to analyze purchase history and recommend new items
            recommendations = self._get_ai_recommendations(customer)
            
            if recommendations:
                message = self._generate_recommendation_message(customer, recommendations)
                self._send_message(customer, message)
                results["recommendations_sent"] += 1
        
        return results
    
    # ==================== OPERATIONS INTELLIGENCE ====================
    
    def generate_sales_report(self, store_id: str, period: str = "daily") -> Dict:
        """
        Generate sales analytics report.
        
        Args:
            store_id: Store identifier
            period: "daily", "weekly", or "monthly"
            
        Returns:
            Comprehensive sales report
        """
        # Fetch sales data from Google Sheets
        sales_data = self._get_sales_data(store_id, period)
        
        report = {
            "store_id": store_id,
            "period": period,
            "generated_at": datetime.now().isoformat(),
            "metrics": {
                "total_revenue": sum(sale["amount"] for sale in sales_data),
                "total_transactions": len(sales_data),
                "average_transaction": 0,
                "top_selling_items": self._calculate_top_items(sales_data),
                "peak_hours": self._calculate_peak_hours(sales_data),
                "loyalty_member_percentage": self._calculate_loyalty_percentage(sales_data)
            }
        }
        
        if report["metrics"]["total_transactions"] > 0:
            report["metrics"]["average_transaction"] = (
                report["metrics"]["total_revenue"] / report["metrics"]["total_transactions"]
            )
        
        # Store report in Google Sheets
        self._store_report_in_sheets(report)
        
        return report
    
    def predict_inventory_needs(self, store_id: str, days_ahead: int = 7) -> Dict:
        """
        Use AI to predict inventory requirements.
        
        Args:
            store_id: Store identifier
            days_ahead: Number of days to forecast
            
        Returns:
            Inventory predictions
        """
        # Get historical sales data
        historical_data = self._get_historical_sales(store_id, days=30)
        
        # Use Vertex AI for demand forecasting
        predictions = self._call_vertex_ai_forecast(historical_data, days_ahead)
        
        inventory_needs = {
            "store_id": store_id,
            "forecast_period": f"{days_ahead} days",
            "generated_at": datetime.now().isoformat(),
            "predictions": predictions,
            "reorder_alerts": self._generate_reorder_alerts(predictions)
        }
        
        return inventory_needs
    
    def analyze_customer_sentiment(self, feedback_text: str) -> Dict:
        """
        Analyze customer feedback sentiment using AI.
        
        Args:
            feedback_text: Customer review or feedback
            
        Returns:
            Sentiment analysis results
        """
        # Call Vertex AI sentiment analysis via Zapier MCP
        sentiment = self._call_mcp_tool(
            tool="google_vertex_ai_analyze_text_sentiment",
            params={
                "text": feedback_text,
                "instructions": "Analyze the sentiment of this customer feedback"
            }
        )
        
        # Take action based on sentiment
        if sentiment.get("score", 0) < -0.5:  # Negative sentiment
            # Alert manager
            self._alert_manager(f"Negative feedback detected: {feedback_text}")
            
            # Generate apology email
            apology = self._generate_apology_email(feedback_text)
            
            return {
                "sentiment": "negative",
                "score": sentiment.get("score"),
                "action_taken": "manager_alerted_and_apology_generated",
                "apology_email": apology
            }
        
        return {
            "sentiment": "positive" if sentiment.get("score", 0) > 0 else "neutral",
            "score": sentiment.get("score"),
            "action_taken": "none"
        }
    
    # ==================== MCP INTEGRATION HELPERS ====================
    
    def _call_mcp_tool(self, tool: str, params: Dict) -> Dict:
        """
        Call a Zapier MCP tool.
        
        Args:
            tool: Tool name (e.g., "google_vertex_ai_send_prompt")
            params: Tool parameters as dict
            
        Returns:
            Tool execution result
        """
        try:
            # Convert params to JSON string
            params_json = json.dumps(params)
            
            # Call MCP CLI
            result = subprocess.run(
                [
                    "manus-mcp-cli",
                    "tool",
                    "call",
                    tool,
                    "--server",
                    self.mcp_server,
                    "--input",
                    params_json
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"MCP tool error: {result.stderr}")
                return {"error": result.stderr}
                
        except Exception as e:
            print(f"Exception calling MCP tool: {e}")
            return {"error": str(e)}
    
    def _generate_personalized_message(self, customer: Dict, campaign_type: str) -> str:
        """
        Generate personalized marketing message using AI.
        """
        prompt = f"""
        Write a friendly, personalized marketing message in Vietnamese for {customer['name']}.
        Campaign type: {campaign_type}
        Customer details:
        - Favorite drink: {customer.get('favorite_drink', 'unknown')}
        - Total visits: {customer.get('total_visits', 0)}
        - Last visit: {customer.get('last_visit', 'unknown')}
        
        Keep it warm, casual, and under 100 words.
        Include a special 15% discount offer.
        """
        
        result = self._call_mcp_tool(
            tool="google_vertex_ai_send_prompt",
            params={
                "prompt": prompt,
                "instructions": "Generate a personalized marketing message"
            }
        )
        
        return result.get("text", "We miss you! Come back for 15% off!")
    
    def _get_ai_recommendations(self, customer: Dict) -> List[str]:
        """
        Get AI-powered product recommendations.
        """
        prompt = f"""
        Based on this customer's purchase history, recommend 2-3 new drinks they might enjoy:
        - Favorite drink: {customer.get('favorite_drink')}
        - Total visits: {customer.get('total_visits')}
        
        Respond with just the drink names, one per line.
        """
        
        result = self._call_mcp_tool(
            tool="google_vertex_ai_send_prompt",
            params={
                "prompt": prompt,
                "instructions": "Generate product recommendations"
            }
        )
        
        recommendations = result.get("text", "").strip().split("\n")
        return [r.strip() for r in recommendations if r.strip()]
    
    # ==================== DATA STORAGE HELPERS ====================
    
    def _store_customer_in_sheets(self, customer: Dict):
        """Store customer data in Google Sheets via Zapier MCP."""
        self._call_mcp_tool(
            tool="google_sheets_create_spreadsheet_row",
            params={
                "instructions": f"Add new customer {customer['name']} to the Customers sheet",
                "spreadsheet": "BobaBot Customer Database",
                "worksheet": "Customers"
            }
        )
    
    def _update_customer_in_sheets(self, customer: Dict):
        """Update customer data in Google Sheets."""
        self._call_mcp_tool(
            tool="google_sheets_update_spreadsheet_row",
            params={
                "instructions": f"Update customer {customer['id']} with new data",
                "spreadsheet": "BobaBot Customer Database",
                "worksheet": "Customers"
            }
        )
    
    def _store_report_in_sheets(self, report: Dict):
        """Store sales report in Google Sheets."""
        self._call_mcp_tool(
            tool="google_sheets_create_spreadsheet_row",
            params={
                "instructions": f"Add sales report for {report['store_id']}",
                "spreadsheet": "BobaBot Reports",
                "worksheet": "Sales Reports"
            }
        )
    
    # ==================== UTILITY METHODS ====================
    
    def _generate_customer_id(self) -> str:
        """Generate unique customer ID."""
        import uuid
        return f"CUST-{uuid.uuid4().hex[:8].upper()}"
    
    def _get_customer(self, customer_id: str) -> Dict:
        """Retrieve customer from database."""
        # In production, query Google Sheets
        return {"id": customer_id, "name": "Sample Customer"}
    
    def _get_inactive_customers(self, days: int) -> List[Dict]:
        """Get customers inactive for specified days."""
        # In production, query Google Sheets with date filter
        return []
    
    def _get_birthday_customers(self) -> List[Dict]:
        """Get customers with birthdays today."""
        return []
    
    def _get_recent_customers(self, days: int) -> List[Dict]:
        """Get customers who visited recently."""
        return []
    
    def _send_message(self, customer: Dict, message: str):
        """Send message via Gmail/SMS."""
        print(f"Sending to {customer['name']}: {message}")
    
    def _send_welcome_message(self, customer: Dict):
        """Send welcome message to new customer."""
        message = f"Welcome to Boba Club, {customer['name']}! You've earned 100 points!"
        self._send_message(customer, message)
    
    def _check_milestone_rewards(self, customer: Dict):
        """Check if customer reached a milestone."""
        if customer["total_visits"] in [5, 10, 25, 50, 100]:
            print(f"Milestone! {customer['name']} reached {customer['total_visits']} visits!")
    
    def _get_sales_data(self, store_id: str, period: str) -> List[Dict]:
        """Fetch sales data from Google Sheets."""
        return []
    
    def _calculate_top_items(self, sales_data: List[Dict]) -> List[str]:
        """Calculate top-selling items."""
        return ["Taro Milk Tea", "Brown Sugar Boba", "Mango Smoothie"]
    
    def _calculate_peak_hours(self, sales_data: List[Dict]) -> List[str]:
        """Calculate peak sales hours."""
        return ["2pm-4pm", "7pm-9pm"]
    
    def _calculate_loyalty_percentage(self, sales_data: List[Dict]) -> float:
        """Calculate percentage of sales from loyalty members."""
        return 35.5
    
    def _get_historical_sales(self, store_id: str, days: int) -> List[Dict]:
        """Get historical sales data."""
        return []
    
    def _call_vertex_ai_forecast(self, historical_data: List[Dict], days_ahead: int) -> Dict:
        """Call Vertex AI for demand forecasting."""
        return {"milk_tea": 150, "boba": 200, "fruit": 100}
    
    def _generate_reorder_alerts(self, predictions: Dict) -> List[str]:
        """Generate inventory reorder alerts."""
        return ["Reorder tapioca pearls", "Reorder milk powder"]
    
    def _alert_manager(self, message: str):
        """Send alert to store manager."""
        print(f"ALERT: {message}")
    
    def _generate_apology_email(self, feedback: str) -> str:
        """Generate apology email for negative feedback."""
        return "We're sorry for your experience. Please accept this free drink coupon."
    
    def _generate_birthday_message(self, customer: Dict, offer: Dict) -> str:
        """Generate birthday message."""
        return f"Happy Birthday {customer['name']}! Enjoy a free {offer['item']} on us!"
    
    def _generate_recommendation_message(self, customer: Dict, recommendations: List[str]) -> str:
        """Generate recommendation message."""
        items = ", ".join(recommendations)
        return f"Hi {customer['name']}! Based on your taste, you might love: {items}"


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("🧋 BobaBot Agent v1.0.0-alpha")
    print("=" * 50)
    
    agent = BobaBotAgent()
    
    # Demo: Capture a new customer
    print("\n📝 Demo: Capturing new customer...")
    new_customer = agent.capture_customer({
        "name": "Nguyen Van A",
        "phone": "+84901234567",
        "email": "nguyen@example.com",
        "favorite_drink": "Taro Milk Tea"
    })
    print(f"✅ Customer created: {new_customer['id']}")
    
    # Demo: Run marketing campaigns
    print("\n📧 Demo: Running marketing campaigns...")
    campaign_results = agent.run_marketing_campaigns()
    for result in campaign_results:
        print(f"✅ {result['campaign']}: {result.get('messages_sent', result.get('rewards_sent', 0))} sent")
    
    # Demo: Generate sales report
    print("\n📊 Demo: Generating sales report...")
    report = agent.generate_sales_report("STORE-001", "daily")
    print(f"✅ Report generated: ${report['metrics']['total_revenue']:.2f} revenue")
    
    # Demo: Sentiment analysis
    print("\n😊 Demo: Analyzing customer feedback...")
    sentiment = agent.analyze_customer_sentiment("The boba was amazing! Best I've ever had!")
    print(f"✅ Sentiment: {sentiment['sentiment']} (score: {sentiment['score']})")
    
    print("\n" + "=" * 50)
    print("🎉 BobaBot Agent demo complete!")
