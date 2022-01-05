import boto3, gzip
from io import BytesIO
import json

client = boto3.client("s3")
client_firehose = boto3.client("firehose")

def lambda_handler(event, context):
    # Get the object from the event and show its content type
    data_list = ["carSN", "a.x", "a.y", "a.z", "tembo", "temp", "dist", "light", "sound", "compass", "mag.x", "mag.y",
                 "mag.z", "mag.str", "left", "right", "mv", "seconds"]
    data_lake_raw = "s3-microbit-data-develop-data-lake-raw"
    data_lake_processed = "s3-microbit-data-develop-data-lake-processed"
    data = ""
    try:
        response = client.list_objects(Bucket=data_lake_raw, Prefix="atomic_events")
        print("Total Responses: ", len(response.get("Contents", [])))
        for content in response.get("Contents", []):
            # print(content.get("Key"))
            key = content.get("Key")
            print(key)
            obj = client.get_object(Bucket=data_lake_raw, Key=key)
            gzip_content = obj["Body"].read()
            with gzip.GzipFile(fileobj=BytesIO(gzip_content), mode="rb") as gzipfile:
                content = gzipfile.read()
                for line in content.decode().split("\n"):
                    line = line.rstrip()
                    if line:
                        if "k" not in line:
                            line = line.replace('""', '"k"')
                        dic = json.loads(line)
                        if dic["k"] in data_list:
                            data = f"{data}{json.dumps(dic)}\n"
                        else:
                            print("NOT IN THE LIST", dic["k"])
                if data:
                    print(data)
                    with gzip.GzipFile(fileobj=data, mode="wb") as new_gzipfile:
                        client.Bucket(data_lake_processed).put_object(
                            Key="atomic_events/date=!{timestamp:yyyy}-!{timestamp:MM}-!{timestamp:dd}/",
                            Body=new_gzipfile)

                else:
                    print('NO DATA')
            print("-" * 100)
        # return response["ContentType"]
    except Exception as e:
        print(e)
        print(
            "Error getting objects from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                client
            )
        )
        raise e
