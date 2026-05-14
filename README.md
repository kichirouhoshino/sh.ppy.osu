## My edit of the osu!lazer flatpak
### Changes:
- Add LatencyFleX
- libstrangle for more flexible framerate capping (useful for VRR)
- Stuttering fixes for Vulkan Renderer
- Additional envvars for lower latency (adjustable using Flatseal or similar methods)
### Notes
- Make sure the game renderer is set to Vulkan.
- Set your preferred STRANGLE_FPS cap, PIPEWIRE_LATENCY (For PipeWire output, default) and PULSE_LATENCY_MSEC (For PulseAudio output) variables using something like Flatseal.
- You can reduce audio stutters and xruns caused by low latency by configuring pipewire to dynamically switch between 44100Hz and 48000Hz. Due to how osu audio works, it only outputs at 44100Hz, which causes pipewire to resample the audio. If you do configure pipewire, make sure to launch osu first before playing any other audio to prioritize 44100Hz.
- You can also play around with direct ALSA output, but I have not tested it myself. PipeWire is already low-latency enough for me.


# osu!
Keep in mind that the package is **not** official, there may be bugs specific to the flatpak. If you find such, report them here.
> Note: This is osu!(lazer) - a future update which is yet to be considered mainstream. It is not osu!(stable).

## Where is the game directory located?
Check `~/.var/app/sh.ppy.osu/data/osu`

## Graphics tablets
osu! uses [OpenTabletDriver](https://github.com/OpenTabletDriver/OpenTabletDriver) for graphics tablets support. \
However, it may not work for some reasons, here are some of them:
 - **At the moment, the tablet is controlled by the kernel module** \
You need to unload the module yourself from the terminal, using the following command: \
`sudo rmmod wacom || sudo rmmod hid_uclogic`
 - **Failed to open device streams** \
You need to download and execute the script from this repository (`tablet-udev-gen-rules.sh`) and create some [udev rules](https://wiki.archlinux.org/title/udev)\
Don't forget to install `git` and `jq` via your package manager! \
\
If you are *not sure*/*do not understand* what to do:
```
curl -L -o ./tablet-udev-gen-rules.sh https://raw.githubusercontent.com/flathub/sh.ppy.osu/master/tablet-udev-gen-rules.sh
chmod +x ./tablet-udev-gen-rules.sh
./tablet-udev-gen-rules.sh --idk # press Enter after udev question
```
or, follow [this guide](https://opentabletdriver.net/Wiki/FAQ/Linux#fail-device-streams)
> **_Note_**: To generate udev rules using the official guide, you need to install `dotnet` from the repositories of your distribution

Please, share your experience of using a graphics tablet in **osu!**. Both on the build in `flatpak` and on the official one (`AppImage`).

## When selecting files, not all directories are visible
This happens because when a flatpak container is launched, only the necessary directories are passed through to it.

If you want to be able to access all files and directories in your home directory, use `Flatseal` from `flatpak`, or `sudo flatpak override sh.ppy.osu --filesystem=home`
