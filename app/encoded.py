import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from app.database import pg_connection
import pandas as pd
import pandas.io.sql as psql


def encodeandindex():
    print("In encode and index method")
    try:
        model = SentenceTransformer('msmarco-distilbert-base-dot-prod-v3')
        connection = pg_connection()
        if not connection:
            raise Exception('Error connecting to db')
        connection.cursor()
        print("Db connected now reading companyinfo...")
        # reading the data from the database to the dataframe
        df = psql.read_sql("select * from companyinfo", connection)
        print("Companyinfo extracted from db...")
        df = df[['url', 'extracteddata', 'category', 'title', 'summary']]
        df.reset_index(drop=True, inplace=True)
        # save dataframe to pickle file
        df.to_pickle('app/others/companiesdata.pkl')
        print("Encoding dataframe...")
        # encoding the data into the vectors
        encoded_data = model.encode(df.extracteddata.tolist())
        encoded_data = np.asarray(encoded_data.astype('float32'))
        print("Indexing encoded data...")
        # indexing the encoded data
        index = faiss.IndexIDMap(faiss.IndexFlatIP(768))
        ids = np.array(range(0, len(df)))
        ids = np.asarray(ids.astype('int64'))
        index.add_with_ids(encoded_data, ids)
        print("Saving the indexes into a file...")
        # saving the indexes into the file
        faiss.write_index(index, 'app/others/aicompanies.index')

    except Exception as error:
        print("Error in encodeandindex method: ", error)

    finally:
        if connection is not None:
            connection.close()
