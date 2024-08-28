# mac-revive
Detect slowness issues due to throttling such as may be caused by an old battery. Provide steps that may improve the situation in some cases. See license for disclaimers.

## Examples
### Mid 2012 MacBook Air (A1466)
- Graphics: IntelHD 4000
- Processor: i5 1.8 GHz (model 1536M, no T2), but the script may inform you (using `pmset -g therm`) of the following issues:
  - CPU_Speed_Limit = 48 (100 is 100%)
  - CPU_Available_CPUs = 4 (4 is expected)
  - CPU_Speed_Limit = 31 (100 is 100%)
