// Textur für das 3D-Gestell: die Gestell-Zeichnung in hoher Auflösung, transparenter Hintergrund.
import React from "react";
import { AbsoluteFill } from "remotion";
import { GH, GW, Gestell, GestellDefs } from "../pruef/Gestell";

export const TEX_SCALE = 4;
export const GestellTex: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "transparent" }}>
    <svg width={GW * TEX_SCALE} height={GH * TEX_SCALE} viewBox={`0 0 ${GW} ${GH}`}>
      <GestellDefs />
      <Gestell st={{}} t={0} />
    </svg>
  </AbsoluteFill>
);
