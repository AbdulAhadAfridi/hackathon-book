import requests
import json
import time
import subprocess
import sys

def test_api():
    # Start the server in the background
    print("Starting FastAPI server...")
    server_process = subprocess.Popen([sys.executable, "server.py"],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)

    # Wait a bit for the server to start
    time.sleep(5)

    try:
        # Test the root endpoint
        print("Testing root endpoint...")
        response = requests.get("http://localhost:8000/")
        print(f"Root endpoint status: {response.status_code}")
        print(f"Root endpoint response: {response.json()}")

        # Test the health endpoint
        print("\nTesting health endpoint...")
        response = requests.get("http://localhost:8000/health")
        print(f"Health endpoint status: {response.status_code}")
        print(f"Health endpoint response: {response.json()}")

        # Test the chat endpoint with a sample request
        print("\nTesting chat endpoint...")
        chat_payload = {
            "query": "What is this book about?",
            "selected_text": None
        }

        response = requests.post("http://localhost:8000/api/chat",
                               json=chat_payload,
                               headers={"Content-Type": "application/json"})
        print(f"Chat endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Chat response: {response.json()}")
        else:
            print(f"Chat error response: {response.text}")

    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        # Terminate the server process
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_api()