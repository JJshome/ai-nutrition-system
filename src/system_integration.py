#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System Integration for AI-based Real-time Personalized Nutritional Supplement Recommendation and Management System

This module integrates all components of the system and provides a unified interface.

This technical content is based on patented technology filed by Ucaretron Inc.
All rights reserved by Ucaretron Inc.
"""

import json
import time
import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AI-Nutrition-System")


class NutritionSystem:
    """Main class integrating all components of the AI-based nutrition system"""
    
    def __init__(self):
        """Initialize the nutrition system"""
        # Import modules only when needed to avoid circular imports
        from src.data_collection.sensor_manager import SensorManager
        from src.ai_analysis.nutrition_analyzer import NutritionAnalyzer
        from src.recommendation.supplement_recommender import SupplementRecommender
        from src.management.intake_manager import IntakeManager
        from src.security.data_security import DataSecurity
        from src.ui.user_interface_manager import UserInterfaceManager
        
        logger.info("Initializing AI-based Nutrition System")
        
        # Initialize components
        self.sensor_manager = SensorManager()
        self.nutrition_analyzer = NutritionAnalyzer()
        self.supplement_recommender = SupplementRecommender()
        self.intake_manager = IntakeManager()
        self.data_security = DataSecurity()
        self.ui_manager = UserInterfaceManager()
        
        # System state
        self.is_running = False
        self.active_users = {}
        
        logger.info("System initialized successfully")
    
    def start(self):
        """Start the nutrition system"""
        if self.is_running:
            logger.warning("System is already running")
            return False
        
        logger.info("Starting AI-based Nutrition System")
        
        # Start all components
        self.sensor_manager.start()
        self.nutrition_analyzer.start()
        self.supplement_recommender.start()
        self.intake_manager.start()
        self.data_security.start()
        self.ui_manager.start()
        
        self.is_running = True
        logger.info("System started successfully")
        return True
    
    def stop(self):
        """Stop the nutrition system"""
        if not self.is_running:
            logger.warning("System is not running")
            return False
        
        logger.info("Stopping AI-based Nutrition System")
        
        # Stop all components in reverse order
        self.ui_manager.stop()
        self.data_security.stop()
        self.intake_manager.stop()
        self.supplement_recommender.stop()
        self.nutrition_analyzer.stop()
        self.sensor_manager.stop()
        
        self.is_running = False
        logger.info("System stopped successfully")
        return True
    
    def register_user(self, user_id, user_data):
        """Register a new user
        
        Args:
            user_id (str): User's unique identifier
            user_data (dict): User's registration data
            
        Returns:
            bool: True if registration was successful
        """
        if user_id in self.active_users:
            logger.warning(f"User {user_id} is already registered")
            return False
        
        logger.info(f"Registering user {user_id}")
        
        # Encrypt sensitive user data
        encrypted_user_data = self.data_security.encrypt_user_data(user_data)
        
        # Create user profile
        user_profile = {
            "id": user_id,
            "encrypted_data": encrypted_user_data,
            "registered_at": datetime.datetime.now().isoformat(),
            "last_activity": datetime.datetime.now().isoformat(),
            "components": {}
        }
        
        # Initialize user in each component
        user_profile["components"]["sensor"] = self.sensor_manager.register_user(user_id, user_data)
        user_profile["components"]["analyzer"] = self.nutrition_analyzer.register_user(user_id, user_data)
        user_profile["components"]["recommender"] = self.supplement_recommender.register_user(user_id, user_data)
        user_profile["components"]["intake_manager"] = self.intake_manager.register_user(user_id, user_data)
        user_profile["components"]["ui"] = self.ui_manager.register_user(user_id, user_data)
        
        # Add user to active users
        self.active_users[user_id] = user_profile
        
        logger.info(f"User {user_id} registered successfully")
        return True
    
    def process_sensor_data(self, user_id, sensor_data):
        """Process incoming sensor data
        
        Args:
            user_id (str): User's unique identifier
            sensor_data (dict): Sensor data to process
            
        Returns:
            dict: Processing result
        """
        if user_id not in self.active_users:
            logger.warning(f"User {user_id} is not registered")
            return {"status": "error", "message": "User not registered"}
        
        logger.info(f"Processing sensor data for user {user_id}")
        
        # Update last activity
        self.active_users[user_id]["last_activity"] = datetime.datetime.now().isoformat()
        
        # Process the data through the pipeline
        # 1. Validate and preprocess sensor data
        validated_data = self.sensor_manager.process_data(user_id, sensor_data)
        
        # 2. Analyze the data
        analysis_result = self.nutrition_analyzer.analyze(user_id, validated_data)
        
        # 3. Update recommendations if needed
        if analysis_result.get("update_recommendation", False):
            self.update_recommendations(user_id, analysis_result)
        
        # 4. Check for health alerts
        alerts = analysis_result.get("alerts", [])
        for alert in alerts:
            self.handle_health_alert(user_id, alert)
        
        # 5. Update UI
        self.ui_manager.update_health_data(user_id, analysis_result)
        
        logger.info(f"Sensor data processing completed for user {user_id}")
        return {"status": "success", "result": analysis_result}
    
    def update_recommendations(self, user_id, analysis_result):
        """Update supplement recommendations based on analysis results
        
        Args:
            user_id (str): User's unique identifier
            analysis_result (dict): Analysis results
            
        Returns:
            dict: Updated recommendations
        """
        if user_id not in self.active_users:
            logger.warning(f"User {user_id} is not registered")
            return {"status": "error", "message": "User not registered"}
        
        logger.info(f"Updating recommendations for user {user_id}")
        
        # Generate new recommendations
        recommendations = self.supplement_recommender.recommend(user_id, analysis_result)
        
        # Update intake management
        self.intake_manager.update_schedule(user_id, recommendations)
        
        # Update UI
        self.ui_manager.update_supplement_data(user_id, recommendations)
        
        logger.info(f"Recommendations updated for user {user_id}")
        return {"status": "success", "recommendations": recommendations}
    
    def record_supplement_intake(self, user_id, supplement_id, intake_time=None):
        """Record a supplement intake
        
        Args:
            user_id (str): User's unique identifier
            supplement_id (str): Supplement ID
            intake_time (datetime, optional): Time of intake
            
        Returns:
            dict: Intake recording result
        """
        if user_id not in self.active_users:
            logger.warning(f"User {user_id} is not registered")
            return {"status": "error", "message": "User not registered"}
        
        logger.info(f"Recording supplement intake for user {user_id}")
        
        # Update last activity
        self.active_users[user_id]["last_activity"] = datetime.datetime.now().isoformat()
        
        # Record the intake
        result = self.intake_manager.record_intake(user_id, supplement_id, intake_time)
        
        # Update UI
        self.ui_manager.update_intake_status(user_id, result)
        
        logger.info(f"Supplement intake recorded for user {user_id}")
        return {"status": "success", "result": result}
    
    def handle_health_alert(self, user_id, alert):
        """Handle a health alert
        
        Args:
            user_id (str): User's unique identifier
            alert (dict): Health alert data
            
        Returns:
            dict: Alert handling result
        """
        logger.warning(f"Health alert for user {user_id}: {alert.get('message')}")
        
        # Determine alert severity
        severity = alert.get("severity", "medium")
        
        # Take action based on severity
        if severity == "high":
            # Immediate notification
            self.ui_manager.send_urgent_notification(user_id, alert)
            
            # If configured, notify healthcare provider
            if self.active_users[user_id].get("notify_healthcare_provider", False):
                self._notify_healthcare_provider(user_id, alert)
        
        elif severity == "medium":
            # Standard notification
            self.ui_manager.send_notification(user_id, alert)
        
        else:  # low
            # Add to report but don't notify
            self.ui_manager.add_to_health_report(user_id, alert)
        
        logger.info(f"Health alert handled for user {user_id}")
        return {"status": "success", "alert_handled": True}
    
    def _notify_healthcare_provider(self, user_id, alert):
        """Notify healthcare provider about a health alert
        
        Args:
            user_id (str): User's unique identifier
            alert (dict): Health alert data
        """
        # In a real implementation, this would send a notification to the healthcare provider
        # This is a simplified demonstration
        logger.info(f"Notifying healthcare provider about alert for user {user_id}")
    
    def get_user_dashboard(self, user_id):
        """Get the user's dashboard data
        
        Args:
            user_id (str): User's unique identifier
            
        Returns:
            dict: Dashboard data
        """
        if user_id not in self.active_users:
            logger.warning(f"User {user_id} is not registered")
            return {"status": "error", "message": "User not registered"}
        
        logger.info(f"Getting dashboard for user {user_id}")
        
        # Update last activity
        self.active_users[user_id]["last_activity"] = datetime.datetime.now().isoformat()
        
        # Get health data
        health_data = self.nutrition_analyzer.get_health_data(user_id)
        
        # Get supplement data
        supplement_data = self.intake_manager.get_schedule(user_id)
        
        # Get compliance data
        compliance_data = self.intake_manager.get_compliance_rate(user_id)
        
        # Combine data
        dashboard_data = {
            "health_data": health_data,
            "supplement_data": supplement_data,
            "compliance_data": compliance_data
        }
        
        logger.info(f"Dashboard data retrieved for user {user_id}")
        return {"status": "success", "dashboard": dashboard_data}
    
    def get_health_report(self, user_id, report_type="monthly"):
        """Get the user's health report
        
        Args:
            user_id (str): User's unique identifier
            report_type (str): Type of report (daily, weekly, monthly)
            
        Returns:
            dict: Health report
        """
        if user_id not in self.active_users:
            logger.warning(f"User {user_id} is not registered")
            return {"status": "error", "message": "User not registered"}
        
        logger.info(f"Generating {report_type} health report for user {user_id}")
        
        # Update last activity
        self.active_users[user_id]["last_activity"] = datetime.datetime.now().isoformat()
        
        # Get date range for the report
        end_date = datetime.datetime.now().date()
        if report_type == "daily":
            start_date = end_date
        elif report_type == "weekly":
            start_date = end_date - datetime.timedelta(days=7)
        elif report_type == "monthly":
            start_date = end_date - datetime.timedelta(days=30)
        else:
            return {"status": "error", "message": f"Invalid report type: {report_type}"}
        
        # Get health data for the period
        health_data = self.nutrition_analyzer.get_health_data(user_id, start_date, end_date)
        
        # Get supplement data for the period
        supplement_data = self.intake_manager.get_intake_history(user_id, start_date, end_date)
        
        # Get compliance data for the period
        compliance_data = self.intake_manager.get_compliance_rate(user_id, start_date, end_date)
        
        # Get health trends
        trends = self.nutrition_analyzer.get_trends(user_id, start_date, end_date)
        
        # Create the report
        report = {
            "user_id": user_id,
            "report_type": report_type,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "generated_at": datetime.datetime.now().isoformat(),
            "health_data": health_data,
            "supplement_data": supplement_data,
            "compliance_data": compliance_data,
            "trends": trends
        }
        
        logger.info(f"{report_type.capitalize()} health report generated for user {user_id}")
        return {"status": "success", "report": report}
    
    def get_user_profile(self, user_id):
        """Get the user's profile data
        
        Args:
            user_id (str): User's unique identifier
            
        Returns:
            dict: User profile
        """
        if user_id not in self.active_users:
            logger.warning(f"User {user_id} is not registered")
            return {"status": "error", "message": "User not registered"}
        
        logger.info(f"Getting profile for user {user_id}")
        
        # Update last activity
        self.active_users[user_id]["last_activity"] = datetime.datetime.now().isoformat()
        
        # Get encrypted user data
        encrypted_user_data = self.active_users[user_id]["encrypted_data"]
        
        # Decrypt user data
        user_data = self.data_security.decrypt_user_data(encrypted_user_data)
        
        # Remove sensitive information
        if "password" in user_data:
            del user_data["password"]
        
        # Add registration and activity information
        user_data["registered_at"] = self.active_users[user_id]["registered_at"]
        user_data["last_activity"] = self.active_users[user_id]["last_activity"]
        
        logger.info(f"Profile data retrieved for user {user_id}")
        return {"status": "success", "profile": user_data}
    
    def update_user_profile(self, user_id, update_data):
        """Update the user's profile data
        
        Args:
            user_id (str): User's unique identifier
            update_data (dict): Data to update
            
        Returns:
            dict: Update result
        """
        if user_id not in self.active_users:
            logger.warning(f"User {user_id} is not registered")
            return {"status": "error", "message": "User not registered"}
        
        logger.info(f"Updating profile for user {user_id}")
        
        # Update last activity
        self.active_users[user_id]["last_activity"] = datetime.datetime.now().isoformat()
        
        # Get encrypted user data
        encrypted_user_data = self.active_users[user_id]["encrypted_data"]
        
        # Decrypt user data
        user_data = self.data_security.decrypt_user_data(encrypted_user_data)
        
        # Update user data
        for key, value in update_data.items():
            user_data[key] = value
        
        # Encrypt updated user data
        updated_encrypted_data = self.data_security.encrypt_user_data(user_data)
        
        # Update user profile
        self.active_users[user_id]["encrypted_data"] = updated_encrypted_data
        
        # Update user in each component as needed
        if update_data.get("update_sensor_settings", False):
            self.sensor_manager.update_user_settings(user_id, update_data)
        
        if update_data.get("update_analysis_settings", False):
            self.nutrition_analyzer.update_user_settings(user_id, update_data)
        
        if update_data.get("update_recommendation_settings", False):
            self.supplement_recommender.update_user_settings(user_id, update_data)
        
        if update_data.get("update_intake_settings", False):
            self.intake_manager.update_user_settings(user_id, update_data)
        
        if update_data.get("update_ui_settings", False):
            self.ui_manager.update_user_settings(user_id, update_data)
        
        logger.info(f"Profile updated for user {user_id}")
        return {"status": "success", "message": "Profile updated successfully"}


# Example usage
def main():
    # Initialize the system
    nutrition_system = NutritionSystem()
    
    # Start the system
    nutrition_system.start()
    
    try:
        # Register a user
        user_id = "user123"
        user_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 35,
            "gender": "male",
            "height": 175,  # cm
            "weight": 70,  # kg
            "notify_healthcare_provider": True,
            "healthcare_provider": {
                "name": "Dr. Smith",
                "email": "dr.smith@example.com"
            }
        }
        
        nutrition_system.register_user(user_id, user_data)
        
        # Simulate receiving sensor data
        sensor_data = {
            "timestamp": time.time(),
            "heart_rate": 72,
            "blood_pressure": {"systolic": 120, "diastolic": 80},
            "blood_oxygen": 98,
            "body_temperature": 36.7,
            "impedance_measurements": {
                "vitamin_d": 25,  # ng/mL
                "iron": 60,  # mcg/dL
                "vitamin_b12": 500,  # pg/mL
                "magnesium": 1.8,  # mg/dL
                "zinc": 70,  # mcg/dL
                "omega_3": 3.5,  # %
                "glucose": 95  # mg/dL
            }
        }
        
        # Process the sensor data
        nutrition_system.process_sensor_data(user_id, sensor_data)
        
        # Get the user's dashboard
        dashboard = nutrition_system.get_user_dashboard(user_id)
        print(json.dumps(dashboard, indent=2))
        
        # Record a supplement intake
        nutrition_system.record_supplement_intake(user_id, "vd001")
        
        # Get a health report
        report = nutrition_system.get_health_report(user_id, "weekly")
        print(json.dumps(report, indent=2))
    
    finally:
        # Stop the system
        nutrition_system.stop()


if __name__ == "__main__":
    main()