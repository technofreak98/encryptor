from fastapi import FastAPI, File, UploadFile
from encrypt import Encryptor, upload_file_to_bucket, download_file_from_bucket
from config import BUCKET_NAME

app = FastAPI()

encryptor = Encryptor()
mykey = encryptor.key_create()
encryptor.key_write(mykey, 'mykey.key')
loaded_key = encryptor.key_load('mykey.key')


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
        encryptor.file_encrypt(loaded_key, file.filename, 'encrypt/' + file.filename)
        s3_url = upload_file_to_bucket(BUCKET_NAME, 'encrypt/' + file.filename)

    except Exception as e:
        print(e)
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully Encrypted and uploaded at {s3_url}"}


@app.post("/download")
def download(filename: str):
    try:
        download_file_from_bucket(BUCKET_NAME, filename, 'decrypt/' + filename)
        encryptor.file_decrypt(loaded_key, 'decrypt/' + filename, filename)
    except Exception as e:
        print(e)
        return {"message": "There was an error uploading the file"}
    return {"message": f"Downloaded and Decrypted {filename}"}
