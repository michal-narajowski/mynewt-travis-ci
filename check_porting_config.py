#!/usr/bin/env python3

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from utils import backend
import os
import subprocess

TRAVIS_REPO_SLUG = os.environ['TRAVIS_REPO_SLUG']
TRAVIS_PULL_REQUEST = os.environ['TRAVIS_PULL_REQUEST']
CHECK_PORTING_CONFIG_BOT_ID = "<!-- check-porting-config-bot -->"
DEBUG = bool(os.environ.get('DEBUG', False))
SOURCE_EXTS = ['.c', '.h']

GH_COMMENT_TITLE = """
{}

## Style check summary"""
GH_CODING_STYLE_URL = """
### Some changes are required to ported config files.
Run `mynewt-nimble/porting/update_generated_files.sh` script from your project 
root directory to update these files automatically.
"""
GH_COMMENT_DIFF = """
#### {}
<details>

```diff
{}
```

</details>"""


def get_diff():
    diff_cmd = "git diff"
    if DEBUG:
        print("Executing: " + diff_cmd)
    output = subprocess.check_output(diff_cmd.split()).decode().strip()
    if DEBUG:
        print("output: " + output)
    return output


def exec_update_script():
    cwd = os.getcwd()
    print("PWD: " + cwd)
    output = subprocess.check_output('ls'.split()).decode().strip()
    print(output)
    cmd = "./porting/update_generated_files.sh"
    if DEBUG:
        print("Executing: " + cmd)
    output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT).decode().strip()
    if DEBUG:
        print("output: " + output)
    return


def main():
    if TRAVIS_PULL_REQUEST == "false":
        print("Not a PR, exiting")
        exit(0)

    owner, repo = TRAVIS_REPO_SLUG.split("/")

    if repo != 'mynewt-nimble':
        print("This works only on mynewt-nimble")
        exit(1)

    exec_update_script()

    diff = get_diff()

    if len(diff) == 0:
        print("No changes required")
        exit(0)

    comments = [GH_COMMENT_TITLE.format(CHECK_PORTING_CONFIG_BOT_ID),
                GH_CODING_STYLE_URL,
                GH_COMMENT_DIFF.format("Required changes", diff)]
    comment = "\n".join(comments)

    if DEBUG:
        print("Comment body: ", comment)
    if not backend.new_comment(owner, repo, TRAVIS_PULL_REQUEST, comment):
        exit(1)


if __name__ == '__main__':
    main()
