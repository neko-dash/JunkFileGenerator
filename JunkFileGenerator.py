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
import time


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
JUNK_FILE_PREFIX    = "JunkFile_"
CHUNK_SIZE_BYTE     = 1024 * 1024   # Write in 1MB chunks


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

        # Initialize class
        root.title(APPLICATION_NAME)
        self.root                       = root
        self.fillingUpModeEnabled       = tk.BooleanVar(value=True)
        self.fileSizeWithoutUnit        = tk.IntVar(value=1)
        self.fileSizeUnit               = tk.StringVar(value=list(FILE_SIZE_UNITS.keys())[0])
        self.numberOfFiles              = tk.IntVar(value=1)
        self.outputFolderPathString     = tk.StringVar(value=GetUserDocumentFolder())
        self.freeDriveSpaceString       = tk.StringVar()
        self.junkFileGenerationCancel   = threading.Event()
        self.drivePathString            = ""

        # Initialize widget
        self.createWidgets()
        self.refreshNumberOfFilesEntry()
        self.outputFolderChangedEvent()
        self.writeNormalMessage("This is an app that generates random files.")
        self.outputFolderPathString.trace_add("write", self.outputFolderChangedEvent)

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
        ttk.Checkbutton(frame, variable=self.fillingUpModeEnabled, command=self.refreshNumberOfFilesEntry).grid(row=row, column=1, sticky="w", padx=0)

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
        free_space_frame = ttk.Frame(frame)
        free_space_frame.grid(row=row, column=1, sticky="w")
        ttk.Button(free_space_frame, text="Update", command=self.outputFolderChangedEvent).pack(side="left", padx=(0, 5))
        ttk.Label(free_space_frame, textvariable=self.freeDriveSpaceString).pack(side="left")

        # Buttons
        row = 5
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=row, column=1, sticky="ew", pady=10)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        buttons_frame.columnconfigure(3, weight=1)
        ttk.Button(buttons_frame, text="Generate",      command=self.startJunkFileGeneration    ).grid(row=0, column=0, padx=2)
        ttk.Button(buttons_frame, text="Cancel",        command=self.cancelJunkFileGeneration   ).grid(row=0, column=1, padx=2)
        ttk.Button(buttons_frame, text="Open Folder",   command=self.openOutputFolder           ).grid(row=0, column=2, padx=2)
        ttk.Button(buttons_frame, text="Close",         command=self.root.quit                  ).grid(row=0, column=3, padx=2)

        # Status message label
        row = 6
        self.status_label = ttk.Label(frame, text="")
        self.status_label.grid(row=row, column=1, sticky="ew", pady=5)

        # Application information
        row = 7
        ttk.Label(frame, text=f"Version : {APPLICATION_VERSION}, Copyright : {COPYRIGHT}", anchor="e", font=tkfont.Font(size=8)).grid(row=row, column=1, sticky="ew")

    #----------------------------------------------------------------------------------------------------
    # @brief    Refresh number of files entry
    # @param    self
    #----------------------------------------------------------------------------------------------------
    def refreshNumberOfFilesEntry(self):
        if self.fillingUpModeEnabled.get():
            state = "disabled"
        else:
            state = "normal"
        self.numberOfFilesEntry.config(state=state)

    #----------------------------------------------------------------------------------------------------
    # @brief    Refresh free drive space label
    # @param    self
    # @param    free_drive_space_bytes
    #----------------------------------------------------------------------------------------------------
    def refreshFreeDriveSpaceLabel(self, free_drive_space_bytes):
        kbyte = 1024
        mbyte = 1024 * kbyte
        gbyte = 1024 * mbyte
        tbyte = 1024 * gbyte

        if free_drive_space_bytes >= tbyte:
            self.freeDriveSpaceString.set(f"{free_drive_space_bytes / tbyte:.1f} Tbyte  (={free_drive_space_bytes:,} bytes)")
        elif free_drive_space_bytes >= gbyte:
            self.freeDriveSpaceString.set(f"{free_drive_space_bytes / gbyte:.1f} Gbyte  (={free_drive_space_bytes:,} bytes)")
        elif free_drive_space_bytes >= mbyte:
            self.freeDriveSpaceString.set(f"{free_drive_space_bytes / mbyte:.1f} Mbyte  (={free_drive_space_bytes:,} bytes)")
        elif free_drive_space_bytes >= kbyte:
            self.freeDriveSpaceString.set(f"{free_drive_space_bytes / kbyte:.1f} Kbyte  (={free_drive_space_bytes:,} bytes)")
        else:
            self.freeDriveSpaceString.set(f"{free_drive_space_bytes:,} bytes")

    #----------------------------------------------------------------------------------------------------
    # @brief    Set drive path string
    # @param    self
    # @param    output_folder_path_string
    #----------------------------------------------------------------------------------------------------
    def setDrivePathString(self, output_folder_path_string):
        try:
            while not os.path.exists(output_folder_path_string):
                output_folder_path_string = os.path.dirname(output_folder_path_string)
                if output_folder_path_string == "":
                    self.drivePathString = ""
                    return
            self.drivePathString = output_folder_path_string
            return
        except Exception as e:
            self.drivePathString = ""

    #----------------------------------------------------------------------------------------------------
    # @brief    Get free drive space
    # @param    self
    # @return   Free drive space [byte]
    #----------------------------------------------------------------------------------------------------
    def getFreeDriveSpaceBytes(self):
        try:
            if self.drivePathString == "":
                return 0
            total, used, free_drive_space_byte = shutil.disk_usage(self.drivePathString)
            return free_drive_space_byte
        except Exception as e:
            return 0

    #----------------------------------------------------------------------------------------------------
    # @brief    Output folder changed event
    # @param    self
    # @param    *args
    #----------------------------------------------------------------------------------------------------
    def outputFolderChangedEvent(self, *args):
        self.setDrivePathString(self.outputFolderPathString.get())
        self.refreshFreeDriveSpaceLabel(self.getFreeDriveSpaceBytes())

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
        self.junkFileGenerationCancel.clear()
        threading.Thread(target=self.generateJunkFiles, daemon=True).start()

    #----------------------------------------------------------------------------------------------------
    # @brief    Cancel junk file generation
    # @param    self
    #----------------------------------------------------------------------------------------------------
    def cancelJunkFileGeneration(self):
        self.junkFileGenerationCancel.set()

    #----------------------------------------------------------------------------------------------------
    # @brief    Get file size
    # @param    self
    # @return   File size [byte]
    #----------------------------------------------------------------------------------------------------
    def getFileSizeByte(self):
        file_size_without_unit  = self.fileSizeWithoutUnit.get()
        file_size_unit          = self.fileSizeUnit.get()
        file_size_byte          = file_size_without_unit * FILE_SIZE_UNITS[file_size_unit]
        return file_size_byte

    #----------------------------------------------------------------------------------------------------
    # @brief    Get start file index
    # @param    self
    # @return   Start file index
    #----------------------------------------------------------------------------------------------------
    def getStartFileIndex(self):
        file_index = 0
        output_folder_path_string = self.outputFolderPathString.get()
        while True:
            file_name_string = f"{JUNK_FILE_PREFIX}{file_index:08d}.dat"
            if not os.path.exists(os.path.join(output_folder_path_string, file_name_string)):
                return file_index
            file_index += 1

    #----------------------------------------------------------------------------------------------------
    # @brief    Ceil divide
    # @param    self
    # @param    numerator
    # @param    denominator
    # @return   Ceil divide
    #----------------------------------------------------------------------------------------------------
    def ceilDivide(self, numerator: int, denominator: int) -> int:
        return -(-numerator // denominator)

    #----------------------------------------------------------------------------------------------------
    # @brief    Is file generation ongoing
    # @param    self
    # @param    free_drive_space_bytes
    # @param    filling_up_mode_enabled
    # @param    file_count
    # @param    number_of_files
    # @retval   True
    # @retval   False
    #----------------------------------------------------------------------------------------------------
    def isFileGenerationOngoing(self, free_drive_space_bytes, filling_up_mode_enabled, file_count, number_of_files):
        if free_drive_space_bytes <= 0:
            return False
        if filling_up_mode_enabled:
            return True
        if file_count < number_of_files:
            return True
        return False

    #----------------------------------------------------------------------------------------------------
    # @brief    Get unique file name string
    # @param    self
    # @param    output_folder_path_string
    # @param    file_index
    # @return   Unique file name string
    #----------------------------------------------------------------------------------------------------
    def getUniqueFilenameString(self, output_folder_path_string, file_index):
        while True:
            file_name_string = f"{JUNK_FILE_PREFIX}{file_index:08d}.dat"
            file_path = os.path.join(output_folder_path_string, file_name_string)
            if not os.path.exists(file_path):
                return file_name_string
            file_index += 1

    #----------------------------------------------------------------------------------------------------
    # @brief    Get elapsed time string
    # @param    self
    # @param    start_time
    # @return   Elapsed time string
    #----------------------------------------------------------------------------------------------------
    def getElapsedTimeString(self, start_time):
        elapsed_time_sec    = time.time() - start_time
        mins, secs          = divmod(int(elapsed_time_sec), 60)
        hours, mins         = divmod(mins, 60)
        return f"{hours:02d}h{mins:02d}m{secs:02d}s"

    #----------------------------------------------------------------------------------------------------
    # @brief    Get estimated time of arrival string
    # @param    self
    # @param    start_time
    # @param    total_finish_size_byte
    # @param    total_goal_size_byte
    # @return   Estimated time of arrival string
    #----------------------------------------------------------------------------------------------------
    def getEstimatedTimeOfArrivalString(self, start_time, total_finish_size_byte, total_goal_size_byte):
        elapsed_time_sec = time.time() - start_time
        if total_finish_size_byte <= 0 or elapsed_time_sec <= 0:
            return "-"

        bytes_per_sec           = total_finish_size_byte / elapsed_time_sec
        remaining_size_bytes    = total_goal_size_byte - total_finish_size_byte
        estimated_seconds       = remaining_size_bytes / bytes_per_sec
        mins, secs              = divmod(int(estimated_seconds), 60)
        hours, mins             = divmod(mins, 60)
        return f"{hours:02d}h{mins:02d}m{secs:02d}s"

    #----------------------------------------------------------------------------------------------------
    # @brief    Generate junk files
    # @param    self
    #----------------------------------------------------------------------------------------------------
    def generateJunkFiles(self):
        try:

            # Check output folder path
            output_folder_path_string = self.outputFolderPathString.get()
            if not os.path.isdir(output_folder_path_string):
                self.writeErrorMessage("Please specify a valid output folder.")
                return

            # Initialize loop conditions
            filling_up_mode_enabled = self.fillingUpModeEnabled.get()
            file_size_byte          = self.getFileSizeByte()
            free_drive_space_bytes  = self.getFreeDriveSpaceBytes()
            file_index              = self.getStartFileIndex()
            file_count              = 0
            if filling_up_mode_enabled:
                number_of_files = self.ceilDivide(free_drive_space_bytes, file_size_byte)
            else:
                number_of_files = self.numberOfFiles.get()

            # Check file size and number of files
            if file_size_byte <= 0 or number_of_files <= 0:
                self.writeErrorMessage("Check the file size and number of files.")
                return

            # Generate junk files
            total_goal_size_byte = min(file_size_byte * number_of_files, free_drive_space_bytes)
            total_finish_size_byte = 0
            start_time = time.time()
            while self.isFileGenerationOngoing(free_drive_space_bytes, filling_up_mode_enabled, file_count, number_of_files):

                # Decide junk file size
                if free_drive_space_bytes >= file_size_byte:
                    file_goal_size_byte = file_size_byte
                else:
                    file_goal_size_byte = free_drive_space_bytes

                # Decide junk file path
                file_name_string    = self.getUniqueFilenameString(output_folder_path_string, file_index)
                file_path           = os.path.join(output_folder_path_string, file_name_string)

                # Write junk file
                with open(file_path, "wb") as file_pointer:
                    file_finish_size_byte = 0

                    while file_finish_size_byte < file_goal_size_byte:

                        # Check cancel
                        if self.junkFileGenerationCancel.is_set():
                            elapsed_time_string = self.getElapsedTimeString(start_time)
                            self.writeNormalMessage(f"File generation cancelled. (File:{file_count}/{number_of_files}, Total:{total_finish_size_byte/total_goal_size_byte*100:.3f}%), {elapsed_time_string})")
                            return

                        # Refresh widgets
                        estimated_time_of_arrival_string = self.getEstimatedTimeOfArrivalString(start_time, total_finish_size_byte, total_goal_size_byte)
                        self.refreshFreeDriveSpaceLabel(free_drive_space_bytes)
                        self.writeNormalMessage(f"Generating files... (File:{file_count}/{number_of_files}, Total:{total_finish_size_byte/total_goal_size_byte*100:.3f}%, {estimated_time_of_arrival_string})")
                        self.root.update_idletasks()

                        # Write random data
                        write_size_byte = min(CHUNK_SIZE_BYTE, file_goal_size_byte - file_finish_size_byte)
                        file_pointer.write(os.urandom(write_size_byte))
                        file_finish_size_byte   += write_size_byte
                        total_finish_size_byte  += write_size_byte
                        free_drive_space_bytes = self.getFreeDriveSpaceBytes()

                # Refresh loop conditions
                file_index += 1
                file_count += 1

            elapsed_time_string = self.getElapsedTimeString(start_time)
            self.refreshFreeDriveSpaceLabel(free_drive_space_bytes)
            self.writeNormalMessage(f"File generation completed. (File:{file_count}/{number_of_files}, Total:{total_finish_size_byte/total_goal_size_byte*100:.3f}%), {elapsed_time_string})")
        except Exception as e:
            free_drive_space_bytes = self.getFreeDriveSpaceBytes()
            self.refreshFreeDriveSpaceLabel(free_drive_space_bytes)
            self.writeErrorMessage(f"Error: {str(e)}")


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
    root.resizable(False, False)
    app = JunkFileGenerator(root)
    root.mainloop()

