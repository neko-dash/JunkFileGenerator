#========================================================================================================
# @file         JunkFileGenerator.py
# @brief        Junk file generator
# @date         2025/6/5
# @author       Takashi Obara ( E-mail:cat.laboratory@gmail.com )
# @copyright    Takashi Obara
#========================================================================================================

#========================================================================================================
# Include definition
#========================================================================================================
import os
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.font as tkfont
import random
import threading
import platform
import subprocess
import shutil


#========================================================================================================
# Constant definition
#========================================================================================================

# Application information
APPLICATION_NAME                = "Junk file generator"
APPLICATION_FILE_NAME_STRING    = os.path.basename( __file__ )
APPLICATION_VERSION             = "1.0.0"
APPLICATION_DATE_TIME           = "2025/6/5 17:00:00 (UTC+9:00)"
COPYRIGHT                       = "Takashi Obara"

# Application constant
FILE_SIZE_UNITS = {
    "Gbyte": 1024**3,
    "Mbyte": 1024**2,
    "Kbyte": 1024,
    "byte": 1,
}
JUNK_FILE_PREFIX = "JunkFile_"


#========================================================================================================
# Class definition
#========================================================================================================
class JunkFileGenerator:

    #====================================================================================================
    # Private functions
    #====================================================================================================

    #----------------------------------------------------------------------------------------------------
    # @brief    Constructor
    # @param    self
    # @param    root
    #----------------------------------------------------------------------------------------------------
    def __init__(self, root):
        root.title(APPLICATION_NAME)
        self.root = root
        self.fillingUpFlag = tk.BooleanVar(value=True)
        self.fileSizeWithoutUnit = tk.IntVar(value=1)
        self.fileSizeUnit = tk.StringVar(value=list(FILE_SIZE_UNITS.keys())[0])
        self.numberOfFiles = tk.IntVar(value=1)
        self.outputFolderPathString = tk.StringVar(value=GetUserDocumentFolder())
        self.freeDriveSpaceString = tk.StringVar()
        self.createWidgets()
        self.refreshFields()
        self.writeNormalMessage("This is an app that generates random files.")

    #----------------------------------------------------------------------------------------------------
    # @brief    Create widgets
    # @param    self
    #----------------------------------------------------------------------------------------------------
    def createWidgets(self):

        # Frame
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

        # Fill entire drive
        row = 0
        ttk.Label(frame, text="Fill entire drive :").grid(row=row, column=0, sticky="w", padx=10)
        ttk.Checkbutton(frame, variable=self.fillingUpFlag, command=self.refreshFields).grid(row=row, column=1, sticky="w", padx=0)

        # File size
        row = 1
        ttk.Label(frame, text="File size :").grid(row=row, column=0, sticky="w", padx=10)
        file_size_frame = ttk.Frame(frame)
        file_size_frame.grid(row=row, column=1, sticky="w")
        ttk.Entry(file_size_frame, textvariable=self.fileSizeWithoutUnit, width=15, justify="right").pack(side="left", padx=0)
        ttk.Combobox(file_size_frame, textvariable=self.fileSizeUnit, values=list(FILE_SIZE_UNITS.keys()), width=7).pack(side="left", padx=0)

        # Number of files to generate
        row = 2
        ttk.Label(frame, text="Number of files :").grid(row=row, column=0, sticky="w", padx=10)
        self.numberOfFilesEntry = ttk.Entry(frame, textvariable=self.numberOfFiles, width=15, justify="right")
        self.numberOfFilesEntry.grid(row=row, column=1, sticky="w")

        # Output folder
        row = 3
        ttk.Label(frame, text="Output folder :").grid(row=row, column=0, sticky="w", padx=10)
        output_folder_path_frame = ttk.Frame(frame)
        output_folder_path_frame.grid(row=row, column=1, sticky="w")
        ttk.Entry(output_folder_path_frame, textvariable=self.outputFolderPathString, width=40).pack(side="left", padx=0)
        ttk.Button(output_folder_path_frame, text="Refer", command=self.selectOutputFolder).pack(side="left", padx=0)

        # Free drive space
        row = 4
        ttk.Label(frame, text="Free drive space :").grid(row=row, column=0, sticky="w", padx=10)
        ttk.Label(frame, textvariable=self.freeDriveSpaceString).grid(row=row, column=1, sticky="w", padx=0)

        # Buttons
        row = 5
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=row, column=1, sticky="ew", pady=10)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        ttk.Button(buttons_frame, text="Generate", command=self.startJunkFileGeneration).grid(row=0, column=0, padx=10)
        ttk.Button(buttons_frame, text="Open Folder", command=self.openOutputFolder).grid(row=0, column=1, padx=10)
        ttk.Button(buttons_frame, text="Close", command=self.root.quit).grid(row=0, column=2, padx=10)

        # Status message label
        row = 6
        self.status_label = ttk.Label(frame, text="")
        self.status_label.grid(row=row, column=1, sticky="ew", pady=5)

        # Application information
        row = 7
        ttk.Label(frame, text=f"Version : {APPLICATION_VERSION}, Copyright : {COPYRIGHT}", anchor="e", font=tkfont.Font(size=8)).grid(row=row, column=1, sticky="ew")

    #----------------------------------------------------------------------------------------------------
    # @brief    Refresh fields
    # @param    self
    #----------------------------------------------------------------------------------------------------
    def refreshFields(self):
        if self.fillingUpFlag.get():
            self.numberOfFilesEntry.config(state="disabled")
        else:
            self.numberOfFilesEntry.config(state="normal")

        folder_path_string = self.outputFolderPathString.get()
        free_drive_space_byte = self.getFreeDriveSpaceBytes(folder_path_string)
        self.freeDriveSpaceString.set(f"{free_drive_space_byte:,} bytes")



    def getFreeDriveSpaceBytes(self, folder_path_string):
        try:
            while not os.path.exists(folder_path_string):
                folder_path_string = os.path.dirname(folder_path_string)
                if folder_path_string == "":
                    return 0
            total, used, free = shutil.disk_usage(folder_path_string)
            return free
        except Exception as e:
            return 0




    #----------------------------------------------------------------------------------------------------
    # @brief    Select output folder
    # @param    self
    #----------------------------------------------------------------------------------------------------
    def selectOutputFolder(self):
        folder_path_string = filedialog.askdirectory(initialdir=self.outputFolderPathString.get())
        if folder_path_string:
            self.outputFolderPathString.set(folder_path_string)

    #----------------------------------------------------------------------------------------------------
    # @brief    Open output folder
    # @param    self
    #----------------------------------------------------------------------------------------------------
    def openOutputFolder(self):
        folder_path_string = self.outputFolderPathString.get()
        if os.path.isdir(folder_path_string):
            OpenFolder(folder_path_string)
        else:
            self.writeErrorMessage("Please specify a valid folder path.")

    #----------------------------------------------------------------------------------------------------
    # @brief    Write error message
    # @param    self
    # @param    message_string
    #----------------------------------------------------------------------------------------------------
    def writeErrorMessage(self, message_string):
        self.status_label.config(text=message_string, foreground="red")

    #----------------------------------------------------------------------------------------------------
    # @brief    Write normal message
    # @param    self
    # @param    message_string
    #----------------------------------------------------------------------------------------------------
    def writeNormalMessage(self, message_string):
        self.status_label.config(text=message_string, foreground="green")

    #----------------------------------------------------------------------------------------------------
    # @brief    Start junk file generation
    # @param    self
    #----------------------------------------------------------------------------------------------------
    def startJunkFileGeneration(self):
        threading.Thread(target=self.generateJunkFiles).start()

    #----------------------------------------------------------------------------------------------------
    # @brief    Generate junk files
    # @param    self
    #----------------------------------------------------------------------------------------------------
    def generateJunkFiles(self):
        try:
            output_folder_string = self.outputFolderPathString.get()
            if not os.path.isdir(output_folder_string):
                self.writeErrorMessage("Please specify a valid output folder.")
                return

            number_of_files = self.numberOfFiles.get()
            file_size_without_unit = self.fileSizeWithoutUnit.get()
            file_size_unit = self.fileSizeUnit.get()
            file_size_byte = file_size_without_unit * FILE_SIZE_UNITS[file_size_unit]
            file_index = self.getStartFileIndex(output_folder_string)
            self.writeNormalMessage(f"Generating files...(0/{number_of_files})")
            for file_count in range(number_of_files):
                file_name_string = self.getUniqueFilenameString(output_folder_string, file_index)
                self.writeRandomData(os.path.join(output_folder_string, file_name_string), file_size_byte)
                file_index += 1
                self.writeNormalMessage(f"Generating files...({file_count}/{number_of_files})")
                self.root.update_idletasks()

            self.writeNormalMessage(f"{number_of_files} file(s) generated successfully.")
        except Exception as e:
            self.writeErrorMessage(f"Error: {str(e)}")

    #----------------------------------------------------------------------------------------------------
    # @brief    Get start file index
    # @param    self
    # @param    output_folder_string
    #----------------------------------------------------------------------------------------------------
    def getStartFileIndex(self, output_folder_string):
        file_index = 0
        while True:
            file_name_string = f"{JUNK_FILE_PREFIX}{file_index:08d}.dat"
            if not os.path.exists(os.path.join(output_folder_string, file_name_string)):
                return file_index
            file_index += 1

    #----------------------------------------------------------------------------------------------------
    # @brief    Get unique file name string
    # @param    self
    # @param    output_folder_string
    # @param    file_index
    #----------------------------------------------------------------------------------------------------
    def getUniqueFilenameString(self, output_folder_string, file_index):
        while True:
            file_name_string = f"{JUNK_FILE_PREFIX}{file_index:08d}.dat"
            file_path = os.path.join(output_folder_string, file_name_string)
            if not os.path.exists(file_path):
                return file_name_string
            file_index += 1

    #----------------------------------------------------------------------------------------------------
    # @brief    Write random data
    # @param    self
    # @param    file_path
    # @param    file_size_byte
    #----------------------------------------------------------------------------------------------------
    def writeRandomData(self, file_path, file_size_byte):
        chunk_size_byte = 1024 * 1024  # Write in 1MB chunks
        written_size_byte = 0
        with open(file_path, "wb") as file_pointer:
            while written_size_byte < file_size_byte:
                write_size_byte = min(chunk_size_byte, file_size_byte - written_size_byte)
                file_pointer.write(os.urandom(write_size_byte))
                written_size_byte += write_size_byte


