from __future__ import print_function
import subprocess


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
    # Run powermetrics command with required flags
    result = subprocess.Popen(['sudo', 'powermetrics', '--samplers', 'cpu_power', '--format', 'text'],
                              stdout=subprocess.PIPE)
    output, _ = result.communicate()

    powermetrics_dict = {}

    if result.returncode == 0:
        # Process the powermetrics output
        for line in output.splitlines():
            line = line.strip()
            # Example key indicators from powermetrics output
            if 'System Average frequency as fraction of nominal' in line:
                key, value = line.split(':', 1)
                powermetrics_dict[key.strip()] = value.strip()
            elif 'CPU_Speed_Limit' in line or 'CPU Power' in line:
                key, value = line.split(':', 1)
                powermetrics_dict[key.strip()] = value.strip()
    else:
        print("Error: powermetrics command failed with return code", result.returncode)

    return powermetrics_dict


def combine_dictionaries(*args):
    """Combines multiple dictionaries."""
    # Make a copy of the first dictionary
    combined_dict = args[0].copy() if args else {}
    
    # Iterate through the remaining dictionaries and update combined_dict
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
