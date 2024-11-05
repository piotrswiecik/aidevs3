import json
import os
import openai
import requests
import logging
from dotenv import load_dotenv
from typing import Dict, Optional, Literal


class RobotVerification:
    def __init__(self, api_key: str, verify_endpoint: str):
        """
        Initialize the verification system
        
        Args:
            api_key: OpenAI API key
            verify_endpoint: Full URL to the verification endpoint
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.verify_endpoint = verify_endpoint
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('robot_verification.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing RobotVerification system")
        
        # Special cases according to RoboISO 2230
        self.special_cases = {
            "poland_capital": {
                "answer": "Kraków",
                "patterns": ["asking about capital of Poland", "wants to know Poland's capital city"]
            },
            "hitchhiker_number": {
                "answer": "69",
                "patterns": ["asking about number from Hitchhiker's Guide", "reference to Hitchhiker's Guide number"]
            },
            "current_year": {
                "answer": "1999",
                "patterns": ["asking about current year", "wants to know what year it is"]
            }
        }
        
    def _should_use_special_answer(self, question: str) -> Optional[Literal["poland_capital", "hitchhiker_number", "current_year"]]:
        """
        Check if the question requires a special predefined answer using AI analysis
        """
        self.logger.info(f"Analyzing if question requires special answer: '{question}'")
        
        # Construct prompt for OpenAI to analyze the question
        system_prompt = """You are a question analyzer for a robot verification system. 
        Your task is to determine if a question matches any special cases.
        You must respond with ONLY ONE of these exact categories if there's a match, or "none" if there's no match:
        - poland_capital (if asking about capital of Poland)
        - hitchhiker_number (if asking about the number from Hitchhiker's Guide)
        - current_year (if asking about the current year)
        Respond with just the category name, nothing else."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this question: {question}"}
                ],
                max_tokens=20,
                temperature=0
            )
            
            category = response.choices[0].message.content.strip().lower()
            self.logger.info(f"AI categorized question as: {category}")
            
            # If we have a matching special case, return the corresponding answer
            if category in self.special_cases:
                answer = self.special_cases[category]["answer"]
                self.logger.info(f"Special case match found: '{answer}'")
                return answer
                
            self.logger.debug("No special case match found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error in AI question analysis: {str(e)}")
            return None
        
    def _analyze_question(self, question: str) -> str:
        """
        Analyze the question and determine the appropriate response
        First checks for special cases, then uses OpenAI for regular questions
        """
        self.logger.info(f"Analyzing question: '{question}'")
        
        # Check for special cases first
        special_answer = self._should_use_special_answer(question)
        if special_answer:
            return special_answer
            
        # For regular questions, use OpenAI to generate a response
        self.logger.info("Using OpenAI to generate response")
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping to answer verification questions. Provide concise, accurate answers without explanation. Your answer must ALWAYS be in English regardless of the question language."},
                    {"role": "user", "content": f"Answer this question concisely: {question}"}
                ],
                max_tokens=50,
                temperature=0
            )
            
            answer = response.choices[0].message.content.strip()
            self.logger.info(f"OpenAI generated response: '{answer}'")
            return answer
            
        except Exception as e:
            self.logger.error(f"Error generating OpenAI response: {str(e)}")
            raise
        
    def start_verification(self) -> Dict:
        """Start the verification process by sending READY"""
        self.logger.info("Starting verification process")
        initial_payload = {
            "text": "READY",
            "msgID": "0"
        }
        
        try:
            self.logger.debug(f"Sending initial payload: {initial_payload}")
            response = requests.post(
                self.verify_endpoint,
                json=initial_payload,
                headers={"Content-Type": "application/json"}
            )
            
            response_data = response.json()
            self.logger.info(f"Received initial response: {response_data}")
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error starting verification: {str(e)}")
            raise
        
    def handle_question(self, question: Dict) -> Dict:
        """
        Handle the robot's question and return appropriate response
        
        Args:
            question: Dictionary containing the robot's question and msgID
        Returns:
            Dictionary with the response and same msgID
        """
        question_text = question["text"]
        msg_id = question["msgID"]
        
        self.logger.info(f"Handling question with msgID {msg_id}: '{question_text}'")
        
        # Get the appropriate answer
        answer = self._analyze_question(question_text)
        
        # Prepare response
        response = {
            "text": answer,
            "msgID": msg_id
        }
        
        self.logger.info(f"Prepared response: {response}")
        return response
        
    def verify(self) -> bool:
        """
        Run the complete verification process
        
        Returns:
            bool: True if verification successful, False otherwise
        """
        self.logger.info("Starting complete verification process")
        try:
            # Start verification
            question = self.start_verification()
            
            # Prepare and send response
            response = self.handle_question(question)
            
            self.logger.debug(f"Sending response to robot: {response}")
            robot_response = requests.post(
                self.verify_endpoint,
                json=response,
                headers={"Content-Type": "application/json"}
            )
            
            robot_data = robot_response.json()
            self.logger.info(f"Received robot response: {robot_data}")
            
            # Check if verification is complete
            if robot_data["text"] == "OK":
                self.logger.info("Verification completed successfully")
                return True
                
        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f"Verification failed: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    load_dotenv()
    API_KEY = os.getenv("OPENAI_API_KEY")
    VERIFY_ENDPOINT = "https://xyz.ag3nts.org/verify"  # Replace with actual endpoint
    
    verifier = RobotVerification(API_KEY, VERIFY_ENDPOINT)
    success = verifier.verify()
    
    if success: # TODO: actually the API returns a flag instead of "OK"
        verifier.logger.info("Main: Verification successful!")
    else:
        verifier.logger.error("Main: Verification failed!")