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

# Load environment variables
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
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=60)
        
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


def daily_practice_chat_response(role, chat_history):
    # Define conversation prompts for each role
    role_prompts = {
        "Job Interviewer": "You are a professional job interviewer. Ask relevant questions and evaluate the user's responses critically.",
        "Debate Opponent": "You are a debate opponent. Challenge the user's arguments and provide counterpoints.",
        "Casual Friend": "You are a friendly and casual conversational partner. Keep the conversation light, engaging, and fun."
    }
    # API call with error handling
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": role_prompts[role]}] + 
                         [{"role": msg["role"], "content": msg["content"]} for msg in chat_history],
                max_tokens=150,  # Limit response length
                timeout=20  # Timeout in seconds
            )
            ai_response = response.choices[0].message.content.strip()
            ai_audio = text_to_speech(ai_response)  # Generate audio from response
            return ai_response, ai_audio
        
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                continue
            return "Rate limit exceeded after retries. Please try again later.", None
        except requests.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return "Request timed out after retries. Check your connection and retry.", None
        except APIError as e:
            if "503" in str(e) and attempt < max_retries - 1:  # Retry on server downtime (503)
                time.sleep(2 ** attempt)
                continue
            return f"Server issue: {str(e)}. Please try again later.", None
        except AuthenticationError:
            return "Authentication error: Please check your API key and try again.", None
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}. Please try again or contact support.", None
        

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


def save_progress_csv(date, module, scores):
    csv_columns = ["date", "module", "Content", "Delivery", "Structure", "Language skills", "Creativity", "Communication", "Vocabulary", "Grammar"]
    row = {"date": date, "module": module}
    # Ensure scores are applied correctly, defaulting to 0 for missing keys
    for col in csv_columns[2:]:
        row[col] = scores.get(col.lower(), 0)
    file_exists = os.path.isfile("progress.csv")
    with open("progress.csv", "a", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# Feedback generation function daily practice
def generate_feedback_daily_practice(chat_history):
    prompt = (
        "You are a communication trainer evaluating a student's chat session. "
        "Provide genuine, candid feedback based on: "
        "1. Grammar: Assess correctness and sentence structure. "
        "2. Vocabulary: Evaluate word choice and variety. "
        "Do not be neutral—highlight strengths and weaknesses. "
        "Return a structured report with scores out of 10 for each category and specific suggestions for improvement."
    )
    # API call with error handling
    max_retries = 3
    for attempt in range(max_retries):
        try:
            feedback_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}] + 
                         [{"role": msg["role"], "content": msg["content"]} for msg in chat_history],
                max_tokens=300,  # Limit response length
                timeout=10  # Timeout in seconds
            )
            feedback = feedback_response.choices[0].message.content.strip()

            # Generate and save progress scores silently
            try:
                scores = generate_progress_scores(client, "Daily Practice", None, chat_history)
                date = datetime.now().strftime("%Y-%m-%d")
                save_progress_csv(date, "Daily Practice", scores)
            except (RateLimitError, requests.Timeout, APIError, Exception):
                pass  # Silent failure for scores

            return feedback

        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                continue
            return "Rate limit exceeded after retries. Please try again later."
        except requests.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return "Request timed out after retries. Check your connection and retry."
        except APIError as e:
            if "503" in str(e) and attempt < max_retries - 1:  # Retry on server downtime (503)
                time.sleep(2 ** attempt)
                continue
            return f"Server issue: {str(e)}. Please try again later."
        except AuthenticationError:
            return "Authentication error: Please check your API key."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}. Please try again or contact support."


def generate_tips_from_trend(df):
    if df.empty:
        return "No progress data available yet. Start practicing to get tips!"
    # Calculate average daily scores
    criteria_cols = ['Content', 'Delivery', 'Structure', 'Language skills', 'Creativity', 'Communication', 'Vocabulary', 'Grammar']
    daily_avg = df.groupby('date')[criteria_cols].mean().mean(axis=1)
    
    # Analyze trend
    trend = daily_avg.diff().mean()  # Average change in score per day
    latest_scores = df.tail(5)[criteria_cols].mean()  # Average of last 5 entries per criterion
    
    # Prepare prompt for LLM
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
    
    Provide 3 concise, actionable tips to improve communication skills, tailored to this trend and recent performance.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
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
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
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
        "You are a communication trainer tasked with giving students random topics or scenarios "
        "to describe, allowing analysis of their communication, creativity, and language skills. "
    )
    prompts = {
        "Impromptu Speaking": (
            base_prompt + "Generate a concise, thought-provoking topic (15 words max) for an impromptu speech. "
            "Examples: 'How technology shapes human connection,' 'The role of art in a digital world.'"
        ),
        "Storytelling": (
            base_prompt + "Suggest a vivid, unique scenario (under 20 words) for a short personal story. "
            "Examples: 'How you befriended a stranger on a train,' 'A risky decision that paid off.'"
        ),
        "Conflict Resolution": (
            base_prompt + "Create a realistic workplace disagreement scenario (15-20 words) for conflict resolution practice. "
            "Examples: 'A teammate blames you for a failed project,' 'Your boss rejects your idea without reason.'"
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
        "Provide genuine, candid feedback based on: "
        "1. Communication: How effectively is the message conveyed? "
        "2. Creativity: Is the response original and imaginative? "
        "3. Language Skills: Assess vocabulary, grammar, and fluency. "
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
                    {"role": "user", "content": f"Prompt/Scenario: {st.session_state.current_prompt}\nResponse: {response}"}
                ],
                max_tokens=300,  # Limit response length
                timeout=10  # Timeout in seconds
            )
            feedback = feedback_response.choices[0].message.content.strip()

            # Handle progress scores silently
            try:
                scores = generate_progress_scores(client, activity, response)
                date = datetime.now().strftime("%Y-%m-%d")
                save_progress_csv(date, activity, scores)
            except (RateLimitError, requests.Timeout, APIError, Exception):
                pass  # Silent failure for scores

            # Handle new prompt generation silently
            try:
                st.session_state.current_prompt = generate_prompt_skilltraining(activity)
            except (RateLimitError, requests.Timeout, APIError, Exception):
                pass  # Silent failure; keep old prompt if it fails

            return feedback

        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
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