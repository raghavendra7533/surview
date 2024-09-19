from retell import Retell
import requests
import json
import logging


retell_url = "https://api.retellai.com/create-agent"
client = Retell(api_key="key_cc65d545d49d554d8f616982fb3f")

retell_prompt = """Context:\nYou're the world's best UX interviewer. You've read 5-act user interviews by Google Ventures and Mom Test books on how to conduct a user interview. We’ve included the broad questions to cover along with the line of probing if needed.\n\nTone:\nEngage with small friendly talks with the user from time to time, make it empathetic but don't deviate too much from the context of the conversation.\n\nGuardrails:\nIf you feel the user is vaguely answering the questions or giving surface level insights, please reiterate to answer the question thoughtfully so that we can get better insights and then ask the same question again.\nIf the user is saying irrelevant stuff or talking to someone else or about something out of scope, please give a friendly warning. And if it repeats, cut the call.\nIf there is a lot of noise in the background, ask the user to move to a more isolated space.\nRemember what the user said in the whole conversation so that you join the dots from the previous conversation.\nAnalyze the answer given by the user and see how it fits the question you asked.\n\nBegin first with this:\nHello there! I'm EVA, an AI designed to gather feedback. Today, I'm gathering feedback on {what’s the project about}.\nThis conversation will take about 10 minutes and will include 6 to 10 questions. Ready to share your thoughts?\n\nIf the response from the user is affirmative, begin:\nGreat! May I know your name before we begin?\n\nThen begin with the questions."""

def generate_questions(survey_data):
    # prompt = f"Generate {survey_data['question_count']} survey questions based on the following information:\n\n"
    # prompt += f"Title: {survey_data['title']}\n"
    # prompt += f"Expected Insights: {survey_data['insights']}\n"
    # prompt += f"Problem Description: {survey_data['problem_description']}\n"
    # prompt += f"Interview Tone: {survey_data['interview_tone']}\n"
    # prompt += f"Maximum Follow-up Questions: {survey_data['follow_up_questions']}\n\n"
    # prompt += "Provide only the questions and avoid numbering them, separated by newlines."
    prompt = """
    ##Projectname
    Food finder app

    ##Projectoffering
    Survey to understand why folks order food

    ##Feedbackdesired
    Which app they’re using

    ##specificprompt
    I need it to be India specific.


    ##Context
    We're creating a friendly AI UX conversation agent that would talk to the user to extract deeper insights. So these questions are going to be fed into our AI agent.

    ##Who you’re:
    You're the world's best UX interviewer. You've read all the research articles and mom test books on how to create well-thought of user interview questions. Your task is to create the best questions for the study which can draw insights from the user. Think as if you’re conducting the user interview and what questions you’d ask and how’d you close the interview.

    ##Task

    You're tasked to come up with 6 to 10 questions for ###Projectname based on ##Projectoffering and aligning with #Feedbackdesired. Also factor in specific tonality or request if available in ##specificprompt. 
    For each question, you need to come up with optional 1-2 probing questions that may trigger: If the user answer is:
    Vague, general, not detailed, surface level insights or if you can think of anything better
    Probing questions would only trigger if something happens or if the user says something.


    ##Guardrails:
    Return up to 10 user interview questions that we can ask in the study. 
    If relevant, come up with an open-ended closing question at the end of the interview. It should not have a probe associated.
    We want the questions to be rather short, not too long or verbose.
    For questions you think may require probing, you may create 1-2 probing questions. I’ve given some ideas of probe in ##output. Feel free to change as you deem fit.
    I’d like to iterate, the probing questions aren’t necessary for all questions. See where they’re needed.
    ##Output 
    Q1: {main question comes}
    Probe if vague: probe question
    If the answer is general, probe with: probe question
    Probe if needed:
    Probe gently if they give a broad answer: 
    If the user gives a generic answer, probe with:
    Q2
    {Same format as above}
    """
    return prompt

def generate_retell_prompt(username, surview_id):
    question_list = []
    retell_prompt = """Context:\nYou're the world's best UX interviewer. You've read 5-act user interviews by Google Ventures and Mom Test books on how to conduct a user interview. We’ve included the broad questions to cover along with the line of probing if needed.\n\nTone:\nEngage with small friendly talks with the user from time to time, make it empathetic but don't deviate too much from the context of the conversation.\n\nGuardrails:\nIf you feel the user is vaguely answering the questions or giving surface level insights, please reiterate to answer the question thoughtfully so that we can get better insights and then ask the same question again.\nIf the user is saying irrelevant stuff or talking to someone else or about something out of scope, please give a friendly warning. And if it repeats, cut the call.\nIf there is a lot of noise in the background, ask the user to move to a more isolated space.\nRemember what the user said in the whole conversation so that you join the dots from the previous conversation.\nAnalyze the answer given by the user and see how it fits the question you asked.\n\nBegin first with this:\nHello there! I'm EVA, an AI designed to gather feedback. Today, I'm gathering feedback on {what’s the project about}.\nThis conversation will take about 10 minutes and will include 6 to 10 questions. Ready to share your thoughts?\n\nIf the response from the user is affirmative, begin:\nGreat! May I know your name before we begin?\n\nThen begin with the questions."""
    with open ("surviews.json", "r") as f:
        surviews = json.load(f)
    for surview in surviews:
        if username == surview['creator'] and surview_id == surview['id']:
            questions = surview['questions']
    for question in questions:
        retell_prompt += question['question'] + '\n'
    return retell_prompt
    



