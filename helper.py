def generate_questions(survey_data):
    prompt = f"Generate {survey_data['question_count']} survey questions based on the following information:\n\n"
    prompt += f"Title: {survey_data['title']}\n"
    prompt += f"Expected Insights: {survey_data['insights']}\n"
    prompt += f"Problem Description: {survey_data['problem_description']}\n"
    prompt += f"Interview Tone: {survey_data['interview_tone']}\n"
    prompt += f"Maximum Follow-up Questions: {survey_data['follow_up_questions']}\n\n"
    prompt += "Provide only the questions, separated by newlines."
    
    