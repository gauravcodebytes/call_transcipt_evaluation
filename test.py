# import requests

# url = "http://127.0.0.1:8080/evaluate_pm"
# data = {"pm_name": "PM_test"}

# response = requests.post(url, json=data)
# print(response.json())


# import requests

# # Replace with your actual Google Drive public link
# google_drive_url = "https://drive.google.com/uc?id=YOUR_FILE_ID"

# response = requests.get(google_drive_url)

# if response.status_code == 200:
#     with open("test_download.txt", "wb") as f:
#         f.write(response.content)
#     print("✅ File downloaded successfully!")
# else:
#     print(f"❌ Failed to download: {response.status_code}, {response.text}")


# important test that solved things
# import os
# import gdown

# Google Drive Folder Link (Make sure it's public)
# GOOGLE_DRIVE_FOLDER_LINK = "https://drive.google.com/drive/folders/1_o-76dq_2rm21PNP_l0h88aG9ESdQz3X"
# SAVE_PATH = "PM_wise_call_transcripts"

# def download_folder():
#     """Downloads folder from Google Drive and checks if files exist."""
#     try:
#         print("Ensuring target directory exists...")
#         os.makedirs(SAVE_PATH, exist_ok=True)

#         print(f"Attempting to download folder from: {GOOGLE_DRIVE_FOLDER_LINK}")
#         gdown.download_folder(GOOGLE_DRIVE_FOLDER_LINK, output=SAVE_PATH, quiet=False, use_cookies=False)

#         # Check if the folder contains files
#         if not os.path.exists(SAVE_PATH) or not os.listdir(SAVE_PATH):
#             print("Downloaded folder is empty!")
#             return False

#         downloaded_files = os.listdir(SAVE_PATH)
#         print(f"Download successful! {len(downloaded_files)} files downloaded.")
#         print("Files:", downloaded_files)
#         return True

#     except Exception as e:
#         print(f"Error during download: {e}")
#         return False

# if __name__ == "__main__":
#     print("Testing Google Drive Folder Download...")
#     success = download_folder()
    
#     if success:
#         print("Test Passed: Files downloaded successfully.")
#     else:
#         print("Test Failed: No files downloaded.")




# from flask import Flask, request, jsonify
# import os
# import openai
# import gdown
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)  # Enable CORS for frontend communication

# # OpenAI API Key
# openai.api_key = os.getenv("OPENAI_API_KEY")

# # Google Drive Folder Link (Umbrella folder storing all PM-specific folders)
# UMBRELLA_FOLDER_LINK = "https://drive.google.com/drive/folders/1_o-76dq_2rm21PNP_l0h88aG9ESdQz3X"
# TRANSCRIPTS_ROOT = "PM_wise_call_transcripts"
# os.makedirs(TRANSCRIPTS_ROOT, exist_ok=True)

# # Ideal Script File Link
# IDEAL_SCRIPT_LINK = "https://drive.google.com/uc?id=1uNEGNdQm-GXWGHj5MVtz9tj-BGKkauRs"
# IDEAL_SCRIPT_PATH = "ideal_script.txt"

# # Function to download folder from Google Drive using gdown
# def download_folder():
#     """Downloads all PM-specific folders from Google Drive."""
#     try:
#         print(f"Downloading transcripts from: {UMBRELLA_FOLDER_LINK}")
#         gdown.download_folder(UMBRELLA_FOLDER_LINK, output=TRANSCRIPTS_ROOT, quiet=False, use_cookies=False)

#         if not os.listdir(TRANSCRIPTS_ROOT):
#             print("Downloaded folder is empty!")
#             return False

#         print(f"Transcripts downloaded successfully to {TRANSCRIPTS_ROOT}")
#         return True
#     except Exception as e:
#         print(f"Error downloading transcripts: {e}")
#         return False

# # Function to download ideal script
# def download_ideal_script():
#     """Downloads the ideal script from Google Drive."""
#     try:
#         print(f"Downloading ideal script from: {IDEAL_SCRIPT_LINK}")
#         gdown.download(IDEAL_SCRIPT_LINK, output=IDEAL_SCRIPT_PATH, quiet=False)

#         if not os.path.exists(IDEAL_SCRIPT_PATH):
#             print("Ideal script download failed!")
#             return False

#         print("Ideal script downloaded successfully.")
#         return True
#     except Exception as e:
#         print(f"Error downloading ideal script: {e}")
#         return False

# # Download transcripts and ideal script at startup
# download_folder()
# download_ideal_script()

# # Load the ideal script
# if os.path.exists(IDEAL_SCRIPT_PATH):
#     with open(IDEAL_SCRIPT_PATH, "r", encoding="utf-8") as f:
#         ideal_script = f.read()
# else:
#     ideal_script = ""

# # Function to evaluate a transcript
# def evaluate_transcript(transcript_text, ideal_script):
#     prompt = f"""
#     You are an expert evaluator for call transcripts. Compare the provided transcript with the ideal script and provide:
#     1. A similarity score (0-100).
#     2. Key differences and improvement areas.

#     Ideal Script:
#     {ideal_script}

#     Transcript to Evaluate:
#     {transcript_text}

#     Provide a structured response as:
#     - Similarity Score: X%
#     - Key Differences: [list the differences]
#     - Improvement Areas: [list improvement areas]
#     """

#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "You are an expert call evaluator."},
#             {"role": "user", "content": prompt}
#         ]
#     )
#     return response["choices"][0]["message"]["content"]

# # Endpoint to list available PMs
# @app.route("/list_pms", methods=["GET"])
# def list_pms():
#     """Returns a list of available PMs based on folder names."""
#     pm_folders = [name for name in os.listdir(TRANSCRIPTS_ROOT) if os.path.isdir(os.path.join(TRANSCRIPTS_ROOT, name))]
#     return jsonify({"available_pms": pm_folders})

# # Endpoint to evaluate all transcripts for a selected PM
# @app.route("/evaluate_pm", methods=["POST"])
# def evaluate_pm():
#     """Evaluates all transcripts for a given PM and returns the overall summary."""
#     data = request.json
#     pm_name = data.get("pm_name")

#     if not pm_name:
#         return jsonify({"error": "PM name not provided"}), 400

#     pm_folder_path = os.path.join(TRANSCRIPTS_ROOT, pm_name)

#     if not os.path.exists(pm_folder_path):
#         return jsonify({"error": f"No transcripts found for {pm_name}"}), 404

#     transcript_files = [f for f in os.listdir(pm_folder_path) if f.endswith(".txt")]

#     if not transcript_files:
#         return jsonify({"error": "No transcript files found"}), 404

#     results = []
#     for file_name in transcript_files:
#         file_path = os.path.join(pm_folder_path, file_name)

#         with open(file_path, "r", encoding="utf-8") as f:
#             transcript_text = f.read()

#         evaluation_result = evaluate_transcript(transcript_text, ideal_script)
#         results.append({"file": file_name, "evaluation": evaluation_result})

#     return jsonify({"pm_name": pm_name, "evaluations": results})

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080, debug=True)


import os
print(os.getenv("OPENAI_API_KEY"))