from richardsonfood import app
from flask import render_template,flash,url_for,request,session
import os
import sys
import requests
# If you are using a Jupyter notebook, uncomment the following line.
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import os
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import http.client, urllib.request, urllib.parse, urllib.error, base64

# Variables
_key = '55449c9e8cd844f9a17562e042f8088d' # Here, paste your primary key
_maxNumRetries = 10


@app.route('/image_rec')
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

@app.route('/classify',methods = ["GET","POST"])
def classify():
    _url = 'https://imagerec.cognitiveservices.azure.com/vision/v3.0/tag'
    # Read the image into a byte array
    # image_data = open(image_path, "rb").read()

    image_data = request.files["file"].read()
    headers = {'Ocp-Apim-Subscription-Key': _key,
               'Content-Type': 'application/octet-stream'}
    params = {'visualFeatures': 'Categories,Description,Color'}
    response = requests.post(
        _url, headers=headers, params=params, data=image_data)
    response.raise_for_status()

    # The 'analysis' object contains various fields that describe the image. The most
    # relevant caption for the image is obtained from the 'description' property.
    analysis = response.json()
    print(analysis)
    # image_caption = analysis["description"]["captions"][0]["text"].capitalize()
    # Display the image and overlay it with the caption.
    image = Image.open(BytesIO(image_data))
    fig = Figure(figsize=(5, 5))
    axis = fig.add_subplot(1, 1, 1)
    axis.axis('off')
    # axis.set_title(image_caption, size="x-large", y=-0.1)
    axis.imshow(image)

    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)

    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    reuslt = []
    for i in range(0, 4):
        tag = analysis['tags'][i]
        temp = []
        temp.append(tag['name'])
        temp.append('{}%'.format(round(tag['confidence'] * 100)))
        reuslt.append(temp)
    return render_template("/image_rec.html", image=pngImageB64String, cats= reuslt)