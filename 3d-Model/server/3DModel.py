import http.client
import json
import base64

# Convert image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
image_base64 = encode_image_to_base64("my_sketch.png")


conn = http.client.HTTPSConnection("api.piapi.ai")
payload = json.dumps({
   "model": "Qubico/trellis",
   "task_type": "image-to-3d",
   "input": {
      "image": image_base64,
      "seed": 0,
      "ss_sampling_steps": 50,
      "slat_sampling_steps": 50,
      "ss_guidance_strength": 7.5,
      "slat_guidance_strength": 3
   },
   "config": {
      "webhook_config": {
         "endpoint": "string",
         "secret": "string"
      }
   }
})
headers = {
   'x-api-key': 'eb7c0a7d040d76a55cb11188ed5bda5c8ff127a65a869b5f7a473f136498ddb6',
   'Content-Type': 'application/json'
}
conn.request("POST", "/api/v1/task", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))