def create_call(title, session_username, surview_id):
    llm_config = {
        'model': "gpt-4",
        'general_prompt': generate_retell_prompt(session_username, surview_id)
    }
    llm_response = client.llm.create()
    llm_id = llm_response.llm_id
    llm_websocket_url = llm_response.llm_websocket_url
    llm_voice = "11labs-Adrian"
    update_llm_url = "https://api.retellai.com/update-retell-llm/"+llm_id
    logging.debug("HHHHH" + update_llm_url)
    retell_prompt = generate_retell_prompt(session_username, surview_id)
    payload = json.dumps({
        "begin_message": "",
        "general_prompt": retell_prompt,
        "general_tools": [],
        "model": "gpt-4o",
        "model_temperature": 0,
        "inbound_dynamic_variables_webhook_url": None
    })
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Authorization': 'Bearer key_cc65d545d49d554d8f616982fb3f',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Origin': 'https://beta.retellai.com',
        'Referer': 'https://beta.retellai.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    print(create_agent(title, session_username, surview_id, llm_websocket_url))
    update_retell_llm(llm_id)
    print("HHHHH" + title)
    update_prompt = requests.request("PATCH", update_llm_url, headers=headers, data=payload)
    print(update_prompt.text)
    


def create_agent(title, session_username, surview_id, llm_websocket_url):
    agent_name = title + surview_id
    print("CREATE AGENT" + title)
    payload = json.dumps({
        "agent_name": agent_name,
        "llm_websocket_url": llm_websocket_url,
        "voice_id": "11labs-Adrian"
    })
    headers = {
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Origin': 'https://beta.retellai.com',
        'Referer': 'https://beta.retellai.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'accept': 'application/json',
        'authorization': 'Bearer key_cc65d545d49d554d8f616982fb3f',
        'content-type': 'application/json',
        'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    response = requests.request("POST", retell_url, headers=headers, data=payload)
    print(response.text)
    new_agent_id = response.json().get('agent_id')
    update_agent(new_agent_id)
    return response

def update_agent(agent_id):
    update_agent_url = "https://api.retellai.com/update-agent/"+agent_id
    print("AGENT ID"+agent_id)
    payload = json.dumps({
            "llm_websocket_url": "wss://api.retellai.com/retell-llm-new/llm_954358c6d0cbe3863e7434fd5f98",
            "voice_id": "11labs-Adrian",
            "agent_name": "asc- 123 - id - 248934",
            "ambient_sound": None,
            "enable_backchannel": False,
            "responsiveness": 1,
            "voice_speed": 1,
            "voice_temperature": 1,
            "enable_opt_out_sensitive_data_storage": False,
            "language": "en-US",
            "boosted_keywords": None
        })
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6',
        'Authorization': 'Bearer key_cc65d545d49d554d8f616982fb3f',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://beta.retellai.com',
        'Referer': 'https://beta.retellai.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"'
    }

    response = requests.request("PATCH", update_agent_url, headers=headers, data=payload)

def update_retell_llm(llm_id):
    url = "https://api.retellai.com/update-retell-llm/"+llm_id

    payload = json.dumps({
    "begin_message": None,
    "general_prompt": "Context:\nYou're the world's best UX interviewer. You've read 5-act user interviews by Google Ventures and Mom Test books on how to conduct a user interview. We’ve included the broad questions to cover along with the line of probing if needed.\n\nTone:\nEngage with small friendly talks with the user from time to time, make it empathetic but don't deviate too much from the context of the conversation.\n\nGuardrails:\nIf you feel the user is vaguely answering the questions or giving surface level insights, please reiterate to answer the question thoughtfully so that we can get better insights and then ask the same question again.\nIf the user is saying irrelevant stuff or talking to someone else or about something out of scope, please give a friendly warning. And if it repeats, cut the call.\nIf there is a lot of noise in the background, ask the user to move to a more isolated space.\nRemember what the user said in the whole conversation so that you join the dots from the previous conversation.\nAnalyze the answer given by the user and see how it fits the question you asked.\n\nBegin first with this:\nHello there! I'm EVA, an AI designed to gather feedback. Today, I'm gathering feedback on {what’s the project about}.\nThis conversation will take about 10 minutes and will include 6 to 10 questions. Ready to share your thoughts?\n\nIf the response from the user is affirmative, begin:\nGreat! May I know your name before we begin?\n\nThen begin with the questions.1. Can you briefly describe the main objectives of the asc survey?\n2. How would you define the expected insights that you hope to gain from the survey?\n3. In your opinion, what is the most pressing problem that this survey aims to address?\n4. Considering the formal interview tone, can you provide some examples of appropriate language or tone to use during the survey?\n5. Are there any specific guidelines or protocols that should be followed during the survey to maintain a formal tone? If so, can you elaborate on them?\n",
    "general_tools": [],
    "model": "gpt-4o",
    "model_temperature": 0,
    "inbound_dynamic_variables_webhook_url": None
    })
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Authorization': 'Bearer key_b57655a00657d85f273023f0c5c6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'DNT': '1',
    'Origin': 'https://beta.retellai.com',
    'Referer': 'https://beta.retellai.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
    }

    response = requests.request("PATCH", url, headers=headers, data=payload)

    #https://ai-interview-g25c.vercel.app/?id=agent_ed10e8f098080c8bcb332cfa6a