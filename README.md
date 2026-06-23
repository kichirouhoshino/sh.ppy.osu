## My edit of the osu!lazer flatpak
### Changes:
- Add LatencyFleX
- libstrangle for more flexible framerate capping (useful for VRR)
- Forcing Vulkan and wayland by default. Stuttering fixes for Vulkan Renderer
- Uses the flatpak runtime's SDL libraries over the appimage ones.
- Additional settings for audio latency.

A config GUI also appears that allows setting some stuff before the game launches.

### Notes
- You can reduce audio stutters and xruns caused by low latency by configuring pipewire to dynamically switch between 44100Hz and 48000Hz. Due to how osu audio works, it only outputs at 44100Hz, which causes pipewire to resample the audio. If you do configure pipewire, make sure to launch osu first before playing any other audio to prioritize 44100Hz.
- Realtime is recommeded to reduce audio crackles on certain setups. Consult your distro documentation on how to do it.

### Other stuff
- **Is this a hack or mod?** No, not really. It does not modify the game binaries in any way and only involves setting env vars or vulkan layers.
- **This is made with the assistance of AI.** I have obviously heavily tested this before pushing anything. If you're not a fan of any of this, simply do not use this flatpak and move on. You can check the various env vars and additional programs it uses and apply it to your own install all on your own.
