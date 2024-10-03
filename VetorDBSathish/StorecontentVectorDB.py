from pymilvus import connections, CollectionSchema, FieldSchema, DataType, Collection
from sentence_transformers import SentenceTransformer

# Step 1: Connect to Milvus
connections.connect("default", host="localhost", port="19530")

# Step 2: Define the schema for the collection
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="content", dtype=DataType.STRING),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),  # Adjust based on the embedding model
]

schema = CollectionSchema(fields=fields, description="CV collection")
collection = Collection(name="cv_collection", schema=schema)

# Step 3: Define the CV content
cv_content = """
K.BHARATHIDHASAN
20/41- MH Colony,
Madha Kovil Street,
Aminithakarai, Email ID: kv.bharathidhasan@gmail.com
Chennai-29. Contact No: + 91-8124289524
Career Objective:
Seeking a position to utilize my skills and abilities in the Information Technology industry that offers professional growth while being resourceful, innovative and flexible, willing to work as a key player in challenging and creative environment.
Summary of Experience:
• Having 7.6 Years of experience in Microsoft technology(C#.Net).
• Good working knowledge on Application development.
• Professional in MS SQL server 2008 Relational Database.
• Experienced in designing and development of Web applications.
• Excellent team player having good communication and interpersonal skills.
Professional Experience:
• Working as a Sr. Tech Associate in Flexicode Technologies Private Limited; Chennai from 01st March 2018 to Till Date.
• Worked as a Software Engineer in Attune Technologies Private Limited; Chennai from 01st August 2014 to 28th Feb 2017.
• Worked as a Junior Developer in Purple Infotech Private Limited; Chennai from 19th November 2012 to 10th February 2014.
"""

# Step 4: Generate embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(cv_content)

# Step 5: Insert the CV content and its embedding into the collection
data = [
    [cv_content],  # content
    [embedding.tolist()]  # embedding
]

collection.insert(data)

# Step 6: Query the collection for similar CVs (using a sample query)
query_embedding = model.encode("Information Technology skills")  # Modify as needed
query_result = collection.query(
    data=[query_embedding.tolist()],
    n_results=5  # Return top 5 similar results
)

# Step 7: Display the results
for result in query_result:
    print("Retrieved CV Content:", result["content"])
