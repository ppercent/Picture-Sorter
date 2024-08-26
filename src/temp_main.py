from ctypes import Structure, c_char_p, c_int, POINTER
import customtkinter as CTk
from time import sleep
import tkinter as tk
import threading
import ctypes
import os
# === TO DO LIST ===
# 1. [DONE] Rename file if name is already used (check for naming conflicts)
# 2. [DONE] Make no sorting type an option (if no sorting && no naming -> cannot click start)
# 3. [DONE] Add more checks to avoid data loss / undefined behaviour (permission, special file, system file)
# 4. [DONE] Load shared library/dll properly (with relative path)
# 5. [TODO] (MAYBE) Button to revert changes made by the program after operation is completed
# 6. [DONE] Upgrade the UI with better understanding of the layout & switch language button (default english, add french)
# 7. [TODO] Split the program in different file folders in an organized way & implement the ui & logic correctly
# 7. [TODO] Let the user choose whether the program will replace the file name or just insert the date
# 8. [TODO] Compile the script to a .exe file / linux executable


# Button to revert changes:
# 1- Implement the getDestinationPath in c++
# 2- make the function to get file to add the destination path in the folder
# 3- iterate the folder and move the file from the destination to the original source
# 4- delete folders that the program created

class Image(Structure):
    _fields_ = [("path", c_char_p),
                ("date", c_char_p)]

class Other(Structure):
    _fields_ = [("path", c_char_p),
                ("date", c_char_p)]

class Folder(Structure):
    _fields_ = [("images", POINTER(Image)),
                ("image_count", c_int),
                ("others", POINTER(Other)),
                ("other_count", c_int)]
    

if os.name == 'nt':
    FileUtils = ctypes.CDLL(os.getcwd() + '\\libFileUtils.dll')
else:
    FileUtils = ctypes.CDLL(os.getcwd() + '\\libFileUtils.so')

FileUtils.getImages.argtypes = [c_char_p]
FileUtils.getImages.restype = POINTER(Folder)

FileUtils.freeFolder.argtypes = [POINTER(Folder)]
FileUtils.freeFolder.restype = None

FileUtils.moveFile.argtypes = [c_char_p, c_char_p]
FileUtils.moveFile.restype = c_int

