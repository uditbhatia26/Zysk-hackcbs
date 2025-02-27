from flask import Flask, redirect, request, render_template, url_for
import os, markdown
from  langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from questions import questions

load_dotenv()

app = Flask(__name__)

responses = []

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
          
with open("config.md", "r", encoding="utf-8") as file:
    config_data = file.read()

example_output = config_data

# Create the model and prompt
prompt = PromptTemplate.from_template("""
You are an AI financial advisor. Your goal is to generate a personalized financial analysis and investment strategy based on user-provided details about their financial goals, income, risk tolerance, and investment preferences.

User Information: {user_options}

Example Output:
<output>
{example_output}
</output>
""")


llm = ChatGroq(
    model='llama-3.3-70b-versatile',
    api_key=groq_api_key,
    max_tokens=8092,
    )

chain = prompt | llm 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    responses = request.form.getlist('responses')
    generated_response = chain.invoke({"user_options": responses, "example_output": example_output})
    generated_text = generated_response.content if hasattr(generated_response, "content") else str(generated_response)
    markdown_response = markdown.markdown(generated_text) 

    return render_template('analysis.html', model_response=markdown_response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
