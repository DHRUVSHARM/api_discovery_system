# api_discovery_system
a web based api discovery system that allows users to query apis based on various functional parameters 
Screenshots of the working system can be viewed by clicking on design_document file

## Introduction
This document outlines the design for the API Discovery System for CSCI.724.01 - Web Services & Service Oriented Computing by Dhruv Sharma.

## Data Structure and Query System
The data model is structured with the help of Pydantic models in a FastAPI application. The following models are specified in `models.py`:

### Models

- **APIModel:** Represents a Web API with attributes such as title, summary, rating, name, and more. It includes properties like type, download URLs, modification dates, tags, categories, protocols, deployment, documentation, and usage constraints.
- **APIUsed:** Represents an API used within a mashup, including the API's name and URL. This model tracks which APIs are utilized by different mashups.
- **MashupModel:** Represents a mashup, a composite application using data from one or more APIs. It includes fields like title, summary, description, tags, and a list of `APIUsed` instances. Additional fields such as `useCount` and `numComments` store usage statistics and engagement metrics.

## Query System
The query system allows users to select the query type and presents forms based on the parameters for querying. The system has six endpoints:

### Query Endpoints

1. **Search APIs by Criteria:** Search APIs based on criteria like `updated_year`, protocols, category, `min_rating`, `max_rating`, and tags. Uses regex, partial, and case-insensitive matching.
   - **Default size:** 10000

2. **Search Mashups by Criteria:** Discover mashups based on `updated_year`, used_apis names, and tags.
   - **Default size:** 10000

3. **Search APIs by Keywords:** Perform keyword searches across multiple fields (title, summary, description) of APIs.
   - **Default size:** 1000

4. **Search Mashups by Keywords:** Similar to the 3rd query but focused on mashups. Searches for keywords in title, summary, or description.
   - **Default size:** 1000

5. **Top Used APIs:** Identify the top K most frequently used APIs in mashups.
   - **Default size:** 10

6. **Top API-rich Mashups:** Rank mashups based on the number of distinct APIs they utilize.
   - **Default size:** 10

The default size limits the number of records inspected. The last two queries have an optional K parameter (default is 10).

Readme for local installation and testing

 Wehave the 4 data files provided ( apis , mashups , members and widgets)
 Steps to run :
 # Install the requirements:
 pip3 install-r requirements.txt
 # Configure the location of your MongoDB database or use local database ( what i used for testing was the connection string : localhost:27017) :
 export
 MONGODB_URL="mongodb+srv://<username>:<password>@<url>/<db>?retryWrites=true&w=
 majority"
 # Start the service:
 Python-m app
 # run the parsing.py file
 This will parse the files and store them in dictionaries and use the services from our app to
 populate the database ( local mongo by default)
 # the index.html is served as a static file by our fastapi app
 So just go to http://localhost/static/index.html , this is where you will find the query
 system. make sure uvicorn app is still runnin
