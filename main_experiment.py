from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from random import randint
from os import listdir

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
app = QApplication([])
window = uic.loadUi('experiment.ui')

######################################################################
# All functions here
# 1.Function for next page
def nextPage():
    pageIndex = window.StackedWidget.currentIndex()  # get current page index
    if pageIndex == 0:                               # page 1 (consent)
        if window.checkConsent.isChecked():          # go to next page when the box is checked
            window.StackedWidget.setCurrentIndex(pageIndex + 1)
        else:
            window.lblError1.show()

    elif pageIndex == 1:                             # page 2 (demographic)
        age = int(window.spinBoxAge.value())
        gender = window.dropGender.currentText()
        edu = window.dropEdu.currentText()
        # go to the next page when 3 requirements are met
        if age >= 18 and gender != '' and edu != '':
            window.StackedWidget.setCurrentIndex(pageIndex + 1)
            # Append demographic information into the csv
            partList.append(str(age))
            partList.append(gender)
            partList.append(edu)
        # if any requirement is not met
        else:
            # age
            if age == 0:
                window.lblError2_1.show()  # if not changed show the error message
            elif age < 18:
                window.lblError2_1.setText('You must be 18+ to participate in this experiment')
                window.lblError2_1.show()  # if under 18 show the message
            else:
                window.lblError2_1.hide()
            # gender
            if gender == '':
                window.lblError2_2.show()  # if is blank show the error message
            else:
                window.lblError2_2.hide()
            # education
            if edu == '':
                window.lblError2_3.show()  # if is blank show the error message
            else:
                window.lblError2_3.hide()

    elif pageIndex == 3:                   # page 4 (experimental trial)
        if partList[-1] == 'blue':         # if participant drew a blue marble, go to mext lottery page
            window.StackedWidget.setCurrentIndex(pageIndex + 1)
            colourTimer.start(400)
        else:                              # if participant drew a red marble, go to the debrief page directly
            window.StackedWidget.setCurrentIndex(pageIndex + 2)
            partList.append('no')          # append whether win/draw a lottery
            # join the list into on string separated by commas
            row = ','.join(partList)
            resultHandle.write(row + "\n")
            resultHandle.close()

    elif pageIndex == 4:                   # page 5 (lottery)
        window.StackedWidget.setCurrentIndex(pageIndex + 1)
        # join the list into on string separated by commas
        row = ','.join(partList)
        resultHandle.write(row + "\n")
        resultHandle.close()


# 2.Function for trial page
def trial():
    window.StackedWidget.setCurrentIndex(window.StackedWidget.currentIndex() + 1)
    # Append condition and urn position to the csv
    partList.append(str(2 * conditionHalf))
    partList.append(str(AorB))
    # Set instruction text based on conditions
    if conditionHalf == 1:  # The 2-marble condition is slightly different
        middleText = 'setting the numbers 0, 1, 2 in the programme'
    else:
        middleText = f'setting the numbers 0, 1, 2, . . ., {2 * conditionHalf} in the programme'
    window.textChange.setText(f'Urn {urn[AorB]} contains {conditionHalf} red marbles and '
                              f'{conditionHalf} blue marbles. '
                              f'Urn {urn[1 - AorB]} contains {2 * conditionHalf} marbles '
                              f'in an unknown color ratio, '
                              f'from {2 * conditionHalf} red marbles and 0 blue marbles to '
                              f'0 red marbles and {2 * conditionHalf} blue marbles. '
                              f'The mixture of red and blue marbles in Urn {urn[1 - AorB]} has been decided by ' +
                              middleText + ', shuffling the numbers thoroughly, '
                              'and then drawing one of them at random. The number chosen was used to determine '
                              f'the number of blue marbles to be put into Urn {urn[1 - AorB]}, '
                              'but you do not know the number. Every possible mixture of '
                              f'red and blue marbles in Urn {urn[1 - AorB]} is equally likely.')
    # Set random positions for 2 urns
    geom = window.pushUrnEqual.geometry()       # get the default geometry
    # The default position is: random urn on the right, equal urn on the left. So I only code the other position
    # The other position: random urn on the left, equal possible urn on the right
    if AorB == 1:
        # Swap x-axis, others remain the same
        window.pushUrnEqual.setGeometry(geom.x() + 510, geom.y(), geom.width(), geom.height())
        window.pushUrnRandom.setGeometry(geom.x(), geom.y(), geom.width(), geom.height())


# 3.Function for clicking the equal urn
def drawEqualUrn():
    # This function will be called when the equal probability urn is clicked. When the function is called,
    # it will get the x-axis position of the equal urn (because it's randomised). We want to know this because
    # we want to set the x-axis of marble corresponding to the urn. Then the animation function will be called
    partList.append('equal')                     # append the chosen urn to the csv
    geomX = window.pushUrnEqual.geometry().x()   # get the x-axis of equal urn
    # Because it's 50:50 chance, whether it's red or blue marble depends on the 'equalRorB' randomiser
    if equalRorB == 0:  # 0 is red
        window.textRed.show()
        partList.append('red')
        window.lblRedBall.setGeometry(geomX + 30, 410, 71, 71)  # set red marble to the equal urn position
    else:  # 1 is blue
        window.textBlue.show()
        partList.append('blue')
        window.lblBlueBall.setGeometry(geomX + 30, 410, 71, 71)  # set blue marble to the equal urn position
    marbleTimer.start(30)
    window.pushNext4.show()                      # show the next button after the choice being made


