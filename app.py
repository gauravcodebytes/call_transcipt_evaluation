
from flask import Flask, request, jsonify
import os
import openai
import gdown
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# OpenAI API Key Setup
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

openai_client = openai.OpenAI(api_key=api_key)

# Google Drive Links
UMBRELLA_FOLDER_LINK = "https://drive.google.com/drive/folders/1_o-76dq_2rm21PNP_l0h88aG9ESdQz3X"
TRANSCRIPTS_ROOT = "PM_wise_call_transcripts"
IDEAL_SCRIPT_LINK = "https://drive.google.com/uc?id=1uNEGNdQm-GXWGHj5MVtz9tj-BGKkauRs"
IDEAL_SCRIPT_PATH = "ideal_script.txt"

os.makedirs(TRANSCRIPTS_ROOT, exist_ok=True)

# Function to download the transcripts folder
def download_folder():
    print("Downloading transcripts...")
    gdown.download_folder(UMBRELLA_FOLDER_LINK, output=TRANSCRIPTS_ROOT, quiet=False, use_cookies=False)
    return bool(os.listdir(TRANSCRIPTS_ROOT))

# Function to download the ideal script
def download_ideal_script():
    print("Downloading ideal script...")
    gdown.download(IDEAL_SCRIPT_LINK, output=IDEAL_SCRIPT_PATH, quiet=False)
    return os.path.exists(IDEAL_SCRIPT_PATH)

# Function to evaluate a transcript
def evaluate_transcript(transcript_text, ideal_script):
    prompt = f"""
    You are an expert evaluator for call transcripts. Compare the provided transcript with the ideal script and provide:
    1. A similarity score (0-100).
    2. Key differences and improvement areas.

    Ideal Script:
    {ideal_script}

    Transcript to Evaluate:
    {transcript_text}

    Provide a structured response as:
    - Similarity Score: X%
    - Key Differences: [list the differences]
    - Improvement Areas: [list improvement areas]
    """

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert call evaluator."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Function to evaluate all transcripts for a PM
def evaluate_pm(pm_name):
    pm_folder_path = os.path.join(TRANSCRIPTS_ROOT, pm_name)
    if not os.path.exists(pm_folder_path):
        return None

    transcript_files = [f for f in os.listdir(pm_folder_path) if f.endswith(".txt")]
    if not transcript_files:
        return None

    results = []
    for file_name in transcript_files:
        file_path = os.path.join(pm_folder_path, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()
        evaluation_result = evaluate_transcript(transcript_text, ideal_script)
        results.append({"file": file_name, "evaluation": evaluation_result})
    return results

# Download files at startup
download_folder()
download_ideal_script()

# Load the ideal script
if os.path.exists(IDEAL_SCRIPT_PATH):
    with open(IDEAL_SCRIPT_PATH, "r", encoding="utf-8") as f:
        ideal_script = f.read()
else:
    ideal_script = ""

# Ask if evaluation should be performed
available_pms = [name for name in os.listdir(TRANSCRIPTS_ROOT) if os.path.isdir(os.path.join(TRANSCRIPTS_ROOT, name))]
if available_pms:
    user_input = input("Would you like to evaluate the transcripts? (yes/no): ").strip().lower()
    if user_input == "yes":
        for pm_name in available_pms:
            print(f"\nEvaluating transcripts for PM: {pm_name}")
            evaluation_results = evaluate_pm(pm_name)
            if evaluation_results:
                for result in evaluation_results:
                    print(f"\nFile: {result['file']}")
                    print(f"Evaluation:\n{result['evaluation']}\n")
            else:
                print(f"No valid transcripts found for {pm_name}")
    else:
        print("Skipping evaluation.")
else:
    print("No PM-specific folders found!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

