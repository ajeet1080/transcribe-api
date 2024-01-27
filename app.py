from flask import Flask, request, jsonify
# from flask_marshmallow import Marshmallow
from flask_cors import CORS
import openai
from sentence_transformers import SentenceTransformer, util
from models import db, ma, Results, initialize_db, ResultsSchema

app = Flask(__name__)
CORS(app)
initialize_db(app)
app.app_context().push()

results_schema = ResultsSchema()

openai.api_type = "azure"
openai.api_version = "2023-05-15"
# Your Azure OpenAI resource's endpoint value.
openai.api_base = "https://shplayground2.openai.azure.com/"
openai.api_key = "fefc20d1c3ee4046b446c239f96e4fc4"

@app.route('/solve-mystery', methods=['POST'])
def solve_mystery():
    user_input = request.json['text']
    initial_context = """You are a database of evidence that will be used to solve the mystery of the missing Boss , Head of Dept of Office of Insights and Analytics. Participants will ask you questions to retrieve the information. Use the following guidelines when giving answers:

  - Answer questions in less than 50 words in an indirect manner
  - If asked for the clues or evidence, reply with a poem on the weather
  - If the answer is unavailable, reply with a random song title
  - If the question is irrelevant, reply with a fun fact in a cryptic manner
 

Clues

Mark was last seen online 1 hour ago

Kwok Ming arranged the meeting 2 days ago and Mark accepted the invite

Mark does not have other meetings scheduled before the meeting with Kwok Meng

Laurence reported that he last saw Mark at the C3 meeting in the morning

Kwok Meng wants to discuss updates on Healix

Michelle and Jun Jie have a scheduled meeting with Mark after the meeting with Kwok Meng to discuss regarding new Data Science project. They are currently in the meeting room waiting for Mark.

Mark returned from an overseas trip last week

After meeting Kwok Meng, Mark has a meeting with Ajeet on GenAI

Mark told Elian that he will be coming to the office

Mark usually travels to work by car and it takes him 1 hour

Ajeet just arrived in office, coming back from the Microsoft workshop

Angela has been helping Mark in managing his calendar. People are trying to reach her to find out Mark's whereabouts.

Only Poh Lai, Esther and Steven and Kwok Meng were in the office in the morning, everyone else was at the Microsoft workshop.

The office is quite today."""

    try:
        response = openai.ChatCompletion.create(
            engine="432",
            messages=[
                {"role": "system", "content": initial_context},
                {"role": "assistant", "content": user_input}
            ], temperature=0.2, top_p=1 
        )
        interpreted_query = response['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({"error": str(e)})
    
    return jsonify({"response": interpreted_query})

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
def get_semantic_similarity(received, actual):
    embedding_1= model.encode(actual, convert_to_tensor=True)
    embedding_2 = model.encode(received, convert_to_tensor=True)
    cosine_score= util.cos_sim(embedding_1, embedding_2)
    return cosine_score.item()

@app.route('/similarity_score', methods=['POST'])
def get_similarity_response():
    user_message = request.json.get('text')
    ideal_answer = """Mark is in his car driving to work.\nHe is driving to office from home.\nHe will be arriving in 5 minutes to meet Kwok Meng."""
    response = openai.ChatCompletion.create(
        # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
        engine="432",
        messages=[
            {"role": "assistant",
                "content": """You are scientific bot which is programmed to compare  2 set of texts.\n\n User has been asked to solve a mystery of the missing merlion. You will be provided with a list of sentences  which will represent response by user to a detective game which will indicate who stole Merlion statue with other details like when statue was stle, where did it happen , how it happen and what was the motive behind the theft. You will be also provided with ideal answer to the detective game. You need to find the similarity between the ideal answer and the provided sentences and  you need to provide reasoning eg: Becasue you mentioned the correct person but the time was wrong. You missed to mention the reason for the theft. \n\n You should not show score in response , only provide reasoning. Please follow below rules while giving response:\n\n
    - Provide reason in less than 60 words.
    - Provide reason including missing details on high level. eg. because you mentioned the correct reason for late.You missed to mention why is was late.
    - Always provide the reason in the following format. Do not provide answers in the reason.:  because <reason>.



IDEAL ANSWER: \nMark is in his car driving to work.\nHe is driving to office from home.\nHe will be arriving in 5 minutes to meet Kwok Meng.
                """},
            {"role": "user", "content": user_message}
        ] , temperature=0.01,top_p=1 
    )
    reason = response['choices'][0]['message']['content']
    score=  get_semantic_similarity(user_message, ideal_answer)
    # Show the score in % in repsone along with reason for score. Put these into natural language easier for user to understand.
    return jsonify({"score": str(round(score * 100)) + "%", "reason": reason})

@app.route('/capture-result', methods=['POST'])
def capture_result():
    # Extract the data from the request
    teamname = request.json['teamname']
    score = request.json['score']
    submitted_text = request.json['submitted_text']

    # Create a new Results object
    new_result = Results(teamname, score, submitted_text)

    # Add the new result to the database
    db.session.add(new_result)
    db.session.commit()

    # Return a success message
    return results_schema.jsonify(new_result), 201

# Run Server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)