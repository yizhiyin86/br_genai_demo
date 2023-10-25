from langchain.chains import GraphCypherQAChain
from langchain.graphs import Neo4jGraph
from langchain.chat_models import AzureChatOpenAI
#from langchain.llms import VertexAI
from langchain.prompts.prompt import PromptTemplate
from retry import retry
from timeit import default_timer as timer
import streamlit as st
# from langchain.memory import ConversationBufferMemory


host = st.secrets["NEO4J_URI"]
user = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASSWORD"]

#get azurecredentials
OPENAI_API_TYPE = st.secrets["OPENAI_API_TYPE"]
OPENAI_API_VERSION = st.secrets["OPENAI_API_VERSION"]
OPENAI_API_BASE = st.secrets["OPENAI_API_BASE"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENAI_MODEL_NAME = st.secrets["OPENAI_MODEL_NAME"]
OPENAI_DEPLOYMENT_NAME = st.secrets["OPENAI_DEPLOYMENT_NAME"]


CYPHER_GENERATION_TEMPLATE = """You are an expert Neo4j Cypher translator who understands the question in english and convert to Cypher strictly based on the Neo4j Schema provided and following the instructions below:
1. Generate Cypher query compatible ONLY for Neo4j Version 5
2. Do not use EXISTS, SIZE keywords in the cypher. Use alias when using the WITH keyword
3. Use only Nodes and relationships mentioned in the schema
4. Always enclose the Cypher output inside 3 backticks
5. Always do a case-insensitive and fuzzy search for any properties related search. Eg: to search for a Business Organization name use `toLower(b.orgName) contains 'information technology'`
6. Always use aliases to refer the node in the query
7. Cypher is NOT SQL. So, do not mix and match the syntaxes
8. do not include the text "Answer:" in your response, this is included below simply to help you understand the question and answer components

Schema:
{schema}

Samples:
Question: List data concepts that are used by the Finacle Core Banking software component
Answer: MATCH (a:SoftwareComponent)-[:QUERIES_DATA|READS_DATA|MODIFIES_DATA|CREATES_DATA]->(d:DataConcept) WHERE toLower(a.appName) CONTAINS "finacle core banking" RETURN d.dataConceptName

Question: What applications does each vendor provide? 
Answer: MATCH (v:Vendor)<-[:HAS_VENDOR]-(sw:SoftwareComponent) with v, collect(DISTINCT sw.appName) as apps RETURN v.vendorName, apps

Question: What business processes does app Finacle Core Banking support
Answer: MATCH p1=(sw1:SoftwareComponent)-[:SUPPORTS_TASK]->(task:BusinessTask) WHERE toLower(sw1.appName) CONTAINS "finacle core banking" OPTIONAL MATCH p2=(task)-[:NEXT]->(:BusinessTask)<-[:SUPPORTS_TASK]-(sw1) WHERE toLower(sw1.appName) CONTAINS "finacle core banking" RETURN p1, p2

Question: Which business applications are impacted by CVE-2019-0016
Answer: MATCH p=(:CVE_Impact)<-[:HAS_IMPACT]-(cve:CVE)-[:CVE_AFFECTS]->(:CPE)-[:REFERS_TO]->(:BusinessApplication)-[:MAPS_TO_APP]->(sw:SoftwareComponent) WHERE cve.CVE_ID=CVE-2019-0016 OPTIONAL MATCH p2=(sw)-[:IS_DEPLOYED_WITH]-(:SoftwareComponent) RETURN p,p2

Question: Find CVEs that impact component SAP Sybase IQ
Answer: MATCH p=(:CVE_Impact)<-[:HAS_IMPACT]-(cve:CVE)-[:CVE_AFFECTS]->(cpe:CPE)-[:CPE_IMPACTS]->(sw:SoftwareApplication)-[:REQUIRES_RTE|IS_DEPLOYED_WITH*0..2]-(app:SoftwareApplication) WHERE (toLower(sw.appName) CONTAINS "sap sybase iq" or toLower(app.appName) CONTAINS "sap sybase iq") RETURN p

Question: {question}"""
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)

@retry(tries=2, delay=10)
def get_results(messages):
    start = timer()
    try:
        graph = Neo4jGraph(
            url=host, 
            username=user, 
            password=password
        )
        # chain = GraphCypherQAChain.from_llm(
        #     VertexAI(
        #             model_name=codey_model_name,
        #             max_output_tokens=2048,
        #             temperature=0,
        #             top_p=0.95,
        #             top_k=0.40), 
        #     graph=graph, verbose=True,
        #     return_intermediate_steps=True,
        #     cypher_prompt=CYPHER_GENERATION_PROMPT
        # )
        
        #get azure code in
        chain = GraphCypherQAChain.from_llm(
            AzureChatOpenAI(
                            deployment_name= OPENAI_DEPLOYMENT_NAME,
                            model_name= OPENAI_MODEL_NAME,
                            openai_api_base=OPENAI_API_BASE,
                            openai_api_version=OPENAI_API_VERSION,
                            openai_api_key=OPENAI_API_KEY,
                            openai_api_type=OPENAI_API_TYPE,
                            temperature=0), 
            graph=graph, verbose=True,
            return_intermediate_steps=True,
            cypher_prompt=CYPHER_GENERATION_PROMPT
)

        if messages:
            question = messages.pop()
        else: 
            question = 'How many cases are there?'
        return chain(question)
    except Exception as ex:
        print(ex)
        return "I'm sorry, there was an error retrieving the information you requested."
    finally:
        print('Cypher Generation Time : {}'.format(timer() - start))


