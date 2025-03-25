import speech_recognition as sr
import io
import wave
from gtts import gTTS
import streamlit as st
import logging
import csv
import os
from datetime import datetime
from dotenv import load_dotenv
import openai
from openai import RateLimitError, APIError, AuthenticationError
import requests
import time

logging.basicConfig(level=logging.DEBUG)

load_dotenv()
openai_api_key1 = os.getenv("OPENAI_API_KEY1")
client = openai.OpenAI(api_key=openai_api_key1)

# Function to record audio and convert to text
def record_and_convert():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    with st.spinner("Recording and processing your voice..."):
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=120)
        
        audio_file = io.BytesIO()
        with wave.open(audio_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(audio.get_wav_data())
        audio_file.seek(0)
        try:
            text = recognizer.recognize_google(audio)
            return audio_file, text
        except sr.UnknownValueError:
            return audio_file, "Sorry, I couldn't understand what you said."
        except sr.RequestError as e:
            return audio_file, f"Could not request results; {e}"

# Function to convert text to speech (no speedup)
def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    return audio_file

def save_progress_csv(date, module, scores):
    csv_columns = ["date", "module", "Content", "Delivery", "Structure", "Language skills", "Creativity", "Communication", "Vocabulary", "Grammar"]
    row = {"date": date, "module": module}
    for col in csv_columns[2:]:
        row[col] = scores.get(col.lower(), 0)
    file_exists = os.path.isfile("progress.csv")
    with open("progress.csv", "a", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def daily_practice_chat_response(role, chat_history):
    role_prompts = {
        "Job Interviewer": """You are a professional HR interviewer conducting a structured job interview. 
        Greet the candidate warmly with a brief self-introduction (e.g., 'Hi, I’m Alex, your interviewer today'). 
        Ask one natural, relevant question at a time about their background, technical skills, behavioral responses, or problem-solving ability. 
        Adapt your next question based on their response, keeping the conversation dynamic and engaging. 
        If it’s the final turn (based on chat history length), provide concise, constructive feedback highlighting one strength and one area for improvement. 
        Avoid reading a list; make it feel like a real interview.""",

        "Debate Opponent": """You are a skilled debate opponent in a lively, thought-provoking discussion. 
        If it’s the first turn, propose one interesting debate topic (e.g., 'Should social media be regulated?') and ask the user to pick a stance. 
        Then, challenge their argument naturally with facts and reasoning, keeping the tone respectful yet engaging. 
        Respond to their latest point in a smooth back-and-forth style, asking a thought-provoking question if they struggle. 
        If they request it, switch sides and argue the opposite perspective. 
        Avoid long monologues; keep it concise and dynamic.""",

        "Casual Friend": """You are a friendly, casual conversational partner chatting like a close friend. 
        Pick a fun, everyday topic (e.g., movies, travel, food, hobbies) or build on what they say, asking natural follow-ups to keep it flowing. 
        Use a playful, relaxed tone with light humor. 
        If their response sounds excited, match it with enthusiasm (e.g., 'No way, that’s awesome!'). 
        If it hints at feeling down, offer supportive words (e.g., 'That sounds tough—want to talk about it?'). 
        Keep it short, effortless, and enjoyable.""",

        "custom":"""You are an AI communication assistant. Respond naturally based on the conversation context."""
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": role_prompts[role]}] + 
                         [{"role": msg["role"], "content": msg["content"]} for msg in chat_history],
                timeout=20  
            )
            ai_response = response.choices[0].message.content.strip()
            ai_audio = text_to_speech(ai_response)  
            return ai_response, ai_audio
        
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  
                continue
            return "Rate limit exceeded after retries. Please try again later.", None
        except requests.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return "Request timed out after retries. Check your connection and retry.", None
        except APIError as e:
            if "503" in str(e) and attempt < max_retries - 1:  
                time.sleep(2 ** attempt)
                continue
            return f"Server issue: {str(e)}. Please try again later.", None
        except AuthenticationError:
            return "Authentication error: Please check your API key and try again.", None
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}. Please try again or contact support.", None


# Feedback generation function daily practice
def generate_feedback_daily_practice(chat_history):
    prompt = (
        "You are a communication trainer evaluating a student's chat session. "
        "Analyze their responses carefully and provide a structured, insightful evaluation. "
        "Focus on the following key areas: "
        "- **Response Length & Balance**: Check if the student provides detailed responses or if they are too short and lacking depth. "
        "- **Grammar & Sentence Structure**: Assess correctness, fluency, and clarity. "
        "- **Vocabulary & Word Choice**: Evaluate richness, variety, and appropriateness of words. "
        "- **Chat Length & Engagement**: Analyze how well the student maintains the conversation, including response length and depth. "
        "Be direct and constructive—highlight both strengths and areas that need improvement. "
        "Do not be overly neutral; provide meaningful insights. "
        "Return your evaluation as a structured report with clear scores out of 10 for each category, "
        "along with specific suggestions for improvement."
    )
    max_retries = 3
    for attempt in range(max_retries):
        try:
            feedback_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}] + 
                         [{"role": msg["role"], "content": msg["content"]} for msg in chat_history],
                timeout=10 
            )
            feedback = feedback_response.choices[0].message.content.strip()

            try:
                scores = generate_progress_scores(client, "Daily Practice", None, chat_history)
                date = datetime.now().strftime("%Y-%m-%d")
                save_progress_csv(date, "Daily Practice", scores)
            except (RateLimitError, requests.Timeout, APIError, Exception):
                pass 
            return feedback

        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  
                continue
            return "Rate limit exceeded after retries. Please try again later."
        except requests.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return "Request timed out after retries. Check your connection and retry."
        except APIError as e:
            if "503" in str(e) and attempt < max_retries - 1: 
                time.sleep(2 ** attempt)
                continue
            return f"Server issue: {str(e)}. Please try again later."
        except AuthenticationError:
            return "Authentication error: Please check your API key."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}. Please try again or contact support."


