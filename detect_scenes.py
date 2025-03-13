from scenedetect import detectors, open_video, SceneManager, FrameTimecode, VideoStream
import numpy as np
from matplotlib.colors import rgb_to_hsv

type Scene = tuple[FrameTimecode,FrameTimecode]
type SceneList = list[Scene]
type Frame = np.ndarray

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

def get_midpoint(scene: Scene,point: float = 0.5) -> FrameTimecode:
    return scene[0] + get_duration(scene)*point

def get_duration(scene: Scene) -> float:
    start = scene[0].get_seconds()
    end = scene[1].get_seconds()
    return end-start

def get_frame_at(video: VideoStream, tc: FrameTimecode) -> Frame:
    video.seek(tc)
    return video.read()

def frame_avg(frame: Frame):
    return rgb_to_hsv(np.mean((frame/255.0),axis=(0,1)))

def fdiff(f0: Frame, f1: Frame):
    hsv0 = rgb_to_hsv(f0/255.0)
    hsv1 = rgb_to_hsv(f1/255.0)
    return np.sum(np.abs(hsv1-hsv0))/hsv0.size

def scenediff(video: VideoStream, scene0: Scene, scene1: Scene, tdiff: float=0.2):
    f0 = get_frame_at(video,get_midpoint(scene0,1.0-tdiff))
    f1 = get_frame_at(video,get_midpoint(scene1,tdiff))
    return fdiff(f0,f1)

def merge_scenes(video: VideoStream, scenes: SceneList, min_duration: float=1.0) -> SceneList:
    new_scenes = []

    scenes = scenes.copy()
    while len(scenes) > 0:
        scene = scenes.pop(0)
        if get_duration(scene) >= min_duration:
            new_scenes.append(scene)
        else:
            last_scenediff = float('inf')
            next_scenediff = float('inf')
            if(0 < len(new_scenes)):
                last_scenediff = scenediff(video, new_scenes[-1], scene, 0.1)
            if(0 < len(scenes)):
                next_scenediff = scenediff(video, scene, scenes[0], 0.1)
            #log.info(f"{next_scenediff.shape}")
            log.info(f"{last_scenediff} {next_scenediff}")
            if next_scenediff == float('inf') and last_scenediff == float('inf'):
                new_scenes.append(scene)
            elif last_scenediff < next_scenediff:
                new_scenes[-1] = (new_scenes[-1][0], scene[1])
            else:
                scenes[0] = (scene[0],scenes[0][1])
    return new_scenes

def get_manager():
    adaptive = detectors.AdaptiveDetector()
    threshold = detectors.ThresholdDetector()
    manager = SceneManager()
    manager.add_detector(adaptive)
    manager.add_detector(threshold)
    return manager

import sys
import analysismodel

from sqlmodel import Session, create_engine

if __name__ == '__main__':
    manager = get_manager()

    video = open_video(sys.argv[1])
    manager.detect_scenes(video=video)
    scenes = manager.get_scene_list()

    database_url = "sqlite:///video_analysis.db"
    engine = create_engine(database_url)

    with Session(engine) as session:
        for scene in merge_scenes(video, scenes, 1.0):
                vid_anal = analysismodel.VideoAnalysis()
                vid_anal.scene = scene
                session.add(vid_anal)
                session.commit()