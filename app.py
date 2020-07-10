from flask import render_template,request,Flask
import requests
from PIL import Image
from io import BytesIO
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import base64

app = Flask(__name__)

"""FIRST RESOURCE: MAIN PAGE
Requests user to select and upload an image,
which gets stored in image_path under Capture.png
"""
@app.route('/')   
def image_rec():
    image_path = './static/image/Capture.png'
    image_data = open(image_path, "rb").read()
    image = Image.open(BytesIO(image_data))
    fig = Figure(figsize=(5, 5))
    axis = fig.add_subplot(1, 1, 1)
    axis.axis('off')
    axis.imshow(image)
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)

    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    return render_template("/image_rec.html",image =pngImageB64String)




"""SECOND RESOURCE: CLASSIFICATIONS RESULTS PAGE 
Function that uses Azure's Custom Vision resource to classify an image
Output: The image that was uploaded and the top 4 results
Methods
    POST: client is providing an image to the server
    GET: client obtains classification results from the server
"""
@app.route('/classify', methods = ["GET", "POST"]) 
def classify():
    _key = 'db67eaca8c4b42669146d4352d5d0f8e'  #Azure's custom vision resource API
    _maxNumRetries = 10
    #This endpoint will look at the second iteration of the trained/custom vision classifier - prediction
    _url = 'https://hhaggancvs.cognitiveservices.azure.com/customvision/v3.0/Prediction/7e067a88-2755-42ef-9302-b729c90001b5/classify/iterations/Iteration2/image?'
    
    # Read the image into a byte array
    # image_data = open(image_path, "rb").read()

    image_data = request.files["file"].read() #Flask object that reads a file (image) by a form
    headers = {
        # Request headers: they represent meta-data associated with the API request and response
        #Format: dictionary
        'Content-Type': 'application/json',
        'Prediction-key': _key,
    }

    params = {
        # Request parameters
        'application': 'classifyModel',
    }

    response = requests.post(
        _url, headers=headers, params=params, data=image_data)
    response.raise_for_status()

    # The 'analysis' object contains various fields that describe the image. The most
    # relevant caption for the image is obtained from the 'description' property.
    analysis = response.json()
    print(analysis)
    image = Image.open(BytesIO(image_data))
    fig = Figure(figsize=(5, 5))
    axis = fig.add_subplot(1, 1, 1)
    axis.axis('off')
    axis.imshow(image)

    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)

    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    #Obtain the four top predictions in this format: [['fruit','93%'],['pineapple','92%']]
    reuslt = []
    for i in range(0, 4):
        tag = analysis['predictions'][i]
        temp = []
        temp.append(tag['tagName'])
        temp.append('{}%'.format(round(tag['probability'] * 100)))
        reuslt.append(temp)
    return render_template("/image_rec.html", image=pngImageB64String, cats= reuslt)

#Make the server (IP) publicly available (deployment)
if __name__ == "__main__":
    app.run(host="0.0.0.0")