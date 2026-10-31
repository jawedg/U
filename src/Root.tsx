import React from "react";
import { Composition } from "remotion";
import { TextVideo, sceneDurations } from "./TextVideo";
import { TrainVideo, trainDurationFrames } from "./train/TrainVideo";
import { AthanVideo, athanDurationFrames } from "./athan/AthanVideo";

export const FPS = 30;

export const RemotionRoot: React.FC = () => {
  const total = sceneDurations(FPS).reduce((a, b) => a + b, 0);
  return (
    <>
    <Composition
      id="TextVideo"
      component={TextVideo}
      durationInFrames={total}
      fps={FPS}
      width={1080}
      height={1920}
    />
    <Composition
      id="Erklaervideo3D"
      component={TrainVideo}
      durationInFrames={trainDurationFrames(FPS)}
      fps={FPS}
      width={1080}
      height={1920}
    />
    <Composition
      id="ErsterAdhan"
      component={AthanVideo}
      durationInFrames={athanDurationFrames(FPS)}
      fps={FPS}
      width={1080}
      height={1920}
    />
    </>
  );
};