class App(CTk.CTk):
    def __init__(self):
        super().__init__()

        # set mainloop
        self.geometry('500x450')
        self.title('PicSorter')
        self.resizable(False, False)

        # fonts
        defaultFont = ('ubunbtu', 15)
        defaultItalicFont = ('ubunbtu', 15, 'italic')
        headFont = ('ubunbtu', 18)

        # widgets
        self.buttonState = '001'
        self.filetypeCheck = ''
        self.picturePath = ''
        self.sortingType = []
        self.namingType = ''

        # picture path
        pathEntryLabel = CTk.CTkLabel(master=self, text='path to pictures', font=headFont)
        pathEntryLabel.pack()
        self.currentPathEntry = CTk.StringVar() #REMOVE THE VALUE LATER
        self.currentPathEntry.trace_add("write", self.updatePathEntryColor)
        self.pathEntry = CTk.CTkEntry(master=self, width=210, height=32, font=(defaultFont), textvariable=self.currentPathEntry)
        self.pathEntry.pack()
        
        # filetype check
        self.currentFileTypeCheckbox = CTk.StringVar(value='on')
        self.fileTypeCheckbox = CTk.CTkCheckBox(master=self, text='only sort images', onvalue='on', offvalue='off', variable=self.currentFileTypeCheckbox)
        self.fileTypeCheckbox.pack(pady=10)

        # sorting type
        self.sortingType = []
        sortingTypeLabel = CTk.CTkLabel(master=self, text='sorting type', font=headFont)
        sortingTypeLabel.pack()
        sortingTypeLabelHelp = CTk.CTkLabel(master=self, text='yyyy/yyyy mm dd', font=defaultItalicFont)
        sortingTypeLabelHelp.pack()
        self.currentSortingType = CTk.StringVar()
        self.currentSortingType.trace_add('write', lambda *args: self.checkSortingType(self.currentSortingType.get()))
        self.sortingTypeEntry = CTk.CTkEntry(master=self, width=210, height=32, font=(defaultFont), textvariable=self.currentSortingType)
        self.sortingTypeEntry.pack()

        # naming type
        self.namingType = ''
        namingTypeLabel = CTk.CTkLabel(master=self, text='naming type', font=headFont)
        namingTypeLabel.pack()
        sortingTypeLabelHelp = CTk.CTkLabel(master=self, text='yyyy mm dd hh MM ss (leave empty to keep default name)', font=defaultItalicFont)
        sortingTypeLabelHelp.pack()
        self.currentNamingType = CTk.StringVar()
        self.currentNamingType.trace_add('write', lambda *args: self.checkNamingType(self.currentNamingType.get().replace(' ', '')))
        self.namingTypeEntry = CTk.CTkEntry(master=self, width=210, height=32, font=(defaultFont), textvariable=self.currentNamingType)
        self.namingTypeEntry.pack()

        # text info
        self.folderLabelVar = tk.StringVar(value='')
        self.folderLabel = CTk.CTkLabel(master=self, wraplength=270, compound='left', anchor=CTk.W, text_color='#251b1b', font=('ubuntu', 15), textvariable=self.folderLabelVar)
        #last: 470 | 12 for font

        # wait var
        self.buttonClicked = CTk.BooleanVar(value=False)
        self.click = None

        # confirm frame
        self.confirmFrame = CTk.CTkFrame(master=self, width=200, height=100)
        self.confirmFrame.pack_propagate(False)
        self.confirmPressed = CTk.BooleanVar(value=False)

        # button start & stop
        self.startButton = CTk.CTkButton(master=self, text='START', state=CTk.DISABLED, fg_color='gray', command=self.startOnClick)
        self.startButton.pack(pady=10)

        # handle stop
        self.folder = None
        self.protocol('WM_DELETE_WINDOW', self.onClose)

    def countFilesIdle(self):
        # fake counter lol
        for i in range(self.folder.contents.image_count + 1):
            self.folderLabelVar.set(f'Total images: {i}\nTotal others: 0')

        for i in range(self.folder.contents.other_count + 1):
            self.folderLabelVar.set(f'Total images: {self.folder.contents.image_count}\nTotal others: {i}')

    def moveFolderIdle(self):
        self.movedImages = 0
        self.movedOthers = 0
        self.imgRetval = -1
        self.otherRetval = -1

        for i in range(self.folder.contents.image_count):
            currentImagePath = self.folder.contents.images[i].path.decode('utf-8')
            currentImageDate = self.folder.contents.images[i].date.decode('utf-8')
            destinationImagePath = self.getDestinationPath(currentImagePath, currentImageDate, self.picturePath, self.sortingType, self.namingType)

            self.folderLabelVar.set(f'Processing: \'{self.getFileName(currentImagePath)}\'\nWith date: {currentImageDate}')

            try:
                self.imgRetval = FileUtils.moveFile(bytes(currentImagePath, 'utf-8'), bytes(destinationImagePath, 'utf-8'))
            except OSError as e:
                print(f'----Error moving the file: {e}\ncurrent: {currentImagePath}\ndestination: {destinationImagePath}----\n')
            print(self.imgRetval)
            if self.imgRetval == 0:
                self.movedImages += 1
                continue
            else:
                # handle potential errors, pause the process
                continue
                

        for i in range(self.folder.contents.other_count):
            if i in self.othersBlackList:
                continue

            currentOtherPath = self.folder.contents.others[i].path.decode('utf-8')
            currentOtherDate = self.folder.contents.others[i].date.decode('utf-8')
            print(currentOtherPath)
            destinationOtherPath = self.getDestinationPath(currentOtherPath, currentOtherDate, self.picturePath, self.sortingType, self.namingType)

            self.folderLabelVar.set(f'Processing: \'{self.getFileName(currentOtherPath)}\'\nWith date: {currentOtherDate}')

            try:
                self.otherRetval = FileUtils.moveFile(bytes(currentOtherPath, 'utf-8'), bytes(destinationOtherPath, 'utf-8'))
            except OSError as e:
                print(f'----Error moving the file: {e}\ncurrent: {currentOtherPath}\ndestination: {destinationOtherPath}----\n')
            print(self.otherRetval)
            if self.otherRetval == 0:
                self.movedOthers += 1
                continue
            else:
                # handle potential errors, pause the process
                continue
        
        self.folderLabelVar.set(f'Successfully sorted {self.movedImages} images and {self.movedOthers} others.')

    def startOnClick(self):
        # show text info
        self.folderLabel.pack(padx=10, pady=17, side='left', anchor='sw')

        # get data
        self.filetypeCheck = self.currentFileTypeCheckbox.get()
        self.picturePath = self.currentPathEntry.get()
        self.sortingType = self.formatType(self.currentSortingType.get())
        self.namingType = self.formatType(self.currentNamingType.get(), True)

        # disable entry interactions
        self.pathEntry.configure(state=CTk.DISABLED)
        self.fileTypeCheckbox.configure(state=CTk.DISABLED)
        self.sortingTypeEntry.configure(state=CTk.DISABLED)
        self.namingTypeEntry.configure(state=CTk.DISABLED)
        self.startButton.configure(state=CTk.DISABLED)


        # handle start on click
        self.folder = FileUtils.getImages(self.picturePath.encode('utf-8'))
        print('folder created')
        self.othersBlackList = []
        # self.folderLabelVar.set(f'Total images: {self.folder.contents.image_count}\nTotal others: {self.folder.contents.other_count}')
        
        threading.Thread(target=self.countFilesIdle).start()
        
        confirmButton = CTk.CTkButton(master=self.confirmFrame, text='Confirm', width=160,
                                      height=42, fg_color='#5784bf', hover_color='#5077aa',
                                      text_color='black', font=('ubuntu', 15), corner_radius=30,
                                      command=lambda: self.confirmPress())
        confirmButton.pack(padx=10, pady=29, side='bottom')
        self.confirmFrame.pack(padx=10, side='right', anchor='se')
        confirmButton.wait_variable(self.confirmPressed)

        if self.filetypeCheck == 'on':
            # Create the frame
            checkFrame = CTk.CTkFrame(master=self, width=200, height=100)
            checkFrame.pack_propagate(False)
            
            # Create buttons
            buttonYesToAll = CTk.CTkButton(master=checkFrame, text='Yes to all', width=80,
                                           height=42, fg_color='#36ce19', hover_color='#33bb19',
                                           text_color='black', font=('ubuntu', 15), command=lambda: self.buttonClick('yes_to_all'))
            
            buttonYes = CTk.CTkButton(master=checkFrame, text='YES', width=80,
                                      height=42, fg_color='#36ce19', hover_color='#33bb19',
                                      text_color='black', font=('ubuntu', 20), command=lambda: self.buttonClick('yes'))
            
            buttonNo = CTk.CTkButton(master=checkFrame, text='NO', width=180,
                                     height=42, fg_color='#CB4821', hover_color='#b7421e',
                                     text_color='black', font=('ubuntu', 25), command=lambda: self.buttonClick('no'))

            if self.folder.contents.other_count >= 1:
                # Pack buttons
                buttonNo.pack(padx=10, pady=4, side='bottom')
                buttonYes.pack(padx=10, pady=4, side='left', anchor='nw')
                buttonYesToAll.pack(padx=10, pady=4, side='left', anchor='ne')

            for i in range(self.folder.contents.other_count):
                # reset click and wait var
                self.buttonClicked.set(False)
                self.click = None

                # update UI
                self.folderLabelVar.set(f'\'{self.getFileName(self.folder.contents.others[i].path.decode("utf-8"))}\' is not an image, do you want to sort it anyway ?')
                checkFrame.pack(padx=10, side='right', anchor='se') # need to make layout arrangements

                # wait for user input
                self.wait_variable(self.buttonClicked)

                # sort based of user input
                if self.click == 'yes_to_all':
                    break
                elif self.click == 'no':
                    self.othersBlackList.append(i)
                else:
                    continue

        checkFrame.pack_forget()
        # print(folder.contents.images[0].path.decode('utf-8'))
        # print(folder.contents.images[0].date.decode('utf-8'))
        # print(self.sortingType)
        # print(self.namingType)
        # update folder label
        # loop over all the images & others
        # check if an appropriate folder based on the sorting type and the file date has been created, if not create it
        threading.Thread(target=self.moveFolderIdle).start()
    
    def getCopyNumber(self, fileName):
        num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        checkLen = len(fileName) -1
        for i in range(1, len(fileName)):
            if fileName[checkLen - i] not in num:
                print('checking: ', fileName[checkLen - i])
                return i - 1
        return 0

    def getCopyCount(self, fileName):
        return int(fileName[len(fileName)-self.getCopyNumber(fileName)-1:].replace(')', ''))

    def isCopied(self, fileName):
        index = fileName.find('(copy ')
        if index == -1 or fileName[-1] != ')':
            print("'", fileName, "'", ' IS NOT COPIED 1')
            return False

        checkIndex = len(fileName)-2

        for i in range(len(fileName)-2):
            if fileName[checkIndex-i].isdigit() == True:
                continue
            if checkIndex-i != index + 5:
                print("'", fileName, "'", ' IS NOT COPIED 2')
                return False
            else:
                print("'", fileName, "'", ' IS COPIED 3')
                return True
        print("'", fileName, "'", ' IS NOT COPIED 4')
        return False

    def checkCopy(self, path):
        if FileUtils.directoryExists(bytes(path, 'utf-8')):
            extension = self.getExtension(path)
            fileName = path.split('\\')[-1].split('.')[0]
            # path[:len(path)-len(extension)] + f'(copy {self.getCopyCount(fileName)+1})' + extension
            if self.isCopied(fileName):
                return self.checkCopy(path[:len(path)-self.getCopyNumber(fileName)-11] + f'(copy {self.getCopyCount(fileName)+1})' + extension)
            else:
                return self.checkCopy(path[:len(path)-len(extension)] + ' (copy 1)' + extension)
        else:
            return path


    def getDestinationPath(self, path, date, parentPath, sortingType, namingType):
        if sortingType != '':
            destinationPath = parentPath + '\\sorted\\'
        else:
            destinationPath = parentPath + '\\'
        sortingTypeSplit = sortingType.split('/')
        dateSplit = date.split('-')
        for i in range(len(sortingTypeSplit)):
            currentSortingType = self.formatType(sortingTypeSplit[i], True).split('-')
            for y in range(len(currentSortingType)):
                if currentSortingType[y] == 'yyyy':
                    destinationPath += dateSplit[0] + ' '
                elif currentSortingType[y] == 'mm':
                    destinationPath += dateSplit[1] + ' '
                elif currentSortingType[y] == 'dd':
                    destinationPath += dateSplit[2] + ' '
                if y == len(currentSortingType)-1:
                    destinationPath = destinationPath[:-1] + '\\'
        if namingType:
            namingTypeSplit = namingType.split('-')
            for i in range(len(namingTypeSplit)):
                if namingTypeSplit[i] == 'yyyy':
                    destinationPath += dateSplit[0] + '-'
                elif namingTypeSplit[i] == 'mm':
                    destinationPath += dateSplit[1] + '-'
                elif namingTypeSplit[i] == 'dd':
                    destinationPath += dateSplit[2] + '-'
                elif namingTypeSplit[i] == 'hh':
                    destinationPath += dateSplit[3] + '-'
                elif namingTypeSplit[i] == 'MM':
                    destinationPath += dateSplit[4] + '-'
                elif namingTypeSplit[i] == 'ss':
                    destinationPath += dateSplit[5] + '-'
                if i == len(namingTypeSplit)-1:
                    destinationPath = destinationPath[:-1] + self.getExtension(path)
        else:
            destinationPath += path.split('\\')[-1]
        
        finalDestinationPath = self.checkCopy(destinationPath) # final destination XD
        print(destinationPath)
        print(finalDestinationPath)

        return finalDestinationPath

    def buttonClick(self, click):
        self.click = click
        self.buttonClicked.set(True)

    def confirmPress(self):
        self.confirmFrame.pack_forget()
        self.confirmPressed.set(True)

    def getExtension(self, path):
        return os.path.splitext(path)[1]

    def onClose(self):
        if self.folder:
            FileUtils.freeFolder(self.folder)
            print('folder freed')
        print('closing')
        self.destroy()
        os._exit(0)

    def getFileName(self, path):
        try:
            return os.path.basename(path)
        except:
            return None

    def formatType(self, typee, isNaming=False):
        if isNaming:
            split = typee.replace(' ', '')
            cumter = 0
            result = split
            for i in range(len(split)-1):
                if split[i] == '-':
                    continue
                if split[i] != split[i+1]:
                    result = result[:i+1+cumter] + '-' + result[i+1+cumter:]
                    cumter += 1
            return result
        else:
            return typee.replace(' ', '')

    def setButton(self, buttonState, event=None):
        print(buttonState)
        if buttonState == '111':
            self.startButton.configure(state=CTk.NORMAL, fg_color='#3B8ED0')
            return
        if len(self.currentNamingType.get()) != 0 and buttonState == '101' and len(self.currentSortingType.get()) == 0:
            self.startButton.configure(state=CTk.NORMAL, fg_color='#3B8ED0')
            return
        self.startButton.configure(state=CTk.DISABLED, fg_color='gray')

        # if buttonState != '111':
        #     self.startButton.configure(state=CTk.DISABLED, fg_color='gray')
        #     return
        # self.startButton.configure(state=CTk.NORMAL, fg_color='#3B8ED0')

    def updateButtonState(self, buttonState, switchIndex):
        split = list(buttonState)
        split[switchIndex[0]] = str(switchIndex[1])
        print('changing ', buttonState, ' to ', ''.join(split))
        result = ''.join(split)
        self.buttonState = result
        return result

    def updatePathEntryColor(self, *args):

        # path is empty
        if len(self.currentPathEntry.get()) == 0:
            self.pathEntry.configure(border_color='#979DA2')

            self.setButton(self.updateButtonState(self.buttonState, [0, 0]))
            return
        
        # directory exists
        if FileUtils.directoryExists(bytes(self.currentPathEntry.get(), 'utf-8')):
            self.pathEntry.configure(border_color='#AAD1A7')
            self.setButton(self.updateButtonState(self.buttonState, [0, 1]))

        # directory doesn't exist
        else:
            self.pathEntry.configure(border_color='#E02F1F')
            self.setButton(self.updateButtonState(self.buttonState, [0, 0]))

    def changeBorderColor(self, color, removeColorChange=False):
        if removeColorChange == False:
            self.sortingTypeEntry.configure(border_color=color)

    def isValidSortingType(self, currentSorting, removeColorChange=False):

        # currentSorting not even or empty
        if len(currentSorting) % 2 != 0 or len(currentSorting) == 0:
            #self.sortingTypeEntry.configure(border_color='#E02F1F')
            self.changeBorderColor('#E02F1F', removeColorChange)
            return False
        
        twoDigits = ['m', 'd']
        i = 0
        while i < len(currentSorting) - 1:

            # 'm' or 'd' bad sequence
            if currentSorting[i] in twoDigits and currentSorting[i] != currentSorting[i+1]:
                #self.sortingTypeEntry.configure(border_color='#E02F1F')
                self.changeBorderColor('#E02F1F', removeColorChange)
                return False
            
            # not enough space for 4 'y'
            if currentSorting[i] == 'y' and len(currentSorting) - i < 4:
                #self.sortingTypeEntry.configure(border_color='#E02F1F')
                self.changeBorderColor('#E02F1F', removeColorChange)
                return False
            elif currentSorting[i] == 'y':
                for y in range(i, i+4):

                    # 'y' sequence is smaller than 4
                    if currentSorting[y] != 'y':
                        #self.sortingTypeEntry.configure(border_color='#E02F1F')
                        self.changeBorderColor('#E02F1F', removeColorChange)
                        return False
                i += 2
            i+= 2

        # good sorting formatting
        #self.sortingTypeEntry.configure(border_color='#AAD1A7')
        self.changeBorderColor('#AAD1A7', removeColorChange)
        return True

    def checkSortingType(self, currentSortingType, *args):
        validChars = ['y', 'm', 'd', '/', ' ']
        sortingTypes = []
        sortingType = ''

        # is empty
        if len(currentSortingType) == 0:
            self.sortingTypeEntry.configure(border_color='#979DA2')
            self.setButton(self.updateButtonState(self.buttonState, [1, 0]))
            self.sortingType = []
            return

        for i in range(len(currentSortingType)): 

            # invalid chars
            if currentSortingType[i] not in validChars:
                self.sortingTypeEntry.configure(border_color='#E02F1F')
                self.setButton(self.updateButtonState(self.buttonState, [1, 0]))
                self.sortingType = []
                return
            
            # adding up sortingType
            if currentSortingType[i] != '/':
                sortingType += currentSortingType[i]

            # new directory & valid sortingType
            if self.isValidSortingType(sortingType.replace(' ', '')):
                self.setButton(self.updateButtonState(self.buttonState, [1, 0]))
            elif currentSortingType[i] == '/' and self.isValidSortingType(sortingType.replace(' ', '')):
                self.sortingTypeEntry.configure(border_color='#AAD1A7')
                self.setButton(self.updateButtonState(self.buttonState, [1, 1]))
                sortingTypes.append(sortingType.replace(' ', ''))
                sortingType = ''
            # end of sortingType, pushing the valid sortingType
            if i == len(currentSortingType) - 1 and self.isValidSortingType(sortingType.replace(' ', '')):
                self.sortingTypeEntry.configure(border_color='#AAD1A7')
                self.setButton(self.updateButtonState(self.buttonState, [1, 1]))
                sortingTypes.append(sortingType.replace(' ', ''))

        # return sortingTypes
        self.sortingType = sortingTypes
        return
    
    def checkNamingType(self, currentNamingType, *args):
        validChars = ['y', 'm', 'd', 'h', 'M', 's', ' ']

        # check for invalid chars
        for i in range(len(currentNamingType)):
            if currentNamingType[i] not in validChars:
                self.namingTypeEntry.configure(border_color='#E02F1F')
                self.setButton(self.updateButtonState(self.buttonState, [2, 0]))
                return
            
        # is empty
        if len(currentNamingType) == 0:
            self.namingTypeEntry.configure(border_color='#979DA2')
            self.setButton(self.updateButtonState(self.buttonState, [2, 1]))
            self.namingType = ''
            return
        
        # is invalid
        if self.isValidSortingType(currentNamingType, True) == False:
            self.namingTypeEntry.configure(border_color='#E02F1F')
            self.setButton(self.updateButtonState(self.buttonState, [2, 0]))
            self.namingType = ''
            return
        
        # is valid
        else:
            self.namingTypeEntry.configure(border_color='#AAD1A7')
            self.setButton(self.updateButtonState(self.buttonState, [2, 1]))
            self.namingType = currentNamingType


app = App()
app.mainloop()
