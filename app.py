from flask import Flask, render_template, request
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Gemini AI client
client = genai.Client()


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        resume = request.files.get("resume")
        role = request.form.get("role")

        if not resume:
            return "Please upload a resume."

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            resume.filename
        )

        resume.save(file_path)

        # Upload PDF directly to Gemini
        uploaded_file = client.files.upload(
            file=file_path
        )

        prompt = f"""
You are an AI career and resume analyzer.

Target Job Role:
{role}

Analyze the uploaded resume carefully.

Provide:

1. Placement Readiness Score out of 100
2. Strong Technical Skills
3. Missing or Weak Skills
4. Resume Strengths
5. Resume Improvement Suggestions
6. Recommended Technologies to Learn
7. Final Career Recommendation

Keep the analysis clear, professional, and useful
for a college student preparing for placements.
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[
                uploaded_file,
                prompt
            ]
        )

        analysis = response.text

        return f"""
        <html>
        <head>
            <title>AI Resume Analysis</title>

            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f8fafc;
                    padding: 40px;
                    color: #172033;
                }}

                .box {{
                    max-width: 900px;
                    margin: auto;
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
                }}

                h1 {{
                    color: #2563eb;
                }}

                pre {{
                    white-space: pre-wrap;
                    font-family: Arial, sans-serif;
                    line-height: 1.7;
                    font-size: 16px;
                }}

                a {{
                    display: inline-block;
                    margin-top: 25px;
                    padding: 12px 20px;
                    background: #2563eb;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                }}
            </style>
        </head>

        <body>

            <div class="box">

                <h1>AI Resume Analysis</h1>

                <p>
                    <b>Target Role:</b> {role}
                </p>

                <hr>

                <pre>{analysis}</pre>

                <a href="/">
                    ← Analyze Another Resume
                </a>

            </div>

        </body>
        </html>
        """

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)