# 4.Function for clicking the random urn
def drawRandomUrn():
    # This function will be called when the random urn is clicked. The logic of setting the marble position and
    # animation is the same as drawEqualUrn. But the rule of getting red or blue marbles is different.
    partList.append('random')                    # append the chosen urn to the csv
    geomX = window.pushUrnRandom.geometry().x()  # get the x-axis position of the ambiguous urn
    nblue = randint(0, conditionHalf * 2)        # this means how many blue marbles in the urn
    ndraw = randint(1, conditionHalf * 2)        # assume each marble has a number from 1-100, this is the draw number
    if nblue < ndraw:
        # Consider this as: if the draw number is outside the range of blue marbles, it'll be a red one
        window.textRed.show()
        partList.append('red')
        window.lblRedBall.setGeometry(geomX + 30, 410, 71, 71)
    else:                                        # this is nblue >= ndraw
        # Consider this as: if the draw number is inside the range of blue marbles, it'll be a blue one
        window.textBlue.show()
        partList.append('blue')
        window.lblBlueBall.setGeometry(geomX + 30, 410, 71, 71)
    marbleTimer.start(30)
    window.pushNext4.show()


# 5.Function for marble animation
def animation():
    if partList[-1] == 'red':
        geom = window.lblRedBall.geometry()      # get the current position
        marble = window.lblRedBall               # set the marble that will move
    else:
        geom = window.lblBlueBall.geometry()
        marble = window.lblBlueBall
    if geom.y() > 350:                           # set the limitation
        marble.setGeometry(geom.x(), geom.y() - 5, geom.width(), geom.height())


# 6.Function for colour changing label
def blink():
    pal = window.lblLotteryTitle.palette()
    pal.setColor(QPalette.WindowText, QColor(window.colour[window.counter]))
    window.lblLotteryTitle.setPalette(pal)
    # Swap the colours by changing the counter
    if window.counter == 0:
        window.counter = 1
    else:
        window.counter = 0


# 7.Function for lottery
def lottery():
    # assume there are 100 numbers
    number = randint(1, 100)            # randomly draw a number from 1-100
    if number <= 5:                     # the first 5 numbers will win the prize
        window.lblLottery.setText('OMG!! You won £30!!')
        window.lblLottery.show()
        partList.append('yes')          # append the result to the csv so that we can know who won £30
    else:
        window.lblLottery.show()
        partList.append('no')
    window.pushNext5.show()             # push button appears after draw


###################################################################################
# Main programme here
partList = []                            # create a list for data for each participant
urn = ['A', 'B']                         # 2 urns. Counterbalance for urns positions A & B
AorB = randint(0, 1)                     # used as indexes of list 'urn' (i.e., urn[AorB]). So 0 is A, 1 is B
equalRorB = randint(0, 1)                # random red or blue marble in 50:50 urn. 0 is red, 1 is blue
marbleTimer = QTimer()                   # set a timer for marble animation
marbleTimer.timeout.connect(animation)   # start marble animation when time out
window.colour = ['red', 'blue']          # for lottery colour
window.counter = 0                       # for lottery colour
colourTimer = QTimer()                   # set a timer for title colour changing
colourTimer.timeout.connect(blink)       # lottery title colour changing
folder = listdir()                       # Access the fold to either create a new scv or read the csv

if 'results.csv' not in folder:          # if there is no result csv, create one and write column names
    resultHandle = open("results.csv", "w")
    resultHandle.write('age,gender,education,condition,urnPosition,urnSelect,marble,lottery' + '\n')
    resultHandle.close()
    conditionHalf = 1                    # set the first condition: 2-marble condition
else:                                    # if there is a result csv, read it to get the last condition
    results = open('results.csv', 'r').readlines()
    lastPart = results[-1].split(",")    # [-1] gives the last participant. Use comma to split the columns
    lastCondition = lastPart[3]          # thr fourth string is last condition
    # Set the current condition based on the last condition
    if lastCondition == '2':
        conditionHalf = 5
    elif lastCondition == '10':
        conditionHalf = 50
    elif lastCondition == '100':         # we can add more conditions after this
        conditionHalf = 1

resultHandle = open("results.csv", "a")  # use append mode to add each participant

window.StackedWidget.setCurrentIndex(0)  # always start from the first page
# Hide things that should not be presented in the first place
window.lblError1.hide()
window.lblError2_1.hide()
window.lblError2_2.hide()
window.lblError2_3.hide()
window.textBlue.hide()
window.textRed.hide()
window.pushNext4.hide()
window.pushNext5.hide()
window.lblLottery.hide()
# Next buttons click & connect
window.pushNext1.clicked.connect(nextPage)
window.pushNext2.clicked.connect(nextPage)
window.pushNext3.clicked.connect(trial)
window.pushNext4.clicked.connect(nextPage)
window.pushNext5.clicked.connect(nextPage)
# Urns click & connect
window.pushUrnEqual.clicked.connect(drawEqualUrn)
window.pushUrnRandom.clicked.connect(drawRandomUrn)
# Lottery click & connect
window.pushLottery.clicked.connect(lottery)
###################################################################

window.show()
app.exec_()
