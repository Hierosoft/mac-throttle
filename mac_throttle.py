from __future__ import print_function
from __future__ import division
import subprocess
import sys
import time

def get_pmset_key_value_pairs():
    """Gets key-value pairs from 'pmset -g therm'."""
    result = subprocess.Popen(['pmset', '-g', 'therm'], stdout=subprocess.PIPE)
    output, _ = result.communicate()

    pmset_dict = {}

    if result.returncode == 0:
        for line in output.splitlines():
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                pmset_dict[key.strip()] = value.strip()
    else:
        print("Error: pmset command failed with return code", result.returncode, file=sys.stderr)

    return pmset_dict

def get_cpu_current_speed():
    """Attempts to get the current CPU frequency using sysctl commands."""
    result = subprocess.Popen(['sysctl', '-a'], stdout=subprocess.PIPE)
    output, _ = result.communicate()

    cpu_dict = {}

    if result.returncode == 0:
        for line in output.splitlines():
            line = line.strip()
            if 'frequency' in line and ':' in line:
                key, value = line.split(':', 1)
                cpu_dict[key.strip()] = value.strip()
    else:
        print("Error: sysctl command failed with return code", result.returncode, file=sys.stderr)

    return cpu_dict


def get_powermetrics_data():
    """Gets throttling-related data from 'powermetrics'."""
    # Define the keys we are interested in
    powermetrics_keys = [
        "System Average frequency as fraction of nominal",
        "Machine model",
        "SMC version",
        "EFI version",
        "OS version",
        "Boot time"
    ]
    # NOTE: When not using -n 1, the live monitor (exit with Ctrl+C)
    #   also has machdep.cpu.mwait.sub_Cstates,
    #   machdep.cpu.thermal.hardware_feedback
    #   which may be useful, but there is no way, apparently,
    #   to get the values. The program must use ncurses or
    #   some other similar library. Such values never make it
    #   to stdout (nor stderr).
    keys_max = len(powermetrics_keys)
    
    # Make a copy of powermetrics_keys to track missing keys
    missing = set(powermetrics_keys)
    
    # Start the powermetrics command with -n 1 to limit it to one sample
    process = subprocess.Popen(['sudo', 'powermetrics', '--samplers', 'cpu_power,gpu_power,gpu_agpm_stats,smc', '-n', '1', '--format', 'text'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    powermetrics_dict = {}
    
    try:
        # sys.stderr.write("\r0%")
        # sys.stderr.flush()
        # ^ This goes before the sudo password prompt, so don't do it.
        #   "Machine model" will appear on the first line or so anyway.
        # Read stdout line by line
        for line in process.stdout:
            line = line.strip()
            
            # Check if any of the powermetrics_keys are in the line
            for key in powermetrics_keys:
                if key in line:
                    key_value = line.split(':', 1)
                    if len(key_value) == 2:
                        powermetrics_dict[key.strip()] = key_value[1].strip()
                        missing.discard(key)
                    break
            
            # Update progress
            sys.stderr.write("\r%s%%" % round(float(len(powermetrics_dict)) / float(keys_max) * 100.0))
            sys.stderr.flush()
            
            # Check if the required number of keys have been collected
            if len(powermetrics_dict) >= keys_max:
                break
        
    except KeyboardInterrupt:
        # Handle manual termination
        print("\nTerminating powermetrics command due to user interruption.", file=sys.stderr)
    
    finally:
        # Ensure the process is terminated
        process.terminate()
        process.wait()
        
        if missing:
            missing_keys = ', '.join(missing)
            print("\npowermetrics completed, but the following keys are missing: " + missing_keys, file=sys.stderr)
        else:
            print("\n100%", file=sys.stderr)
            # Process throttle_str to extract percentage and MHz
        
        throttle_str = powermetrics_dict.get("System Average frequency as fraction of nominal")
        if throttle_str:
            try:
                # Example format: "44.34% (798.20 MHz)"
                percentage, mhz = throttle_str.split(' (', 1)
                mhz = mhz.rstrip(' MHz)')
                powermetrics_dict["average_frequency_percent"] = percentage.strip(" %")
                powermetrics_dict["average_frequency"] = mhz.strip()
            except ValueError:
                print("Error processing throttle string format", file=sys.stderr)
                
    return powermetrics_dict


def combine_dictionaries(*args):
    """Combines multiple dictionaries."""
    combined_dict = args[0].copy() if args else {}
    
    for i in range(1, len(args)):
        combined_dict.update(args[i])
    
    return combined_dict

# Get key-value pairs from all sources
pmset_key_values = get_pmset_key_value_pairs()
cpu_speed_values = get_cpu_current_speed()
powermetrics_values = get_powermetrics_data()

# Combine all dictionaries
combined_values = combine_dictionaries(pmset_key_values, cpu_speed_values, powermetrics_values)

# Display the combined key-value pairs
for key, value in combined_values.items():
    print("{}={}".format(key.replace(".", "_").replace(" ", "_"), value))
