#!/bin/bash

# Original Git-derived version identifier
version=$(git describe --always --tags --dirty --long)

# Check if the version contains Git metadata (commits and commit hash)
if [[ "$version" =~ ([0-9]+\.[0-9]+\.[0-9]+)(-([0-9]+)-g([0-9a-f]+)(-dirty)?)? ]]; then
    core_version="${BASH_REMATCH[1]}" # 0.1.0
    commit_count="${BASH_REMATCH[3]}" # 1 (optional)
    commit_hash="${BASH_REMATCH[4]}"  # 281941e (optional)
    dirty="${BASH_REMATCH[5]}"        # -dirty (optional)

    # If there's no Git metadata, the version is already PEP 440 compliant
    if [[ -z "$commit_count" || "$commit_count" == "0" ]]; then
        pep440_version="$core_version"
    else
        # Construct the PEP 440 compliant version
        pep440_version="${core_version}+${commit_count}.g${commit_hash}"

        # Append .dirty if the version has '-dirty'
        if [[ -n "$dirty" ]]; then
            pep440_version="${pep440_version}.dirty"
        fi
    fi
else
    pep440_version="0.0.0+unknown"
fi
echo "__version__ = \"$pep440_version\"" >src/eve2cml/_version.py
