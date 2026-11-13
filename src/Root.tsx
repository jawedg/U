import React from "react";
import { Composition } from "remotion";
import { TextVideo, sceneDurations } from "./TextVideo";
import { TrainVideo, trainDurationFrames } from "./train/TrainVideo";
import { AthanVideo, athanDurationFrames } from "./athan/AthanVideo";
import { Video2D, video2dFrames } from "./athan2d/Video2D";
import { WisoVideo, wisoFrames, WFPS } from "./wiso/WisoVideo";
import { AllVideo, allFrames, AFPS } from "./wiso_all/AllVideo";
import { LernVideo, lernFrames, LFPS } from "./lern/LernVideo";
import { LegeVideo } from "./lern/LegeVideo";
import { PruefVideo } from "./pruef/PruefVideo";
import { MessVideo, messFrames } from "./mess/MessVideo";
import { GestellTex, TEX_SCALE } from "./mess/GestellTex";
import { WhatIfVideo, whatifFrames } from "./whatif/WhatIf";
import { FPS as WFPS2 } from "./whatif/timeline";
import { AnimeVideo, animeFrames } from "./anime/Anime";

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
    <Composition
      id="ErsterAdhan2D"
      component={Video2D}
      durationInFrames={video2dFrames(FPS)}
      fps={FPS}
      width={1080}
      height={1920}
    />
    <Composition
      id="WisoKB4"
      component={WisoVideo}
      durationInFrames={wisoFrames()}
      fps={WFPS}
      width={1920}
      height={1080}
    />
    <Composition
      id="WisoAlle"
      component={AllVideo}
      durationInFrames={allFrames()}
      fps={AFPS}
      width={1920}
      height={1080}
    />
    {[1, 2, 3, 4].map((kb) => (
      <Composition
        key={kb}
        id={`LernKB${kb}`}
        component={LernVideo}
        defaultProps={{ kb }}
        durationInFrames={lernFrames(kb)}
        fps={LFPS}
        width={1920}
        height={1080}
      />
    ))}
    <Composition
      id="LernGK"
      component={LernVideo}
      defaultProps={{ kb: 5 }}
      durationInFrames={lernFrames(5)}
      fps={LFPS}
      width={1920}
      height={1080}
    />
    <Composition id="LernFuellstand" component={LernVideo} defaultProps={{ kb: 6 }} durationInFrames={lernFrames(6)} fps={LFPS} width={1920} height={1080} />
    <Composition id="AnimeFolge1" component={AnimeVideo} durationInFrames={animeFrames()} fps={30} width={1080} height={1920} />
    <Composition id="WasWaere" component={WhatIfVideo} durationInFrames={whatifFrames()} fps={WFPS2} width={1080} height={1920} />
    <Composition id="MessPOV" component={MessVideo} durationInFrames={messFrames()} fps={LFPS} width={1920} height={1080} />
    <Composition id="GestellTex" component={GestellTex} durationInFrames={1} fps={LFPS} width={960 * TEX_SCALE} height={760 * TEX_SCALE} />
    <Composition id="PruefSim" component={PruefVideo} durationInFrames={lernFrames(7)} fps={LFPS} width={1920} height={1080} />
    <Composition id="LernGK2" component={LegeVideo} durationInFrames={lernFrames(5)} fps={LFPS} width={1920} height={1080} />
    </>
  );
};
