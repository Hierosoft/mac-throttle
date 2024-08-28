# mac-throttle
Detect slowness issues due to throttling such as may be caused by an old battery. Provide steps that may improve the situation in some cases. See license for disclaimers.

## Related Projects
- https://github.com/syscl/CPUTune
- https://github.com/calasanmarko/TurboMac

## Examples
### MacBook Air (13-inch, Mid 2012)
- Model: A1466
- Graphics: Intel HD Graphics 4000 1536 MB
- Memory: 4 GB 1600 MHz DDR3
- Processor: i5 1.8 GHz (model 1536M, no T2), but the script may inform you (using `pmset -g therm`) of the following issues:
  - CPU_Speed_Limit = 48 (100 is 100%)
  - CPU_Available_CPUs = 4 (4 is expected)
  - CPU_Speed_Limit = 31 (100 is 100%)
- You may have to compile CPUTune or other utilities using a different computer with the same version of macOS if the affected computer is too slow:
  - apple.com said Xcode 14.5 was for my Catalina 10.15.7
  - downloading and extracting it took literally days, even on a wired connection
  - There was an 🚫 over the Xcode app
  - I tried draggind it to Applications
  - Trying to open it resulted in some error about it being corrupt
  - When the app is in Applications, `git clone` fails and says "xcrun: error: invalid active developer path (/Applications/Xcode.app/Contents/Developer), missing xcrun at: /Applications/Xcode.app/Contents/Developer/usr/bin/xcrun"
    - git works after removing the app from Applications.
