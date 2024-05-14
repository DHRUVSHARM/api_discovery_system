import os
from fastapi import FastAPI, Body, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from typing import List, Optional

import motor.motor_asyncio
import models
import uvicorn
from pymongo import ReturnDocument
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="API and Mashup Data Management", description="Manage APIs and Mashups data."
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# endpoints for populating database
@app.get("/")
async def root():
    return {"message": "API and Mashup Management Service is ready!"}


@app.post("/api", response_description="Add a new API", response_model=models.APIModel)
async def add_api(api: models.APIModel = Body(...)):
    api = jsonable_encoder(api, exclude=["id"])
    new_api = await api_collection.insert_one(api)
    created_api = await api_collection.find_one({"_id": new_api.inserted_id})
    return created_api


@app.get(
    "/apis", response_description="List all APIs", response_model=List[models.APIModel]
)
async def list_apis():
    apis = await api_collection.find().to_list(10)
    return apis


@app.post(
    "/mashup",
    response_description="Add a new Mashup",
    response_model=models.MashupModel,
)
async def add_mashup(mashup: models.MashupModel = Body(...)):
    mashup = jsonable_encoder(mashup, exclude=["id"])
    new_mashup = await mashup_collection.insert_one(mashup)
    created_mashup = await mashup_collection.find_one({"_id": new_mashup.inserted_id})
    return created_mashup


@app.get(
    "/mashups",
    response_description="List all Mashups",
    response_model=List[models.MashupModel],
)
async def list_mashups():
    mashups = await mashup_collection.find().to_list(10)
    return mashups


# endpoints for queries

# **************************** 1st query **********************************


@app.get("/apis/search-by-criteria")
async def search_apis_by_criteria(
    updated_year: Optional[int] = None,
    protocols: Optional[str] = None,
    category: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    tags: Optional[str] = None,
):
    query = {}
    if updated_year:
        query["updated"] = {"$regex": f"^{updated_year}"}
    if protocols:
        query["protocols"] = {
            "$regex": protocols.strip(),
            "$options": "i",
        }  # Case-insensitive match
    if category:
        query["category"] = {"$regex": category.strip(), "$options": "i"}
    if min_rating is not None:
        query["rating"] = {"$gte": min_rating}
    if max_rating is not None:
        query["rating"] = {**query.get("rating", {}), "$lte": max_rating}
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        query["tags"] = {"$in": tags_list}  # Match any of the tags

    apis = await api_collection.find(query).to_list(10000)
    return [{"name": api["name"]} for api in apis]


# **************************** 2nd query **********************************


@app.get("/mashups/search-by-criteria")
async def search_mashups_by_criteria(
    updated_year: Optional[int] = Query(None),
    used_apis: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
):
    query = {}
    if updated_year:
        query["updated"] = {"$regex": f"^{updated_year}"}
    if used_apis:
        used_apis_list = [api.strip() for api in used_apis.split(",") if api.strip()]
        query["apis.name"] = {"$in": used_apis_list}  # Match any of the used APIs
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        query["tags"] = {"$in": tags_list}  # Match any of the tags

    mashups = await mashup_collection.find(query).to_list(10000)
    return [{"title": mashup["title"]} for mashup in mashups]


# **************************** 3rd query **********************************


@app.get("/apis/search-by-keywords")
async def search_apis_by_keywords(keywords: List[str] = Query(...)):
    query = {
        "$and": [
            {
                "$or": [
                    {"title": {"$regex": keyword, "$options": "i"}},
                    {"summary": {"$regex": keyword, "$options": "i"}},
                    {"description": {"$regex": keyword, "$options": "i"}},
                ]
            }
            for keyword in keywords
        ]
    }

    apis = await api_collection.find(query).to_list(1000)
    return [{"name": api["name"]} for api in apis]


# **************************** 4th query **********************************


@app.get("/mashups/search-by-keywords")
async def search_mashups_by_keywords(keywords: List[str] = Query(...)):
    query = {
        "$and": [
            {
                "$or": [
                    {"title": {"$regex": keyword, "$options": "i"}},
                    {"summary": {"$regex": keyword, "$options": "i"}},
                    {"description": {"$regex": keyword, "$options": "i"}},
                ]
            }
            for keyword in keywords
        ]
    }

    mashups = await mashup_collection.find(query).to_list(1000)
    return [{"title": mashup["title"]} for mashup in mashups]


# **************************** 5th query **********************************
@app.get("/apis/top-used")
async def get_top_used_apis(k: int = 10):
    # Aggregate to count the most frequently used APIs by name in mashups
    most_used_apis = await mashup_collection.aggregate(
        [
            {
                "$unwind": "$apis"
            },  # Deconstructs the apis array field from each input document
            {
                "$match": {"apis.name": {"$ne": None, "$ne": ""}}
            },  # Ensures the API has a name
            {
                "$group": {
                    "_id": "$apis.name",  # Group by API name
                    "count": {"$sum": 1},  # Count occurrences
                }
            },
            {"$sort": {"count": -1}},  # Sort by occurrence count in descending order
            {"$limit": k},  # Limit to top K results
            {
                "$project": {"name": "$_id", "count": 1, "_id": 0}
            },  # Project the name and count
        ]
    ).to_list(k)
    return most_used_apis


# **************************** 6th query **********************************
@app.get("/mashups/top-api-rich")
async def get_top_api_rich_mashups(k: int = 10):
    mashups = await mashup_collection.aggregate(
        [
            {
                "$match": {"title": {"$ne": None, "$ne": ""}}
            },  # Ensure title is not null and not empty
            {
                "$addFields": {"numApis": {"$size": {"$ifNull": ["$apis", []]}}}
            },  # Count the number of APIs in each mashup, defaulting to 0 if $apis is null
            {"$sort": {"numApis": -1}},  # Sort by numApis in descending order
            {"$limit": k},  # Limit to top K results
            {
                "$project": {"title": 1, "numApis": 1, "_id": 0}
            },  # Project only the title and number of apis field
        ]
    ).to_list(k)
    return [
        {"title": mashup["title"], "numberApis": mashup["numApis"]}
        for mashup in mashups
    ]


if __name__ == "__main__":
    # MongoDB connection setup
    client = motor.motor_asyncio.AsyncIOMotorClient(
        os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    )
    db = client.api_mashup_database
    api_collection = db.get_collection("apis")
    mashup_collection = db.get_collection("mashups")
    uvicorn.run(app, host="127.0.0.1", port=8000)
