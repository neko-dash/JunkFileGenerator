```
#========================================================================================================
# @file         JunkFileGenerator.txt
# @version      1.0.0
# @date         2025/6/5
# @author       Takashi Obara ( E-mail:cat.laboratory@gmail.com )
# @copyright    Takashi Obara
#========================================================================================================

#========================================================================================================
# 1. Overview
#========================================================================================================

    "JunkFileGenerator" is an application that generates files filled with random content.

    It is intended for use in securely erasing information when disposing of or transferring devices such as PCs, SSDs, hard disks, and memory sticks.
    The author uses this application as a supplementary tool alongside existing data erasure software.
    If a obtained storage device is completely filled with junk files from the start, a malicious user is likely to give up on recovering any deleted files.

    Surprisingly, there was no user-friendly software of this kind available, so I decided to create one myself as a learning experience.
    I designed it in Python with the intention of using it on various operating systems, including Linux, Windows, and MacOS, which I own.


#========================================================================================================
# 2. Usage
#========================================================================================================

    2.1. How to Launch
        Save JunkFileGenerator.py in any folder and run the following command:

            python .\JunkFileGenerator.py

        You must have python installed beforehand.

    2.2. How to Use
        After launching, configure the following settings and press the "Generate" button:

            --------------------+-----------------------------------------------------------------
             Setting Name       | Description
            --------------------+-----------------------------------------------------------------
             File size          | Size of each generated file.
                                | Units: Gbyte, Mbyte, Kbyte, or byte.
            --------------------+-----------------------------------------------------------------
             Number of files    | Number of files to generate.
            --------------------+-----------------------------------------------------------------
             Output folder      | Destination folder for the generated files.
            --------------------+-----------------------------------------------------------------

        Please enjoy filling your storage device to its limit with junk files!


#========================================================================================================
# 3. Development Environment
#========================================================================================================

    - MicrosoftWindows 11 Pro 23H2
    - Microsoft Visual Studio Code Version 1.96.4 (user setup)
    - Python 3.13.3
    - git version 2.47.1.windows.2
    - TortoiseGit Version 2.17.0

#========================================================================================================
```
