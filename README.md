# Verbal Communication Skills Trainer

A web-based application built with Streamlit and OpenAI’s GPT-3.5-turbo model to help learners improve their verbal communication skills through interactive chat, structured skill-building activities, and presentation assessments. This project serves as a wrapper around the OpenAI API, offering a user-friendly interface and actionable feedback to enhance conversational abilities.

## Features
- **Interactive Chat**: Practice with AI partners (Job Interviewer, Debate Opponent, Casual Friend) via text or voice.
- **Skill Training**: Activities like Impromptu Speaking, Storytelling, and Conflict Resolution with tailored feedback.
- **Presentation Assessments**: Submit text or voice presentations for detailed analysis on structure, delivery, and content.
- **Progress Tracking**: Stores scores in a CSV file for trend analysis and advices.

## Setup Instructions

### Prerequisites
- Python 3.8+
- Git
- An OpenAI API key (sign up at [OpenAI](https://platform.openai.com/))

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sxrxth10/communication_assistant

2. **Install Dependencies**:
    pip install -r requirements.txt

3. **Set Up Environment Variables:**:
    create a .env file in your project root and add your openai api key.
    OPENAI_API_KEY1=your-api-key-here

4. **Run the Application**:
    streamlit run frontend/app.py
    Open your browser to http://localhost:8501



## Usage Examples
1. **Interactive Chat (Daily Practice)**
    Navigate: Go to the "Daily Practice" tab.
    Input: Select "Casual Friend" and type: "I had a great day at the park!"

    Output:AI: Awesome! What made it so great—did you have a picnic or just soak up the sun?
    Audio playback available via Streamlit’s audio widget.

2. **Skill Training (Impromptu Speaking)**
    Navigate: Go to "Skill Training" and choose "Impromptu Speaking."
    Prompt: "Explain why teamwork is important."
    Input: "Teamwork helps us win because we share ideas."

    Output:- Communication: 7/10 - Clear but brief; expand your points.
    - Creativity: 6/10 - Solid idea, try a unique angle next time.
    - Language Skills: 8/10 - Good grammar, simple vocabulary.
    Suggestions: Add an example (e.g., "In sports, teamwork wins games") for impact.

3. **Presentation Assessment**
    Navigate: Go to "Presentation" tab.
    Input: Submit text: "Hi, I’m presenting my project today. It’s great."

    Output:- Structure: 6/10 - Intro present, but no clear body or conclusion.
    - Delivery: 7/10 - Steady tone inferred, could be livelier.
    - Content: 5/10 - Lacks depth; add details to persuade.
    Suggestions: End with a strong call-to-action like "Support my project!"

4. **Progress Tips**
    Navigate: Go to "Progress" and click "Generate."
    Output (assuming prior scores):
    1. Practice varying sentence length for better delivery.
    2. Use vivid adjectives to boost creativity.
    3. Structure responses with a clear beginning and end.


### Design Decisions
1. **API Choice: OpenAI GPT-3.5-turbo**
        Why: Selected over xAI’s Grok for its proven reliability, extensive     documentation, and strong performance in natural language tasks. GPT-3.5-turbo balances cost and quality, ideal for real-time chat and feedback generation.
        Trade-off: Lacks xAI’s unique perspective but ensures stability for this prototype.
2. **Prompt Engineering**
        Chat Roles: Prompts (e.g., Job Interviewer) are detailed (~100 words) to ensure natural, adaptive conversations. Example: "Ask one natural question at a time, adapting to their response" avoids robotic lists.
        Feedback: Structured prompts (e.g., "Return scores out of 10 with suggestions") guarantee consistent, actionable outputs. Kept concise (~90 words) to fit max_tokens=300.
        Why: Balances realism with efficiency, enhancing learner engagement and usability.
3. **Error Handling**
        Approach: Retries for RateLimitError, requests.Timeout, and APIError (503) with exponential backoff (1s, 2s, 4s). Silent failures for progress scores ensure feedback isn’t disrupted.
        Why: Prioritizes user experience—graceful recovery from API hiccups keeps the app reliable.
4. **Streamlit Framework**
        Why: Chosen for its simplicity and rapid prototyping of interactive web UIs. Features like st.audio and st.spinner enhance UX without complex frontend code.
        Trade-off: Less extensible than a full web framework (e.g., Flask), but sufficient for this scope.
5. **Progress Storage**
        Why CSV: Simple, human-readable format over SQLite/JSON for quick setup and progress tracking via pandas.
        Limitation: Scales poorly for many users—future work could use a database.


### Future Improvements
**Add unit/integration tests for core functions.**
**Support xAI API switching via configuration.**
**Enhance voice feedback with real-time pacing analysis.**
**Multi-language support for broader accessibility.**