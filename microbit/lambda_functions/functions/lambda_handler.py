import boto3, gzip
from io import BytesIO, TextIOWrapper
from datetime import datetime
import json

client = boto3.client("s3")


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
                    # print(data)
                    now = datetime.now()
                    filename = f"/tmp/develop-processed-delivery-stream-{now.strftime('%Y-%m-%d-%H-%M-%S')}-{'-'.join(key.split('-')[-5:])}.gz"
                    with gzip.open(filename=filename, mode="wb") as new_gzipfile:
                        with TextIOWrapper(new_gzipfile, encoding='utf-8') as encode:
                            encode.write(data)
                    print(filename)
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
