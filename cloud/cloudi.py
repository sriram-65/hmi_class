import cloudinary.uploader
import cloudinary


cloudinary.config(
    cloud_name="dbrmvywb0",
    api_key="799647841433247",
    api_secret="XLtCOYXxRTnjZqwaF2oFnQ0AK7k"
)

def upload_notes(note_file):
    url = cloudinary.uploader.upload(note_file ,    resource_type="auto")
    return url['secure_url']

