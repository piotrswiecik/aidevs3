import asyncio
import os
from dotenv import load_dotenv

from aidevs3.robot_verification import RobotVerification


async def main():
    load_dotenv()
    API_KEY = os.getenv("OPENAI_API_KEY")
    VERIFY_ENDPOINT = "https://xyz.ag3nts.org/verify"  # Replace with actual endpoint
    
    verifier = RobotVerification(API_KEY, VERIFY_ENDPOINT)
    success = await verifier.verify()
    
    if success: # TODO: actually the API returns a flag instead of "OK"
        verifier.logger.info("Main: Verification successful!")
    else:
        verifier.logger.error("Main: Verification failed!")


# Example usage
if __name__ == "__main__":
    asyncio.run(main())