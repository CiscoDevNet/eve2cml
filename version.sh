#!/bin/bash

# Original Git-derived version identifier
version=$(git describe --always --tags --dirty --long)

# set -x

# Check if the version contains Git metadata (commits and commit hash)
if [[ "$version" =~ ([0-9]+\.[0-9]+\.[0-9]+)(\.post[0-9]+)?(-([0-9]+)-g([0-9a-f]+)(-dirty)?)? ]]; then
    core_version="${BASH_REMATCH[1]}" # 0.1.0
    post="${BASH_REMATCH[2]}"         # post1 (optional)
    commit_count="${BASH_REMATCH[4]}" # 1 (optional)
    commit_hash="${BASH_REMATCH[5]}"  # 281941e (optional)
    dirty="${BASH_REMATCH[6]}"        # -dirty (optional)

    # If there's no Git metadata, the version is already PEP 440 compliant
    if [[ -n "$post" ]]; then
        pep440_version="${core_version}${post}"
    elif [[ -z "$commit_count" || "$commit_count" == "0" ]]; then
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
