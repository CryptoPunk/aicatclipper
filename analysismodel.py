from typing import List, Tuple
from sqlmodel import SQLModel, Field, Relationship, Column, JSON

Scene = Tuple[str, str]

#class Video(SQLModel, table=True):
#    id: int = Field(default=None, primary_key=True)
#    filename: str = Field(default=None, description="The filename of the video")

#    scenes: list["VideoAnalysis"] = Relationship(back_populates="video", cascade_delete=True)

class VideoAnalysisResponse(SQLModel):
    id: int = Field(default=None, primary_key=True)
    description: str = Field(default=None, description="One-sentence description of the video's action.")
    tags: List[str] = Field(default=None, sa_column=Column(JSON), description="Concise tags describing visual elements and tone.")
    vBPM: float = Field(default=None, description="Visual Beats Per Minute of the video's motion.")
    rhythmic_strength: float = Field(default=None, description="Strength of the visually dominant subject's visual rhythm (0-10).")
    energy_score: float = Field(default=None, description="Overall energy level of the video (0-10).")
    cat_score: float = Field(default=None, description="Subjective score of cat focus and duration (0-10).")

class VideoAnalysis(VideoAnalysisResponse, table=True):
#    video_id: int = Field(foreign_key="video.id", ondelete="CASCADE")
#    video: Video = Relationship(back_populates="videoanalysis")
    scene_start: str = Field(description="Scene start timecode")
    scene_end: str = Field(description="Scene end timecode")

    @property
    def scene(self) -> Scene:
        return (self.scene_start, self.scene_end)
    
    @scene.setter
    def scene(self, value: Scene):
        self.scene_start = value[0]
        self.scene_end = value[1]