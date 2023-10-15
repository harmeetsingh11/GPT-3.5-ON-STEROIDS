"""
This module includes all functions used by the program.
"""
import time
import json
import wikipedia
import openai
from PyPDF2 import PdfReader
from docx import Document
import streamlit as st
import pandas as pd
from serpapi import GoogleSearch
from youtube_transcript_api import YouTubeTranscriptApi
from trafilatura import fetch_url, extract
from consts import (
    SERP_API_KEY,
    TOKEN_LIMIT,
    encoding,
)


def search_wiki(command) -> str:
    """Searches wikipedia
    Args:
        command: a dictionary containing the query
    Returns:
        str: results returned by wikipedia
    """
    print("Search wiki called")
    return "Command wikipedia returned: " + wikipedia.summary(command["query"])


def write_to_file(command) -> str:
    """Writes text to a file
    Args:
        command: a dictionary containing the "filename" and "text"
    Returns:
        str: success message
    """
    print("Write to file called")
    with open(command["filename"], "w", encoding="utf-8") as file:
        file.write(command["text"])
    return "Command write_to_file returned: File was written successfully"


def append_to_file(command) -> str:
    """Appends text to a file
    Args:
        command: a dictionary containing the "filename" and "text"
    Returns:
        str: success message
    """
    print("Append to file called")
    with open(command["filename"], "a", encoding="utf-8") as file:
        file.write(command["text"])
    return "Command append_to_file returned: File was appended successfully"


def read_file(command) -> str:
    """Returns text from a file
    Args:
        command: a dictionary containing the "filename"
    Returns:
        str: text stored in the file
    """
    print("Read file called")
    with open(command["filename"], "r", encoding="utf-8") as file:
        data = file.read()
        return f"Command read_file returned: {data}"


def open_file(command) -> str:
    """Shows a download button on the Streamlit interface to download the file generated by GPT.
    Args:
        command: a dictionary containing the "path" to the file
    Returns:
        str: a success message
    """
    print("Open file called")
    with open(command["path"], "r", encoding="utf-8") as file:
        st.download_button("Open File", file, file_name=command["path"])
    return "Command open_file returned: File was opened successfully"


def browse_website(command) -> str:
    """Browse website and extract main content upto TOKEN_LIMIT tokens
    Args:
        command: a dictionary containing "url" to the website
    Returns
        str: the content of that website in json format
    """
    print("Browse website called")
    # grab a HTML file to extract data from
    downloaded = fetch_url(command["url"])

    # output main content and comments as plain text
    result = extract(downloaded, output_format="json")

    if len(encoding.encode(str(result))) < TOKEN_LIMIT:
        return "Command browse_website returned: " + str(result)
    return "Command browse_website returned: " + str(result)[:TOKEN_LIMIT]


def google_tool(command) -> str:
    """Searches google for query and returns upto TOKEN_LIMIT tokens of results
    Args:
        command: a dictionary containing "query"
    Returns:
        str: response in json format
    """
    print("Google tool called")
    params = {
        "q": str(command["query"]),
        "location": "Delhi,India",
        "first": 1,
        "count": 10,
        "num": 4,
        "api_key": SERP_API_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    organic_results = []
    page_count = 0
    page_limit = 1

    while "error" not in results and page_count < page_limit:
        organic_results.extend(results.get("organic_results", []))

        params["first"] += params["count"]
        page_count += 1
        results = search.get_dict()

    response = json.dumps(organic_results, indent=2, ensure_ascii=False)
    if len(encoding.encode(response)) < TOKEN_LIMIT:
        return "Command google returned: " + response
    return "Command google returned: " + response[:TOKEN_LIMIT]


def type_message(command) -> None:
    """Displays text on the screen with a typewriter effect
    Args:
        text: any string
    Returns:
        None
    """
    print("Type message called")
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in command["text"]:
            full_response += response
            time.sleep(0.02)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)


def ask_gpt(messages) -> str:
    """Generates text using the "gpt-3.5-turbo" model
    Args:
        message: a list of dictionaries in the format {"role": <role>, "content": <message>}
    Returns:
        str: text generated by gpt
    """
    reply = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0
    )
    return reply.choices[0].message.content


def get_youtube_transcript(command) -> str:
    """Fetches transcripts from YouTube videos
    Args:
        url: the url of the YouTube video
    Returns:
        str: transcript of the video
    """
    print("Get youtube transcript called")
    try:
        srt_dictionary = YouTubeTranscriptApi.get_transcript(command["video_id"])
        srt_text = " ".join(x["text"] for x in srt_dictionary)
        if len(encoding.encode(srt_text)) < TOKEN_LIMIT:
            return f"Here are the video subtitles: \"{srt_text}\""
        return f"Here are the video subtitles: \"{srt_text}\""[:TOKEN_LIMIT]
    except Exception as error:
        print("ERROR", error)
        return "The video does not have any subtitles"


def getData(uploaded_file)->str:
    '''The function extracts the data from docx , pdf and excel file 
    1.for pdf and doc file it will return the text extracted from the file.
    2.for excel it will convert the excel file into and object named ExcelFile which can be further used for analysis using pandas'''
    extension = uploaded_file.name.split(".")[1]
    text = ""
    if extension=="pdf":
        reader = PdfReader(uploaded_file)
        pages = reader.pages
        for i in range(len(pages)):
            text+=pages[i].extract_text()
    if extension=="docx":
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text+=para.text
    if extension=="xlsx":
        ExcelFile = pd.read_excel(uploaded_file)
        ExcelFile.to_csv()

        st.write(ExcelFile)
    if extension=="csv":
        df = pd.read_csv(uploaded_file)
        return df.to_string()
    if len(encoding.encode(str(text))) < TOKEN_LIMIT:
         return "Command browse_website returned: " + str(text)
    return "Command browse_website returned: " + str(text)[:TOKEN_LIMIT]