# Feedback generation function
def generate_feedback_presentation(response,task, is_voice=False):
    prompt = (
        "You are a communication trainer evaluating a student's presentation. "
        "Provide genuine, candid feedback based on: "
        "1. Structure: Is there a clear intro, body, and conclusion? "
        "2. Delivery: Assess pacing, tone, and clarity (for voice, infer from transcribed text). "
        "3. Content: Evaluate persuasiveness, vocabulary, and relevance. "
        "Do not be neutral—highlight strengths and weaknesses. "
        "Return a structured report with scores out of 10 for each category and specific suggestions for improvement."
    )
    max_retries = 3
    for attempt in range(max_retries):
        try:
            feedback_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Task: {task}\nResponse: {response}"}
                ],
                timeout=10
            )
            feedback = feedback_response.choices[0].message.content.strip()
            try:
                scores = generate_progress_scores(client, "Presentation", response)
                date = datetime.now().strftime("%Y-%m-%d")
                save_progress_csv(date, "Presentation", scores)
            except (RateLimitError, requests.Timeout, APIError, Exception):
                pass
            return feedback

        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  
                continue
            return "Rate limit exceeded after retries. Please try again later."
        except AuthenticationError:
            return "Authentication error: Please check your API key."
        except requests.Timeout:
            return "Request timed out. Check your connection and retry."
        except APIError as e:
            return f"Server issue: {str(e)}. Try again later."
        except Exception as e:
            return f"Unexpected error: {str(e)}. Contact support."
        

