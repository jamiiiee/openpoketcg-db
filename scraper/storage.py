import os
import shutil
import zipfile

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def retrieve_html():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    try:
        res = supabase.storage.from_("html").download("html.zip")
        with open("html.zip", "wb") as f:
            f.write(res)
        print("HTML zip file downloaded successfully.")
    except Exception as e:
        print(f"Error downloading HTML zip file: {e}")

    with zipfile.ZipFile("html.zip", "r") as zip_ref:
        zip_ref.extractall("html")

    os.remove("html.zip")


def update_html_zip():
    shutil.make_archive("html", "zip", "html")
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    try:
        with open("html.zip", "rb") as f:
            supabase.storage.from_("html").upload(
                file=f,
                path="html.zip",
                file_options={"content-type": "application/zip", "upsert": "true"},
            )
        print("HTML zip file uploaded successfully.")
        os.remove("html.zip")
    except Exception as e:
        print(f"Error uploading HTML zip file: {e}")


def clean_html():
    if os.path.exists("html"):
        shutil.rmtree("html")
        print("HTML directory cleaned successfully.")
    else:
        print("HTML directory does not exist.")
