from __future__ import print_function
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
        print("Error: pmset command failed with return code", result.returncode)

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
        print("Error: sysctl command failed with return code", result.returncode)

    return cpu_dict

def get_powermetrics_data():
    """Gets throttling-related data from 'powermetrics'."""
    # Start the powermetrics command
    process = subprocess.Popen(['sudo', 'powermetrics', '--samplers', 'cpu_power', '--format', 'text'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    powermetrics_dict = {}
    start_seconds = None
    max_seconds = 60.0
    timeout = False

    try:
        while True:
            # Read stdout line by line
            line = process.stdout.readline()
            
            # Check for "Machine model" to start timing
            if start_seconds is None and "Machine model" in line:
                start_seconds = time.time()
                sys.stderr.write("\r0%")
            
            # If we have started timing, read the line and process it
            if start_seconds is not None:
                current_seconds = time.time()
                elapsed_seconds = current_seconds - start_seconds
                
                if "System Average frequency as fraction of nominal" in line:
                    key, value = line.split(':', 1)
                    powermetrics_dict[key.strip()] = value.strip()
                
                elif 'CPU_Speed_Limit' in line or 'CPU Power' in line:
                    key, value = line.split(':', 1)
                    powermetrics_dict[key.strip()] = value.strip()

                # Check for timeout
                if elapsed_seconds >= max_seconds:
                    timeout = True
                    sys.stderr.write("\r100%\n")
                    break
                
                # Update progress
                sys.stderr.write("\r%s%%" % round((elapsed_seconds / max_seconds) * 100))
                sys.stderr.flush()

    except KeyboardInterrupt:
        # Handle manual termination
        print("\nTerminating powermetrics command due to user interruption.")
    
    finally:
        # Ensure the process is terminated
        process.terminate()
        process.wait()
        
        if timeout:
            print("powermetrics timed out")

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
print("Combined key-value pairs:")
for key, value in combined_values.items():
    print("{}: {}".format(key, value))