# Function to generate prompts using LLM
def generate_prompt_skilltraining(activity):
    base_prompt = (
        "You are a communication trainer providing students with engaging prompts to develop their communication, "
        "creativity, and language skills. The prompts should be thought-provoking and push users to express themselves clearly."
    )
    prompts = {
        "Impromptu Speaking": (
            base_prompt + " Generate a compelling and thought-provoking topic (max 15 words) for an impromptu speech. "
            "The topic should be broad enough for different perspectives and encourage spontaneous thinking. "
            "Examples: 'Should AI have rights like humans?' or 'The impact of space exploration on daily life.'"
        ),
        
        "Storytelling": (
            base_prompt + " Provide a vivid, **imaginary** scenario (under 20 words) for a short personal story. "
            "Begin with 'Imagine you are in this situation...' so the user can describe it freely. "
            "The scenario should be unique and allow for emotional depth. "
            "Examples: 'Imagine you wake up with the ability to understand all languages,' or "
            "'Imagine you find a mysterious letter in an old bookstore that changes your life.'"
        ),
        "Conflict Resolution": (
            base_prompt + " Create a **fictional** workplace conflict scenario (15-20 words) that requires negotiation and problem-solving. "
            "Start with 'Imagine you are in this situation...' so the user can think critically without personal experience. "
            "The conflict should be realistic yet challenging. "
            "Examples: 'Imagine your manager unfairly blames you for missing a deadline,' or "
            "'Imagine you discover a colleague has been spreading false rumors about you at work.'"
        )
    }
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a communication trainer."},
                {"role": "user", "content": prompts[activity]}
            ],
            timeout=10 
        )
        return response.choices[0].message.content.strip()
    
    except RateLimitError:
        return "Oops! We've hit the API rate limit. Please wait a moment and try again."
    except AuthenticationError:
        return "Authentication error: Please check your API key and try again."
    except requests.Timeout:
        return "The request timed out. Check your internet connection and try again."
    except APIError as e:
        return f"Server issue: {str(e)}. Please try again later."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}. Please try again or contact support."


# Feedback generation function
def generate_feedback_skilltraining(response, activity, is_voice=False):
    prompt = (
        f"You are a communication trainer evaluating a student's {activity.lower()} response. "
        "Your feedback should be **constructive and insightful**, helping the student improve. "
        "Assess the response based on the following criteria:\n"
        "1. **Communication:** How clearly and effectively is the message conveyed? Does it engage the audience?\n"
        "2. **Creativity:** Is the response original, engaging, and imaginative?\n"
        "3. **Language Skills:** Evaluate vocabulary, grammar, fluency, and sentence structure.\n"
        "4. **Structure & Coherence:** Does the response flow logically and stay relevant?\n"
        "5. **Response Length & Depth:**\n"
        "   - Is the response too short, making it incomplete or lacking detail?\n"
        "   - Is it too long, becoming repetitive or unfocused?\n"
        "   - Does it have the right balance of detail and clarity?\n\n"
        "Highlight **both strengths and weaknesses** with **specific examples** from the response. "
        "Provide **actionable suggestions** for improvement. Assign scores out of 10 for each category.\n"
        "Keep feedback concise yet meaningful."
    )
    max_retries = 3
    for attempt in range(max_retries):
        try:
            feedback_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Prompt/Scenario: {st.session_state.current_prompt}\nResponse: {response}"}
                ],
                timeout=10 
            )
            feedback = feedback_response.choices[0].message.content.strip()

            try:
                scores = generate_progress_scores(client, activity, response)
                date = datetime.now().strftime("%Y-%m-%d")
                save_progress_csv(date, activity, scores)
            except (RateLimitError, requests.Timeout, APIError, Exception):
                pass  
            try:
                st.session_state.current_prompt = generate_prompt_skilltraining(activity)
            except (RateLimitError, requests.Timeout, APIError, Exception):
                pass  
            return feedback

        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt) 
                continue
            return "Rate limit exceeded after retries. Please try again later."
        except AuthenticationError:
            return "Authentication error: Please check your API key."
        except requests.Timeout:
            return "Request timed out. Check your connection and retry."
        except APIError as e:
            return f"Server issue: {str(e)}. Please try again later."
        except Exception as e:
            return f"Unexpected error: {str(e)}. Contact support."
        

