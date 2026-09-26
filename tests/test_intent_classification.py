"""
Unit tests for VyaparMitra Phase 5 Intent Classification.
"""

import pytest
from src.copilot.intent.classifier import IntentClassifier, classify_intent
from src.copilot.schemas import Intent


def test_classify_sales_summary():
    classifier = IntentClassifier()
    assert classifier.classify("Kal kitni bikri hui thi?") == Intent.SALES_SUMMARY
    assert classify_intent("Pichle hafte ki total revenue batao") == Intent.SALES_SUMMARY
    assert classify_intent("What was yesterday's revenue?") == Intent.SALES_SUMMARY


def test_classify_sales_forecast():
    assert classify_intent("Agle 7 dino mein sales kitni hogi?") == Intent.SALES_FORECAST
    assert classify_intent("What is the next week sales forecast?") == Intent.SALES_FORECAST
    assert classify_intent("भविष्य में बिक्री का क्या अनुमान है?") == Intent.SALES_FORECAST


def test_classify_inventory():
    assert classify_intent("Kaunsa product restock karna chahiye?") == Intent.INVENTORY_RECOMMENDATION
    assert classify_intent("Which items are out of stock?") == Intent.INVENTORY_RECOMMENDATION
    assert classify_intent("माल खत्म होने वाला है") == Intent.INVENTORY_RECOMMENDATION


def test_classify_customer_risk():
    assert classify_intent("Kaunse grahak aana band ho gaye hain?") == Intent.CUSTOMER_RISK
    assert classify_intent("Who are the churn risk customers?") == Intent.CUSTOMER_RISK
    assert classify_intent("Kaunse customers dukan chhod rahe hain?") == Intent.CUSTOMER_RISK


def test_classify_daily_action_plan():
    assert classify_intent("Aaj mujhe kya karna chahiye?") == Intent.DAILY_ACTION_PLAN
    assert classify_intent("What is today's daily action plan?") == Intent.DAILY_ACTION_PLAN
    assert classify_intent("आज मुझे क्या काम करना चाहिए?") == Intent.DAILY_ACTION_PLAN


def test_classify_out_of_domain():
    assert classify_intent("Who won the cricket match yesterday?") == Intent.OUT_OF_DOMAIN
    assert classify_intent("Bharat ka prime minister kaun hai?") == Intent.OUT_OF_DOMAIN


def test_classify_recommendation_explanation():
    assert classify_intent("Ye recommendation kyun di?") == Intent.RECOMMENDATION_EXPLANATION
    assert classify_intent("Why did you recommend this restock?") == Intent.RECOMMENDATION_EXPLANATION
