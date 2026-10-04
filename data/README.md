# ResumeIQ
AI resume screener and career coach.

Problem: HR teams get hundreds of resumes and keyword filters miss good candidates.
Solution: TF-IDF retrieval for speed, Gemini AI for scoring, explanations and resume feedback.
Data: Resume Screening dataset (962 rows, 166 unique after cleaning, 25 categories).
Tech: Python, Streamlit, Pandas, scikit-learn, Gemini API

Run locally:
pip install -r requirements.txt
streamlit run app.pypython prepare_data.py