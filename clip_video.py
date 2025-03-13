#!/usr/bin/env python3
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from analysismodel import VideoAnalysis
import ffmpyg

import asyncio
import sys

async def find_cat_clips(mksess, min_cat = 8, min_energy = 3):
    async with mksess() as session:
        statement = select(VideoAnalysis).where((VideoAnalysis.cat_score >= min_cat) & (VideoAnalysis.energy_score >= min_energy))
        results = await session.exec(statement)
        return results.all()

async def cut_clip(sem,video_file,clip):
    async with sem:
        await ffmpyg.async_ffmpeg(input_file=video_file,
                                  output_file="clips/clip_%03d.mp4"%clip.id,
                                  start=clip.scene_start,
                                  to=clip.scene_end)

async def main(video_file, clips):
    sem = asyncio.Semaphore(5)
    tasks = []
    for clip in clips:
        tasks.append(asyncio.create_task(cut_clip(sem,video_file,clip)))
    return await asyncio.gather(*tasks)


database_url = "sqlite+aiosqlite:///video_analysis.db"
engine = create_async_engine(database_url, future=True)
mksess = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

clips = asyncio.run(find_cat_clips(mksess))

asyncio.run(main(sys.argv[1], clips))