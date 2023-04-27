import pickle
from urllib.parse import urlparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import nltk
# nltk.download('omw-1.4')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from langdetect import detect
import tldextract
from deep_translator import GoogleTranslator
from nltk.tokenize import word_tokenize
from app.multiclass_classifier import multilabel_classification
#DetectorFactory.seed = 0
ls = WordNetLemmatizer()
stops = set(stopwords.words("english"))

# init
visited = []
crawledDataList = []

# load model
loaded_model = pickle.load(open('app/others/model_svm_update.pkl', 'rb'))
Tfidf_vect = pickle.load(open("app/others/vector_tfidf_updated.pickel", "rb"))


def lemming(text):
    # coverting into tokens
    text_tokens = word_tokenize(text)
    filtered_words = [word for word in text_tokens if word not in stops]
    lemTxt = [ls.lemmatize(word) for word in filtered_words]
    return " ".join(lemTxt)


# Pre-processing function
def preprocess(text):
    text = str(text)
    # removal of punctuations
    text = re.sub(r'[^\w\s]', '', text)
    # removal of removal of whitepaces and tabs
    text = re.sub('\s+', ' ', text)
    # removal of emojis
    rem_emojis = deEmojify(text)
    return rem_emojis


def deEmojify(text):
    regrex_pattern = re.compile(pattern="["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


def irrelavantPage(page):
    irrelavantPages = ["blog", "jobs", "openings", "careers", "privacy", "policy", "legal", "imprint",
                       "mailto", "demo", "support", "pdf", "team", "contact", "terms", "conditions", "case-studies"]
    return any(word in page for word in irrelavantPages)


def pageBelongsTo(company, page):
    schemeExists = urlparse(page).scheme
    pageLink = urlparse(page).netloc
    if schemeExists and domain(company) == domain(pageLink) and not irrelavantPage(page):
        return True
    else:
        if page.startswith('/') and not irrelavantPage(page):
            return True
        else:
            return False


def domain(url):
    return tldextract.extract(url).domain


def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False


def eliminateHeaderAndFooter(soup):
    soup.find('footer').decompose() if soup.find('footer') else soup
    soup.find(class_='footer').decompose() if soup.find(
        class_='footer') else soup
    for nav in soup.find_all('nav'):
        if nav:
            nav.decompose()
    soup.find(class_='nav').decompose() if soup.find(class_='nav') else soup
    return soup


def crawl(company):
    try:
        print("Company: ", urlparse(company).scheme +
              "://" + urlparse(company).netloc)
        company = urlparse(company).scheme + "://" + urlparse(company).netloc
        soup = extractSoup(company)
        if soup['status'] == 1:
            title = domain(company)
            pages = soup["data"].find_all("a")
            extractedData = crawlSubPages(company, pages)
            summary = extractMetaDescription(soup["data"])
            extractedData = preprocess(extractedData)
            if len(str(extractedData).split(" ")) < 100:
                return {"data": "Not enough content extracted for prediction. ", "status": 0}
            return {"status": 1, "data": extractedData, "summary": summary, "title": title}
        else:
            print("No soup found for " + urlparse(company).netloc)
            return {"status": 0, "data": soup['data']}
    except Exception as error:
        print("Error while crawling: ", error)
        return {"status": 0, "data":"Cant able to get the content from website " }


def extractMetaDescription(soup):
    isMetaDescAvailable = soup.find("meta", {"name": "description"}) if soup.find(
        "meta", {"name": "description"}) else soup.find("meta", property="og:description")
    if isMetaDescAvailable:
        return isMetaDescAvailable['content']
    else:
        return ''


def crawlSubPages(company, pages):
    try:
        pagecontent = ''
        for page in pages:
            page = page.get("href")
            page = page if uri_validator(
                page) else company+page if page else company
            if page not in visited and (pageBelongsTo(company, page)):
                print("Page: ", page)
                pagecontent += ' '+extractPageContent(page)
                print("Page content extracted and copeid...")
                visited.append(page)
        return pagecontent
    except Exception as error:
        print("Error in crawling sub pages: "+error)
        raise Exception(error)


def extractSoup(link):
    try:
        page_content = requests.get(
            link, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(page_content.content, 'html.parser')
        return {"data": soup, "status": 1}
    except requests.ConnectionError as e:
        return {"data": "Invalid URL.", "status": 0}
    except requests.HTTPError as e:
        return {"data": "Unfortunately HTTP Error occured.", "status": 0}
    except requests.URLRequired as e:
        return {"data": "URL Required.", "status": 0}
    except requests.Timeout as e:
        return {"data": "Unfortunately Timeout Error occured.", "status": 0}
    except requests.RequestException as e:
        return {"data": e, "status": 0}


def extractRelevantTextFromSoup(soup, relevantTags):
    texts = soup.findAll(relevantTags)
    return " ".join(t.text for t in texts)


def extractPageContent(page):
    pagesoup = extractSoup(page)
    if pagesoup["status"] == 1:
        pagesoup = eliminateHeaderAndFooter(pagesoup["data"])
        extractedText = extractRelevantTextFromSoup(
            pagesoup, ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
        srcLang = detectLang(extractedText)
        if(srcLang == 'en'):
            return extractedText
        else:
            return translate(srcLang, extractedText) if extractedText else ''
    else:
        return ''


def detectLang(text):
    return detect(text) if text else None


def translate(srcLang, text):
    try:
        return GoogleTranslator(source=srcLang, target='en').translate(text[:4999])
    except:
        return "Unable to translate"


def classifyAIOrNonAICompany(compTxt):
    tokenisedtext = [compTxt]
    vectorized_input_data = Tfidf_vect.transform(tokenisedtext)
    prediction = loaded_model.predict(vectorized_input_data)
    return prediction


def classifycompany(url):
    compData = crawl(url)
    if compData["status"] == 1:
        lemtext = lemming(compData["data"])
        isAI = classifyAIOrNonAICompany(lemtext)
        if(isAI):
            PCClass = multilabel_classification(compData["data"])
            if PCClass is None:
                return {"compData": compData, "status": 3, "data": "Not in product creation"}
            return {"title": compData["title"], "summary": compData["summary"], "data": compData["data"], "url": url, "PCClass": PCClass, "status": 1}
        else:
            return {"data": "Non AI company", "status": 2}
    else:
        print("Error: ", compData["data"])
        return {"data":  compData["data"], "status": 0}
