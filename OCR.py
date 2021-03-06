#!pip install google-cloud-vision==1.0.0
# pip install --upgrade google-cloud-storage
import os, io
import re
from google.cloud import vision
from google.cloud import storage
from google.protobuf import json_format

def scanpdfocr(file_source,destination_source):

  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'/content/drive/MyDrive/ColabNotebooks/project-304406-e72f06f8725a.json'
  client = vision.ImageAnnotatorClient()
  batch_size = 2
  mime_type = 'application/pdf'
  feature = vision.types.Feature(
      type=vision.enums.Feature.Type.DOCUMENT_TEXT_DETECTION)

  gcs_source_uri = file_source  #Sourc
  gcs_source = vision.types.GcsSource(uri=gcs_source_uri)
  input_config = vision.types.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

  gcs_destination_uri = destination_source #Destination
  gcs_destination = vision.types.GcsDestination(uri=gcs_destination_uri)
  output_config = vision.types.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

  async_request = vision.types.AsyncAnnotateFileRequest(
      features=[feature], input_config=input_config, output_config=output_config)

  operation = client.async_batch_annotate_files(requests=[async_request])
  operation.result(timeout=180)

  storage_client = storage.Client()
  match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
  bucket_name = match.group(1)
  prefix = match.group(2)
  bucket = storage_client.get_bucket(bucket_name)

  # List object with the given prefix
  blob_list = list(bucket.list_blobs(prefix=prefix))
  output = blob_list[0]
  json_string = output.download_as_string()
  response = json_format.Parse(
            json_string, vision.types.AnnotateFileResponse())

  first_page_response = response.responses[0]
  content = first_page_response.full_text_annotation.text

  return content


try:
  cp = scanpdfocr('gs://eattachments/Rekins_1.pdf','gs://eattachments/1144d')
  print("File Scanned Successfully")
except:
  print("File Format Not Supported")


#Translation
from google_trans_new import google_translator 
translator = google_translator()  
translate_text = translator.translate(cp,lang_tgt='en-US')

final=list()
for dat in cp.split('\n'):
  translate_text = translator.translate(dat,lang_tgt='en-US')
  final.append(translate_text.lower())



