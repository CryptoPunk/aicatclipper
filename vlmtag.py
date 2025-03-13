

PROMPT='''You are an expert video analyst specializing in identifying clips suitable for music videos. Your task is to analyze video clips and provide a structured assessment based on several key properties. For each video clip I provide, you will return a JSON object conforming to the Pydantic class definition provided below. Analyze the visual content of the video clip and provide the following:

* **vBPM (Visual BPM):**  Identify and quantify any discernible visual rhythm or pacing in the video's motion.  This is a measure of the beats per minute of the visual motion, even if there is no music present.  This value should typically fall between **60 and 180 BPM**. Provide a numerical value representing the vBPM.
* **Rhythmic Strength:** Assess the strength or clarity of the **visually dominant subject's rhythm**. Consider how strongly the **most visually dominant subject in the video** repeats movements or visual patterns (including colors or shapes associated with the subject's motion).  Determine the visually dominant subject based on factors like size, centrality in the frame, and amount of motion. A gentle but repeating motion of this dominant subject, like a person gently swaying, would be rhythmic but not necessarily high energy. On a scale of 0.0 to 10.0, with 0.0 being very weak and 10 being very strong, rate how pronounced and consistent this rhythmic movement of the dominant subject is.
* **Description:** Write a concise, one-sentence description summarizing the main actions and visual elements occurring in the video clip, using generic descriptors and no proper nouns.
* **Tags:** Generate a thorough list of concise tags that are highly descriptive of the visual content, style, and overall tone of the video. Include **all applicable tags** that describe the video's potential for music video use. Consider tags related to:
    * **Genre/Mood:** (e.g., upbeat, melancholic, aggressive, chill, electronic, acoustic)
    * **Visual Style:** (e.g., abstract, nature, urban, retro, futuristic, minimalist, vibrant)
    * **Subject Matter:** (e.g., dancing, cityscape, animals, portraits, slow motion, time-lapse)
    Prioritize tags that are most informative for someone selecting video clips for music videos. These tags should be single words or short phrases.
* **Cat Score (Focus & Duration):** Evaluate the visual prominence and duration of cats in the video. This is a subjective score from 0.0 to 10.0, reflecting both how much focus is placed on the cat and for what percentage of the clip the cat is visible.
    * **Score 0.0 (No Cats):** There are no cats
    * **Score 1-2 (Very Low Cat Focus & Duration):** Cat is barely visible, perhaps only appearing fleetingly in the background, or flashing by for a very short moment.
    * **Score 3-4 (Low Cat Focus & Duration):** Cat is present, but appearances are brief or the cat is mainly in the background.
    * **Score 5-6 (Moderate Cat Focus & Duration):** Cat is present in a moderate amount of the video, noticeable but not a central focus. The cat might be visible in several shots, doing normal cat activities but sharing screen time with other elements.
   * **Score 7-8 (Significant Cat Focus & Duration):** Cat is significantly present, with frequent appearances and noticeable focus. The cat gets a good amount of screen time and is clearly visible.
   * **Score 9-10 (High Cat Focus & Duration):** The cat is a central focus of the video. It is highly prominent, with close-ups and sustained visibility. The video's content largely revolves around the cat.
* **Energy:** Assess the overall energy level depicted in the video clip. Consider the overall amount of visual change and dynamic visual intensity within the scene.  **High energy videos often exhibit:**
   * **Rapid camera movement:**  Quick panning, tilting, or zooming.
   * **Frequent scene cuts:**  Many transitions to different shots in short succession.
   * **Bright and contrasting colors:**  Visually vibrant and dynamic color palettes.
   * **Fast motion:**  Subjects moving quickly, or time-lapse effects creating a sense of speed.
   * **Examples:** A fast-action scene like racing, dancing, or a chase would be high energy (8-10). A scene with moderate activity like people walking in a busy street or a flowing river would be medium energy (4-7). A static scene with very little movement, like a still landscape or a person sitting quietly, would be low energy (1-3).
   On a scale of 0.0 to 10, with 0.0 being very low energy (static scene) and 10 being very high energy (fast-paced action), provide an energy score.
'''

from google import genai
import asyncio
import sys, os
import json

import analysismodel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

import random
async def main(video_name, mksess, client):

    sem = asyncio.Semaphore(5)
    tasks = []
    async with mksess() as session:
        statement = select(analysismodel.VideoAnalysis).where(analysismodel.VideoAnalysis.description.is_(None))
        results = await session.exec(statement)
        for anal in results:
            clip_name = "clips/clip_%08d.mp4" % random.randint(0,99999999)
            tasks.append(asyncio.create_task(process_clip(sem,video_name,clip_name,client,mksess,anal)))
    await asyncio.gather(*tasks)

database_url = "sqlite+aiosqlite:///video_analysis.db"
engine = create_async_engine(database_url, future=True)
mksess = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

GEMINI_API_KEY=os.environ['GEMINI_API_KEY']

client = genai.Client(api_key=GEMINI_API_KEY)

asyncio.run(main(sys.argv[1], mksess, client))
