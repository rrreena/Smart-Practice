import streamlit as st

st.set_page_config(page_title="Smart Practice", page_icon="🎹")

import time
from openai import OpenAI

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except (FileNotFoundError, KeyError):
    st.error("OpenAI API key not found. Please create a `.streamlit/secrets.toml` file with your key.")
    st.info("Example `secrets.toml`:\n```\nOPENAI_API_KEY = \"sk-xxxxxxxxxx\"\n```")
    st.stop()

# add title, desc, pg config
# possible subheaders 

st.title("Practice Planner")



# prompt = f"""You are a professional music teacher. You are thoughtful and patient. Your students have trouble practicing every day 
#         and need your help. Please suggest a week-long practice plan for your students that tells them what and how long they should practice each day.
#         Additionally, you may suggest actual pieces (or excerpts) based on what your students have already played, or pieces and excerpts that help strengthen
#         your students' abilities and reach their goals. For example, if a student is struggling with expressing themselves while playing, you could suggest Saint-Saëns's "The Swan."
#         Does not have to be famous concertos or exercises, just as long as they help the students achieve their goals.
#         Other than the plan, do not give any feedback, questions, or commentary. No title is necessary. Be specific when generating the plan, and make sure you specify exactly what 
#         piece(s) your student should play, don't just give a generalized answer.
#         """
prompt = f"""
You are a professional, patient, and thoughtful music teacher. Your students often struggle to practice consistently,
and they rely on you to create motivating, structured weekly practice plans.

Please generate a **7-day practice plan** that tells students **what to practice** and **how long to practice** each day.

Each day’s entry should:
- Include clear **Markdown headings** (e.g., "# Day 1 – Focus on Tone and Expression")
- Use **bulleted or numbered lists** for exercises, pieces, and time allocations
- Optionally include *short italicized notes* with encouragement or reminders
- Be specific about pieces or excerpts to practice (avoid vague suggestions)

Suggest **actual repertoire** or **short excerpts** that address the student’s goals.
For example, if a student struggles with expression, you might recommend Saint-Saëns's *“The Swan.”*

**Formatting Rules:**
- Use proper Markdown structure with headings, bold, and italics where appropriate.
- Do **not** include any commentary, greetings, or explanations outside the plan.
- Do **not** include a title at the top; start directly with "### Day 1".
- Make sure spacing and indentation are clean for Markdown rendering.
- The days ("Day 1", "Day 2," etc.) should be headers. 

Your final response should be cleanly formatted for direct display in a Streamlit Markdown block.
"""


if 'practice_plan' not in st.session_state: 
    st.subheader("Create Your 7-Day Practice Plan")
    st.markdown("Fill out the details below, and our AI music teacher will build a custom plan for you!")
    with st.container(border=True):
        with st.form(key = "planForm"): 
            col1, col2 = st.columns(2)
            with col1:
                instrument = st.text_input("What instrument do you play? ", placeholder="i.e. Piano, Violin, French Horn...")
            with col2:
                options = ["Beginner", "Intermediate", "Advanced", "Professional"]
                level = st.selectbox(
                    "Choose your skill level: ", options
                )
            goals = st.text_area("What are your goals?", placeholder="i.e. Being able to vibrato smoothly and sight read new pieces...")
            recentPieces = st.text_area("What recent pieces or excerpts have you played? ", placeholder='i.e. Fur Elise, Tchaikovsky\'s "Symphony No.5"...')
            practiceTime = st.slider(
                "How many minutes can you practice each day?", # Should it be day or week?
                min_value = 15,
                max_value = 240,
                value = 45,
                step = 5
            )
            submitted = st.form_submit_button("Submit")

    # submit button

    if submitted:
        # check if user has filled out goals, level, etc., send st.error, else: 

        with st.spinner("Your plan is being created... 🎼"):
            try:
                userPrompt = f"""I play the {instrument} and am a(n) {level} player. 
                I wish to reach my goal(s) of {goals}, and can practice {practiceTime} minutes every day.
                Recently, I've played {recentPieces}. Please help me create a practice plan.
                """ # from user perspective 
                
                response = client.chat.completions.create(
                    model = "gpt-3.5-turbo-0125",
                    messages = [{"role": "system", "content": prompt},
                    {"role": "user", "content": userPrompt}]

                )
                plan = response.choices[0].message.content
                st.session_state.practice_plan = plan
                st.session_state.instrument = instrument.capitalize()
                
                st.rerun()
            except Exception as e:
                st.error(f"ERROR {e}")

else:
    st.header(f"Your 7-Day {st.session_state.get('instrument', 'Practice')} Plan")
    newPlan = st.button('New plan')

# --- Display Output--- 

# Display the students plan *outside* of tghe form, using session_state
#Were putting it outside of the form so it doesn't disappear if the user interacts with anything else on the website

# if practice plan exists in session --> if 'practice_plan' in st.session_state: 

    #display the plan [using markdown - st.markdown(st.session_state.practice_plan)]
    st.divider()
    st.markdown(st.session_state.practice_plan)
    
    with st.container(border=True): 
        st.markdown("###### How is your practice plan? ")
        feedbk = st.feedback(options = "faces")
        if feedbk != None:
            st.success("Thank you for your feedback!")
#if the student hits a make new plan button --> if st.button('newPlan'): 
    if newPlan:
        #clear the old plan and start over --> del st.session_state.practice_plan (deleting)
        del st.session_state.practice_plan
        #reset --> st.rerun()
        if 'instrument' in st.session_state:
            del st.session_state.instrument
        st.rerun()

