import os
import shutil
import zipfile

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def retrieve_html():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise EnvironmentError(
            "Environment variables SUPABASE_URL and SUPABASE_KEY must be set."
        )

    supabase = create_client(supabase_url, supabase_key)

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

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise EnvironmentError(
            "Environment variables SUPABASE_URL and SUPABASE_KEY must be set."
        )

    supabase = create_client(supabase_url, supabase_key)

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