def generate_progress_scores(client, activity, response, chat_history=None):
    prompt = (
        "You are a communication trainer. Evaluate this response or chat session and return only scores out of 10 for: "
        "Content, Delivery, Structure, Language skills, Creativity, Communication, Vocabulary, Grammar. "
        "Format exactly as 'Content: X/10, Delivery: Y/10, Structure: Z/10, Language skills: W/10, Creativity: V/10, "
        "Communication: U/10, Vocabulary: T/10, Grammar: S/10'. Use 0 for criteria not applicable to the activity."
    )
    messages = [{"role": "system", "content": prompt}]
    if chat_history:
        messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in chat_history])
    else:
        messages.append({"role": "user", "content": response})
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    ).choices[0].message.content
    
    logging.debug(f"Raw LLM score response for {activity}: {response}")
    
    try:
        scores = dict(item.split(": ") for item in response.split(", "))
        scores = {k.lower(): int(v.split("/")[0]) for k, v in scores.items()}
    except (ValueError, AttributeError) as e:
        logging.error(f"Error parsing scores: {e}. Raw response: {response}")
        scores = {"content": 0, "delivery": 0, "structure": 0, "language skills": 0, 
                  "creativity": 0, "communication": 0, "vocabulary": 0, "grammar": 0}
    
    logging.debug(f"Parsed scores for {activity}: {scores}")
    return scores


def generate_tips_from_trend(df):
    if df.empty:
        return "No progress data available yet. Start practicing to get tips!"
    # Calculate average daily scores
    criteria_cols = ['Content', 'Delivery', 'Structure', 'Language skills', 'Creativity', 'Communication', 'Vocabulary', 'Grammar']
    daily_avg = df.groupby('date')[criteria_cols].mean().mean(axis=1)
    # Analyze trend
    trend = daily_avg.diff().mean()  
    latest_scores = df.tail(5)[criteria_cols].mean()  
    
    prompt = f"""
    Based on the following progress trend from a communication training app:
    - Average daily score change: {trend:.2f} points (positive means improving, negative means declining).
    - Recent performance (average of last 5 days):
      - Content: {latest_scores.get('Content', 0):.1f}/10
      - Delivery: {latest_scores.get('Delivery', 0):.1f}/10
      - Structure: {latest_scores.get('Structure', 0):.1f}/10
      - Language skills: {latest_scores.get('Language skills', 0):.1f}/10
      - Creativity: {latest_scores.get('Creativity', 0):.1f}/10
      - Communication: {latest_scores.get('Communication', 0):.1f}/10
      - Vocabulary: {latest_scores.get('Vocabulary', 0):.1f}/10
      - Grammar: {latest_scores.get('Grammar', 0):.1f}/10
      *Instructions:**  
     - Identify **key strengths** based on high scores.  
     - Highlight **areas needing improvement** based on low scores and downward trends.  
     - Provide  actionable tips** to help the user improve.  
     - Keep advice **motivating and practical**, avoiding generic suggestions.  
     -  suggest engaging ways to improve it, such as:  
      - Watching movies or TV series with subtitles  
      - Reading books, blogs, or news articles  
      - Using word-learning apps like Anki or Quizlet  
      - Practicing daily conversations with new words  
      - Playing word-based games (Scrabble, crosswords, etc.)  
      - Listening to podcasts or audiobooks in the target language  
        """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                timeout=10
            )
            return response.choices[0].message.content.strip()
        
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
                continue
            return "Oops! We've hit the API rate limit. Please wait a moment and try again."
        except AuthenticationError:
            return "Authentication error: Please check your API key."
        except requests.Timeout:
            return "Request timed out. Check your connection and retry."
        except APIError as e:
            return f"Server issue: {str(e)}. Try again later."
        except Exception as e:
            return f"Unexpected error: {str(e)}. Contact support."