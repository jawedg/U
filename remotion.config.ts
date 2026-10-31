import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setCodec("h264");
// Auf Linux-Servern ohne eigenen Chrome z. B.:
// Config.setBrowserExecutable("/opt/pw-browsers/chromium/chrome-linux/chrome");