#========================================================================================================
# Private functions
#========================================================================================================

#--------------------------------------------------------------------------------------------------------
# @brief    Open folder
# @param    folder_path_string
#--------------------------------------------------------------------------------------------------------
def OpenFolder(folder_path_string):
    system = platform.system()
    if system == "Windows":
        os.startfile(folder_path_string)
    elif system == "Darwin":     # macOS
        subprocess.run(["open", folder_path_string])
    else:
        subprocess.run(["xdg-open", folder_path_string])

#----------------------------------------------------------------------------------------------------
# @brief    Get user document folder
#----------------------------------------------------------------------------------------------------
def GetUserDocumentFolder():
    system = platform.system()
    if system == 'Windows':
        return os.path.join(os.environ['USERPROFILE'], 'Documents')
    elif system == 'Darwin':  # macOS
        return os.path.join(os.path.expanduser('~'), 'Documents')
    elif system == 'Linux':
        try:
            return subprocess.check_output(['xdg-user-dir', 'DOCUMENTS']).decode().strip()
        except Exception:
            return os.path.join(os.path.expanduser('~'), 'Documents')
    else:
        return os.path.expanduser('~')  # fallback

#--------------------------------------------------------------------------------------------------------
# @brief    Main
#--------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = JunkFileGenerator(root)
    root.mainloop()

