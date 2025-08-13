"""Test Google Gemini API integration"""
import asyncio
import os
from dotenv import load_dotenv
from src.a2a.ai_service import ai_service

load_dotenv()

async def test_gemini_api():
    """Test Google Gemini API"""
    
    print("[INFO] Testing Google Gemini 2.0 Flash API Integration...")
    print(f"[CONFIG] Provider: {ai_service.provider}")
    print(f"[CONFIG] AI Enabled: {ai_service.enable_ai}")
    print(f"[CONFIG] Google API Key: {'Configured' if ai_service.google_key else 'Missing'}")
    
    if not ai_service.google_key:
        print("\n[ERROR] Google AI API Key not found!")
        print("[SETUP] Hãy cập nhật file .env với:")
        print("[SETUP] GOOGLE_AI_API_KEY=your-api-key-here")
        print("[SETUP] Lấy key tại: https://aistudio.google.com/app/apikey")
        return
    
    print(f"Google API Key (first 10 chars): {ai_service.google_key[:10]}...")
    
    # Test mission
    test_mission = """
    Create a comprehensive e-commerce platform that allows users to browse products, 
    add items to cart, process payments via Stripe and PayPal, and manage orders. 
    The platform should include an admin panel for inventory management, user management, 
    and real-time analytics dashboard. The system needs to be scalable to handle 
    10,000 concurrent users, secure with OAuth2 authentication, and mobile-responsive 
    with PWA capabilities.
    """
    
    print("\n[TEST] Testing mission analysis with Gemini...")
    print(f"[INPUT] Mission: {test_mission[:100]}...")
    
    try:
        # Test AI analysis
        result = await ai_service.analyze_project_requirements(test_mission)
        
        print("\n[SUCCESS] Gemini Analysis Successful!")
        print("="*60)
        print(f"[RESULT] Complexity: {result.get('complexity', 'N/A').upper()}")
        print(f"[RESULT] Estimated Weeks: {result.get('estimated_weeks', 'N/A')}")
        print(f"[RESULT] Project Type: {result.get('project_type', 'N/A').upper()}")
        print(f"[RESULT] Team Size: {result.get('recommended_team_size', 'N/A')} members")
        print(f"[RESULT] Budget: {result.get('budget_category', 'N/A').upper()}")
        
        if result.get('key_technologies'):
            print(f"[TECH] Technologies: {', '.join(result['key_technologies'])}")
        
        if result.get('required_skills'):
            print(f"[SKILLS] Skills: {', '.join(result['required_skills'])}")
        
        if result.get('risk_factors'):
            print(f"[RISKS] Risks: {', '.join(result['risk_factors'])}")
        
        print("\n[INFO] Google Gemini integration is working perfectly!")
        
        # Test milestone generation
        print("\n[TEST] Testing milestone generation...")
        milestones = await ai_service.generate_smart_milestones(test_mission, result)
        
        if milestones:
            print(f"[SUCCESS] Generated {len(milestones)} smart milestones:")
            for i, milestone in enumerate(milestones, 1):
                print(f"  [MILESTONE] {i}. {milestone.get('name', 'Unnamed')} ({milestone.get('duration_weeks', 'N/A')} weeks)")
        
        print("\n[READY] Ready to use AI-powered A2A system!")
        
    except Exception as e:
        print(f"\n[ERROR] Error testing Gemini API: {e}")
        print("[DEBUG] Possible issues:")
        print("[DEBUG] 1. Invalid API key")
        print("[DEBUG] 2. API quota exceeded") 
        print("[DEBUG] 3. Network connectivity")
        print("[DEBUG] 4. Model name incorrect")
        
        print(f"\n[CONFIG] Current configuration:")
        print(f"[CONFIG] - Model: {os.getenv('GOOGLE_MODEL', 'gemini-2.0-flash-exp')}")
        print(f"[CONFIG] - Max Tokens: {os.getenv('GOOGLE_MAX_TOKENS', '8000')}")
        print(f"[CONFIG] - Temperature: {os.getenv('GOOGLE_TEMPERATURE', '0.7')}")

if __name__ == "__main__":
    asyncio.run(test_gemini_api())
