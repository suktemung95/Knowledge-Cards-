from PIL import Image
import numpy as np
import boto3

s3 = boto3.client('s3')
BUCKET_NAME = 'knowledge-cards-bucket'

def upload_to_s3(file_obj, filename):
    s3.upload_fileobj(file_obj, BUCKET_NAME, filename)
    
    return f"http://{BUCKET_NAME}.s3.amazonaws.com/{filename}"

def delete_from_s3(filename):
    s3.delete_object(Bucket=BUCKET_NAME, Key=filename)

def generate_histogram(image_file):
    img = Image.open(image_file).resize((100, 100)).convert("RGB")
    arr = np.array(img)

    hist, _ = np.histogram(arr.flatten(), bins=32, range=(0, 256))
    hist = hist / hist.sum()

    return ",".join(map(str, hist))