#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Download the Northwind CSV dataset by cloning the neo4j-contrib repo.

Usage:
    python download_northwind.py --workspace ./workspace

Output:
    {workspace}/data/*.csv
"""

import argparse
import os
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description="Download Northwind dataset")
    parser.add_argument("--workspace", default="workspace", help="Workspace directory")
    args = parser.parse_args()

    out_dir = os.path.join(args.workspace, "data")
    os.makedirs(out_dir, exist_ok=True)

    repo_url = "https://github.com/neo4j-contrib/northwind-neo4j.git"
    temp_clone_dir = os.path.join(args.workspace, "tmp_northwind_clone")

    print("=== Data Analyst Agent: Download Northwind Dataset ===")
    print(f"Cloning from: {repo_url}")

    try:
        # Clean up temp dir if it exists
        if os.path.exists(temp_clone_dir):
            shutil.rmtree(temp_clone_dir)

        # Clone the repo
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_clone_dir],
            check=True,
            capture_output=True,
        )

        src_data_dir = os.path.join(temp_clone_dir, "data")
        if not os.path.exists(src_data_dir):
            print(f"❌ Error: 'data' directory not found in the cloned repo.")
            return

        # Copy CSV files
        copied_files = []
        for item in os.listdir(src_data_dir):
            if item.endswith(".csv"):
                src_file = os.path.join(src_data_dir, item)
                dst_file = os.path.join(out_dir, item)
                shutil.copy2(src_file, dst_file)
                copied_files.append(item)

        print(f"\n✅ Successfully copied {len(copied_files)} CSV files to {out_dir}:")
        for f in sorted(copied_files):
            print(f"  - {f}")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Git clone failed: {e.stderr.decode()}")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        # Clean up
        if os.path.exists(temp_clone_dir):
            shutil.rmtree(temp_clone_dir)


if __name__ == "__main__":
    main()
