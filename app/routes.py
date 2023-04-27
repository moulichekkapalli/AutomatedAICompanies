from app.crawler import classifycompany
from app.database import store, check
from flask import render_template, request, Response
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from threading import Thread
from app.utils import fetchCompanies, validateCredentials, validexcel, saveUrls, validexcelsheetname
from app import app

# load model
searchModel = SentenceTransformer('msmarco-distilbert-base-dot-prod-v3')


@app.route('/')
def home():
    return render_template('main.html')


@app.route('/findCompanies', methods=['GET'])
def findCompanies():
    return render_template('findCompanies.html')


@app.route('/results', methods=['POST'])
def search():
    print("In /results API...")
    try:
        if request.method == 'POST':
            keywords = request.form['keywords']
            print("Received Keywords: ", keywords)
            print("Now fetching companies...")
            index = faiss.read_index('app/others/aicompanies.index')
            # read the index file
            relatedCompanies = fetchCompanies(str(keywords), top_k=5,
                                              index=index, model=searchModel)
            print("Fetched companies from db: ", len(relatedCompanies))
            for idx, r in enumerate(relatedCompanies, 1):
                r['idx'] = idx
            #print("Indexing performed on relatedCompanies: ", relatedCompanies)
            return render_template('results.html', relatedCompanies=relatedCompanies, inputKeywords=keywords)
    except Exception as error:
        print("Error in /results API: ", error)


@ app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        isTrue = validateCredentials(username, password)
        if isTrue:
            return render_template('admin.html')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@ app.route('/url-result', methods=['POST'])
def urlResult():
    print("In /url-result API...")
    try:
        if request.method == 'POST':
            url = request.form['url']
            print("Received url: ", url)
            print("Checking if already exists in our db...")
            url_exists = check(url)
            if url_exists:
                modelPred = {"status": 1, "PCClass": url_exists}
            else:
                print("Now crawling...")
                modelPred = classifycompany(str(url))
                print("modelPred: ", modelPred)
                if modelPred["status"] == 1:
                    store(modelPred)
            return render_template('urlResult.html', prediction=modelPred, inputurl=url)
    except Exception as error:
        print("Error in /url-result API: ", error)


@ app.route('/bulkresults', methods=['POST', 'GET'])
def bulkresults():
    print("In bulkresults API...")
    try:
        # verify if the request contains files
        if 'urlFile' not in request.files:
            print("No file found. Returning...")
            return render_template('admin.html', __anchor="addToDb", error="No file found. Please upload excel file.")

        file = request.files['urlFile']

        # check for the empty file without a filename.
        if not file or file.filename == '':
            print("No filename found. Returning...")
            return render_template('admin.html', error="No file found. Please upload excel file.")

        # check for the valid excel extension
        if not validexcel(file.filename):
            print("Not an excel file. Returning...")
            return render_template('admin.html', error="Please upload excel file.")

        if not validexcelsheetname(file):
            print("Excel file doesnot have valid sheet name. Returning...")
            return render_template('admin.html', error="Please upload excel file with valid sheet name.")

        print("File found. Reading file...", file.filename)
        dframe = pd.read_excel(file, 'Sheet1', index_col=None)
        print("dframe.columns: ", dframe.columns)
        if 'url' not in dframe.columns:
            print("No column url found. Returning...")
            return render_template('admin.html', error="Please upload excel file with proper format.")

        print("dframe to list: ", len(dframe['url'].tolist()))
        thread = Thread(target=saveUrls, args=(dframe['url'].tolist(),))
        thread.start()
        return render_template('admin.html', success="The file is accepted. Once URLs are added into database, you will be notified by email.")

    except Exception as error:
        print("Error in /bulstore API: ", error)
        raise Exception(error)
