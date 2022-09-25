from flask import Flask, render_template, request
import nltk
from nltk.corpus import wordnet
nltk.download('wordnet')
nltk.download('omw-1.4')
import re

app = Flask(__name__)

import cohere
from cohere.classify import Example
co = cohere.Client('CSrnecfjDvIop7lxfsLyR226fQ6wTmQe7rpGmMKG')

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/data',methods = ['POST'])
def hello():
    if request.method == 'POST':
        #recieve the inputted article
        form.data=request.form
        inputted = form.data['Article']

        #divide the article into sentences
        sentences = [" "]
        for i in range(len(inputted)):
            if inputted[i] == ".":
                sentences = inputted.split(".")
        if len(sentences) > 1:
            sentences.pop()

        #analyze the sentiment of each sentence, find average sentiment across the article
        predictions = []
        average_sentiment = 0
        for sentence in sentences:
            response = co.classify(
                model='e1fb5f67-7289-4ef7-a6c5-ac474399566a-ft',
                inputs=[sentence])
            prediction = response.classifications[0].prediction
            print(response.classifications[0].prediction)
            predictions.append(prediction)
            average_sentiment += int(prediction)
        average_sentiment = average_sentiment / len(predictions)

        #find most inflammatory sentences
        offenders =[]
        if average_sentiment >= 0.5:
            sentiment = "Highly Positive"
            for count in range(len(predictions)):
                if int(predictions[count]) == 1:
                    offenders.append(sentences[count])
                    if len(offenders) > len(sentences)-2:
                        break
        elif average_sentiment > 0.25:
            sentiment = "Slightly Positive"
            for count in range(len(predictions)):
                if int(predictions[count]) == 1:
                    offenders.append(sentences[count])
                    if len(offenders) > len(sentences)-2:
                        break
        elif average_sentiment > -0.25:
            sentiment = "Neutral"
        elif average_sentiment > -0.5:
            sentiment = "Slightly Negative"
            for count in range(len(predictions)):
                if int(predictions[count]) == -1:
                    offenders.append(sentences[count])
                    if len(offenders) > len(sentences)-2:
                        break
        else:
            sentiment = "Highly Negative"
            for count in range(len(predictions)):
                if int(predictions[count]) == -1:
                    offenders.append(sentences[count])
                    if len(offenders) > len(sentences)-2:
                        break
        
        #find and replace emotionally charged words
        inputteds = replacer(inputted)
        inputteds = inputteds.split()
        final = []
        for word in inputteds:
            response = co.classify(
                model='e1fb5f67-7289-4ef7-a6c5-ac474399566a-ft',
                inputs=[word])
            prediction = int(response.classifications[0].prediction)
            print(word, prediction)
            if prediction == 1 or prediction == -1:
                try:
                    word = wordnet.synsets(word)[0].lemmas()[1].name()
                except IndexError:
                    errors = True
            final.append(word)
        inputteds = " ".join(inputteds)
        final = " ".join(final)
        if sentiment == "Neutral":
            return render_template('neutral.html', predictions=predictions, average=sentiment, inputted = inputted, final = final)
        else:
            return render_template('results.html', predictions=predictions, average=sentiment, inputted = inputted, final = final, offenders = offenders)
        

def replacer(inputs):
    listy = ['himself','herself','democrat','republican','he','she','her','his','woman','man','female','male','liberal','conservative','socialist','communist','capitalist','black','white','latino','asian','african american','hispanic']
    replace = ['themself','themself','party member','party member','they','they','their', 'their', 'person','person','person','person','hidden','hidden','hidden','hidden','hidden','race','race','race','race','race','race']
    inputs = re.sub('([.,!?()])', r' \1 ', inputs)
    inputs = re.sub('\s{2,}', ' ', inputs)
    words = inputs.split()
    new_input = []  
    for i in words:
        for possible in range(len(listy)):
            if i.lower() == listy[possible]:
                i = replace[possible]
            if i.lower() == listy[possible]+"s":
                i = replace[possible]+"s"
        new_input.append(i)
    new_input = " ".join(new_input)
    new_input = re.sub(r'\s+([?,.!"])', r'\1', new_input)
    return new_input
