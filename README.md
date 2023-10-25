# resume
This is a sample notebook and web application which shows how OpenAI Generative AI can be used with Neo4j.  We will explore how OpenAI can be used to retrieve information from Neo4j.


## Setup

## UI
The UI application is based on Streamlit. In this example we're going to show how to run it on a [Google Compute Engine (GCE)](https://console.cloud.google.com/compute/instances) VM.  First, deploy a VM. You need to replace your environment specific values int he command below:

    export VM_INSTANCE_NAME='neo4j-gcp-genai-demo'
    export GCP_PROJECT_NAME=$(gcloud config get-value project)
    gcloud compute instances create $VM_INSTANCE_NAME \
        --project=$GCP_PROJECT_NAME \
        --zone=us-central1-c \
        --machine-type=e2-medium \
        --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
        --maintenance-policy=MIGRATE --provisioning-model=STANDARD \
        --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
        --tags=allow-http,http-server \
        --create-disk=auto-delete=yes,boot=yes,device-name=$VM_INSTANCE_NAME,image=projects/debian-cloud/global/images/debian-11-bullseye-v20230509,mode=rw,size=10,type=projects/$GCP_PROJECT_NAME/zones/us-central1-c/diskTypes/pd-balanced \
        --no-shielded-secure-boot \
        --shielded-vtpm --shielded-integrity-monitoring \
        --labels=goog-ec-src=vm_add-gcloud --reservation-affinity=any
        

Next, login to the new VM instance:

    gcloud compute ssh --zone "us-central1-c" $VM_INSTANCE_NAME --project $GCP_PROJECT_NAME

We're going to be running the application on port 80.  That requires root access, so first:

    sudo su

Then you'll need to install git and clone this repo:

    apt install -y git
    mkdir -p /app
    cd /app
    git clone https://github.com/neo4j-partners/intelligent-app-google-generativeai-neo4j.git
    cd intelligent-app-google-generativeai-neo4j

Login using GCP credentials via the `gcloud` cli.

    gcloud auth application-default login

Let's install python & pip first:

    apt install -y python
    apt install -y pip

Now, let's create a Virtual Environment to isolate our Python environment and activate it

    apt-get install -y python3-venv
    python3 -m venv /app/venv/genai
    source /app/venv/genai/bin/activate

To install Streamlit and other dependencies:

    cd ui
    pip install -r requirements.txt

Check if `streamlit` command is accessible from PATH by running this command:

    streamlit --version

If not, you need to add the `streamlit` binary to PATH variable like below:

    export PATH="/app/venv/genai/bin:$PATH"

Next up you'll need to create a secrets file for the app to use.  Open the file and edit it:

    cd streamlit
    cd .streamlit
    cp secrets.toml.example secrets.toml
    vi secrets.toml

You will now need to edit that file to reflect your GCP and Neo4j credentials. The file has the following variables:

    GCP_PROJECT = "myprojectname" # Your GCP project ID
    GCP_LOCATION = "us-central1" # Location
    TUNED_CYPHER_MODEL = "" # If you have a tuned Codey Model, provide here. Else, Leave it blank
    NEO4J_URI = "neo4j+s://xxxxx.databases.neo4j.io" # Neo4j URL. Include port if applicable
    NEO4J_USER = "neo4j" # Neo4j User Name
    NEO4J_PASSWORD = "Foo12345678" #Neo4j Password

Now we can run the app with the commands:

    cd ..
    streamlit run main.py --server.port=80

On a GCP VM to run on port 80:
- Ensure you are a root or has access to run on port 80
- If you are running `sudo`, you also need to run the `gcloud auth` command above as a sudoer. And ensure that `streamlit` is accessible from the PATH.
- Ensure that the VM has port 80 open for HTTP access. You might need to open that port or any other via firewall-rules. You can use the [following gcloud command](https://cloud.google.com/sdk/gcloud/reference/compute/firewall-rules/create) to open the port. Make sure you replace with relevant values. You also need to add network tags to your VM before executing this command:

    ```bash
    gcloud compute firewall-rules create <rule-name> --allow tcp:80 --source-tags=<list-of-your-instances-name-tags> --source-ranges=0.0.0.0/0 --description="<your-description-here>"
    ```
    
From the UI, you can ask questions like:
1. How many experts do we have on Google Docs?
2. What skills does p06150 have?
3. What are all the companies did p06150 work for?
4. What skills do p06150 and p10343 have in common?
5. Who went to most number of universities and how many did they go to?
6. How many pythonistas are there?
