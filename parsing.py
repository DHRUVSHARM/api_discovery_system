from pprint import pprint

import requests

base_url = "http://127.0.0.1:8000"


def parse_api_record(line):
    fields = line.strip().split("$#$")
    record = {
        "id": fields[0],
        "title": fields[1],
        "summary": fields[2],
        "rating": float(fields[3]) if fields[3] else None,
        "name": fields[4],
        "label": fields[5],
        "author": fields[6] if fields[6] else None,
        "description": fields[7],
        "type": int(fields[8]) if fields[8] else None,
        "downloads": fields[9] if fields[9] else None,
        "useCount": fields[10] if fields[10] else None,
        "sampleUrl": fields[11] if fields[11] else None,
        "downloadUrl": fields[12] if fields[12] else None,
        "dateModified": fields[13] if fields[13] else None,
        "remoteFeed": fields[14] if fields[14] else None,
        "numComments": fields[15] if fields[15] else None,
        "commentsUrl": fields[16] if fields[16] else None,
        "tags": fields[17].split("###") if fields[17] else [],
        "category": fields[18],
        "protocols": fields[19],
        "serviceEndpoint": fields[20] if fields[20] else None,
        "version": fields[21] if fields[21] else None,
        "wsdl": fields[22] if fields[22] else None,
        "dataFormats": fields[23],
        "apiGroups": fields[24] if fields[24] else None,
        "example": fields[25] if fields[25] else None,
        "clientInstall": fields[26] if fields[26] else None,
        "authentication": fields[27] if fields[27] else None,
        "ssl": fields[28] if fields[28] else None,
        "readonly": fields[29] if fields[29] else None,
        "vendorApiKits": fields[30] if fields[30] else None,
        "communityApiKits": fields[31] if fields[31] else None,
        "blog": fields[32] if fields[32] else None,
        "forum": fields[33] if fields[33] else None,
        "support": fields[34] if fields[34] else None,
        "accountReq": fields[35] if fields[35] else None,
        "commercial": fields[36] if fields[36] else None,
        "provider": fields[37] if fields[37] else None,
        "managedBy": fields[38] if fields[38] else None,
        "nonCommercial": fields[39] if fields[39] else None,
        "dataLicensing": fields[40] if fields[40] else None,
        "fees": fields[41] if fields[41] else None,
        "limits": fields[42] if fields[42] else None,
        "terms": fields[43] if fields[43] else None,
        "company": fields[44] if fields[44] else None,
        "updated": fields[45] if fields[45] else None,
    }
    return record


def parse_api_file(filename):
    with open(filename, "r") as file:
        records = [parse_api_record(line) for line in file]
    return records


def parse_mashup_record(line):
    fields = line.strip().split("$#$")
    # Correctly identify the APIs field, which seems to be one position before the last (updated) field
    apis_field = (
        fields[-2].split("###") if fields[-2] else []
    )  # Adjusted to correctly target the APIs field
    apis = []
    for api in apis_field:
        # Split each API-URL pair
        name_url_pair = api.split("$$$")
        if len(name_url_pair) == 2:
            name, url = name_url_pair
            apis.append({"name": name, "url": url})

    record = {
        "id": fields[0],
        "title": fields[1].strip(),
        "summary": fields[2].strip(),
        "rating": float(fields[3]) if fields[3] else None,
        "name": fields[4].strip(),
        "label": fields[5].strip(),
        "author": fields[6].strip() if fields[6].strip() else None,
        "description": fields[7].strip(),
        "type": fields[8].strip() if fields[8].strip() else None,
        "downloads": int(fields[9]) if fields[9] else None,
        "useCount": int(fields[10]) if fields[10] else None,
        "sampleUrl": fields[11].strip() if fields[11].strip() else None,
        "dateModified": fields[12].strip() if fields[12].strip() else None,
        "numComments": int(fields[13]) if fields[13] else None,
        "commentsUrl": fields[14].strip() if fields[14].strip() else None,
        "tags": fields[15].split("###") if fields[15] else [],
        "apis": apis,
        "updated": (
            fields[-1] if fields[-1] else None
        ),  # Assumes last field is always 'updated'
    }
    return record


def parse_mashup_file(filename):
    with open(filename, "r") as file:  # or use a different encoding if required
        records = [parse_mashup_record(line) for line in file]
    return records


# Now calling the parse_mashup_file function should work without skipping all records


def post_records_to_endpoint(url: str, records: list):
    for record in records:
        # Remove the 'id' field to avoid conflicts
        record.pop("id", None)
        # print("record ... ")
        # pprint(record)
        response = requests.post(url, json=record)
        if response.status_code != 200:
            print(f"Failed to post record: {response.text}")
            break
        else:
            print(f"Record posted successfully:")
            # print( response.json())


def retrieve_and_display_all_records(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        records = response.json()
        print(f"Retrieved {len(records)} records from {url}")
        for record in records:
            pprint(record)
    else:
        print(f"Failed to retrieve records: {response.text}")


def retrieve_and_display_record_by_id(url: str, record_id: str):
    full_url = f"{url}/{record_id}"
    response = requests.get(full_url)
    if response.status_code == 200:
        record = response.json()
        print(f"Record with ID {record_id}:")
        pprint(record)
    else:
        print(f"Failed to retrieve the record with ID {record_id}: {response.text}")


def main():
    # Use the function to parse the file and store the results
    api_records = parse_api_file("api.txt")

    # For demonstration, print the first record
    pprint(api_records[0])
    print("number of records : ", len(api_records))
    # Now, api_records can be used to insert records into MongoDB
    print("\n*********************************************\n")

    # Use the function to parse the file and store the results
    mashup_records = parse_mashup_file("mashup.txt")

    # For demonstration, print the first record
    pprint(mashup_records[19])
    print("number of mashup records : ", len(mashup_records))
    # Now, mashup_records can be used to insert records into MongoDB

    # Parse API records and post them to the FastAPI endpoint
    post_records_to_endpoint("http://127.0.0.1:8000/api", api_records)
    # print(f"Number of API records posted: {len(api_records)}")

    # Parse Mashup records and post them to the FastAPI endpoint
    post_records_to_endpoint("http://127.0.0.1:8000/mashup", mashup_records)
    # print(f"Number of Mashup records posted: {len(mashup_records)}")

    # Test retrieving all API records
    api_url = f"{base_url}/apis"
    print("Retrieving all API records:")
    retrieve_and_display_all_records(api_url)

    # Test retrieving all Mashup records
    mashup_url = f"{base_url}/mashups"
    print("\nRetrieving all Mashup records:")
    retrieve_and_display_all_records(mashup_url)

    # specific id based testing later


main()
