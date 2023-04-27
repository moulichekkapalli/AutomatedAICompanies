from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')


def multilabel_classification(text):
    Planning = ["Using AI generate a foresight process based on emerging trends for planning"
                "Generate insights or insights automation for planning"
                "predict future statistics, modelling tools "
                "Tech scouting or Scouting platform "
                "Identification of emerging markets, technologies, trends and the most innovative companies in the industry"
                "Perform data analytics"
                "Data sources for tech startups/companies from research publications or patent or scientific grants"]
    development = ["Requirement management"
                   "AI driven Product engineering"
                   "Data management with custom AI solutions"
                   "AI based product design algorithms"
                   "AI powered Software testing, test automation"
                   "Data annotation"]
    Production = ["Spotting defects and  quality control during production"
                  "AI based Anomaly detection, detect errors during production"
                  "Autonomous Forecasting, AI based forecasting for production"
                  "AI based Predictive maintenance during production"
                  "Autonomous monitoring of product data during production"
                  "Predictive modelling and optimize productivity during production"
                  "Reducing downtime, maintenance costs and production waste"
                  "Maximize machine uptime and prevent downtime during production"]

    sentence_embeddings = model.encode([text])
    developement_embeddings = model.encode(development)
    planning_embeddings = model.encode(Planning)
    production_embeddings = model.encode(Production)
    developement_similarity = cosine_similarity(
        [sentence_embeddings[0]],
        [developement_embeddings[0]]
    )
    planning_similarity = cosine_similarity(
        [sentence_embeddings[0]],
        [planning_embeddings[0]]
    )
    production_similarity = cosine_similarity(
        [sentence_embeddings[0]],
        [production_embeddings[0]]
    )

    development_cos = developement_similarity[0][0]*100
    planning_cos = planning_similarity[0][0]*100
    production_cos = production_similarity[0][0]*100
    print("development", development_cos)
    print("planning_similarity", planning_cos)
    print("production_similarity", production_cos)

    if development_cos > 10 and planning_cos > 10 and production_cos > 10:
        if development_cos > planning_cos and development_cos > production_cos:
            return 'Development'
        elif planning_cos > development_cos and planning_cos > production_cos:
            return 'Planning'
        else:
            return 'Production'
    else:
        return None
