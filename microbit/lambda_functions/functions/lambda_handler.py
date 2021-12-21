import boto3, gzip
from io import BytesIO

client = boto3.client('s3')


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    # s3: // s3 - microbit - data - develop - data - lake - raw / atomic_events / date = 2021 - 11 - 26 /
    bucket = "s3-microbit-data-develop-data-lake-raw"
    try:
        response = client.list_objects(Bucket=bucket, Prefix="atomic_events")
        print(response)
        for content in response.get("Contents", []):
            # print(content.get("Key"))
            key=content.get("Key")
            obj = client.get_object(Bucket=bucket, Key=key)
            for file in obj:
                print(file)
                # with gzip.GzipFile(fileobj=file) as gzipfile:
                #     content = gzipfile.read()
                #     print(content)
        # return response["ContentType"]
    except Exception as e:
        print(e)
        print(
            "Error getting objects from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                client
            )
        )
        raise e
