# import nltk
# nltk.download('averaged_perceptron_tagger')

# import nltk
# nltk.download('all')

# import nltk
# nltk.download('punkt')


# from pymilvus import connections, CollectionSchema, FieldSchema, DataType, Collection
# from sentence_transformers import SentenceTransformer

# # Step 1: Connect to Milvus
# connections.connect("default", host="localhost", port="19530")
# print(connections)

# from pymilvus import MilvusClient
# client = MilvusClient("./milvus_demo.db")


# from pymilvus import (
#     connections,
#     utility,
#     FieldSchema,
#     CollectionSchema,
#     DataType,
#     Collection,
# )

# connections.connect("default", host="localhost", port="19530")

# print("connected...")

from pymilvus import MilvusClient
client = MilvusClient("./milvus_demo.db")