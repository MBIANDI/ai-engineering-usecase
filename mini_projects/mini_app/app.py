from flask import Flask, request, jsonify, render_template
from model import gpt4_chain, gpt5_chain
import time
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    user_message = data.get('message')
    city = data.get('city')
    
    if not user_message or not city:
        return jsonify({"error": "Missing message or model selection"}), 400
    ## GPT4 MINI
    start_time = time.time()
    result_gpt4=gpt4_chain.invoke(city) 
    gpt4_mini_time = time.time() - start_time
    if result_gpt4 is not list:
        result4 = []
        result4.append(result_gpt4)
        result4.append({"duration": gpt4_mini_time})
        return jsonify(result4)
    else:
        result4 = result_gpt4
        return jsonify(result4)
    # result = [
    # {
    #     "city_name": "Yaoundé",
    #     "touristic_site_name": "Mvog-Betsi Zoo",
    #     "free": False
    # },
    # {
    #     "city_name": "Yaoundé",
    #     "touristic_site_name": "National Museum of Yaoundé",
    #     "free": False
    # }
    # ]
    #result_gpt4.append({"duration": gpt4_mini_time})

    ## GPT5 MINI
    # start_time = time.time()
    # result_gpt5= gpt5_chain.invoke('Yaoundé') 
    # gpt5_mini_time = time.time() - start_time
    #return jsonify(result4)
    

if __name__ == '__main__':
    app.run(debug=True)