from gpiozero import Button, LED
from statemachine import StateMachine, State
from time import sleep
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
from threading import Thread
DEBUG = True

class ManagedDisplay():
    def __init__(self):
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)
        self.lcd_columns = 16
        self.lcd_rows = 2 
        self.lcd = characterlcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en, 
                    self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7, 
                    self.lcd_columns, self.lcd_rows)

        
        self.lcd.clear()

    def cleanupDisplay(self):
        
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()
        
    def clear(self):
        self.lcd.clear()

    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.message = message

class CWMachine(StateMachine):
    "A state machine designed to display morse code messages"

    redLight = LED(18)
    blueLight = LED(23)
    message1 = 'SOS'
    message2 = 'OK'

    activeMessage = message1
    endTransmission = False
    off = State(initial = True)
    dot = State()
    dash = State()
    dotDashPause = State()
    letterPause = State()
    wordPause = State()

    screen = ManagedDisplay()
    morseDict = {
        "A" : ".-", "B" : "-...", "C" : "-.-.", "D" : "-..",
        "E" : ".", "F" : "..-.", "G" : "--.", "H" : "....",
        "I" : "..", "J" : ".---", "K" : "-.-", "L" : ".-..",
        "M" : "--", "N" : "-.", "O" : "---", "P" : ".--.",
        "Q" : "--.-", "R" : ".-.", "S" : "...", "T" : "-",
        "U" : "..-", "V" : "...-", "W" : ".--", "X" : "-..-",
        "Y" : "-.--", "Z" : "--..", "0" : "-----", "1" : ".----",
        "2" : "..---", "3" : "...--", "4" : "....-", "5" : ".....",
        "6" : "-....", "7" : "--...", "8" : "---..", "9" : "----.",
        "+" : ".-.-.", "-" : "-....-", "/" : "-..-.", "=" : "-...-",
        ":" : "---...", "." : ".-.-.-", "$" : "...-..-", "?" : "..--..",
        "@" : ".--.-.", "&" : ".-...", "\"" : ".-..-.", "_" : "..--.-",
        "|" : "--...-", "(" : "-.--.-", ")" : "-.--.-"
    }

    ##
    ## doDot - Event that moves between the off-state (all-lights-off)
    ## and a 'dot'
    ##
    doDot = (
        off.to(dot) | dot.to(off)
    )

    ##
    ## doDash - Event that moves between the off-state (all-lights-off)
    ## and a 'dash'
    ##
    doDash = (
        off.to(dash) | dash.to(off)
    )

    ##
    ## doDDP - Event that moves between the off-state (all-lights-off)
    ## and a pause between dots and dashes
    ##
    doDDP = (
        off.to(dotDashPause) | dotDashPause.to(off)
    )

    ##
    ## doLP - Event that moves between the off-state (all-lights-off)
    ## and a pause between letters
    ##
    doLP = (
        off.to(letterPause) | letterPause.to(off)
    )

    ##
    ## doWP - Event that moves between the off-state (all-lights-off)
    ## and a pause between words
    ##
    doWP = (
        off.to(wordPause) | wordPause.to(off)
    )

    ##
    ## on_enter_dot - Action performed when the state machine transitions
    ## into the dot state
    ##
    def transition_twice(self, event):
        event()  # This call transitions from off into the pause state.
        event()  # This call transitions from the pause state back to off.

    def on_enter_dot(self):
        
        self.redLight.on(); sleep(0.5)

        if(DEBUG):
            print("* Changing state to red - dot")

    ##
    ## on_exit_dot - Action performed when the statemachine transitions
    ## out of the red state.
    ##
    def on_exit_dot(self):
        #
        self.redLight.off()
    ##
    ## on_enter_dash - Action performed when the state machine transitions
    ## into the dash state
    ##
    def on_enter_dash(self):
        #
        self.blueLight.on(); sleep(1.5)

        if(DEBUG):
            print("* Changing state to blue - dash")

    ##
    ## on_exit_dash - Action performed when the statemachine transitions
    ## out of the dash state.
    ##
    def on_exit_dash(self):
        #
        self.blueLight.off()
    ##
    ## on_enter_dotDashPause - Action performed when the state machine 
    ## transitions into the dotDashPause state
    ##
    def on_enter_dotDashPause(self):
        #
        sleep(0.25)
        
        if(DEBUG):
            print("* Pausing Between Dots/Dashes - 250ms")

    ##
    ## on_exit_dotDashPause - Action performed when the statemachine transitions
    ## out of the dotDashPause state.
    ##
    def on_exit_dotDashPause(self):
        pass
	
    ##
   
    def on_enter_letterPause(self):
        #
        sleep(0.75)

        if(DEBUG):
            print("* Pausing Between Letters - 750ms")

    ##
    ## on_exit_letterPause - Action performed when the statemachine transitions
    ## out of the letterPause state.
    ##
    def on_exit_letterPause(self):
        pass

    ##
    ## on_enter_wordPause - Action performed when the state machine 
    ## transitions into the wordPause state
    ##
    def on_enter_wordPause(self):
        sleep(3.0)

        
        if(DEBUG):
            print("* Pausing Between Words - 3000ms")

    ##
    ## on_exit_wordPause - Action performed when the statemachine transitions
    ## out of the wordPause state.
    ##
    def on_exit_wordPause(self):
        pass

    ##
    ## toggleMessage - method used to switch between message1
    ## and message2
    ##
    def toggleMessage(self):

        #
        if self.activeMessage == self.message1:
            self.activeMessage = self.message2
        else:
            self.activeMessage = self.message1

        if(DEBUG):
            print(f"* Toggling active message to: {self.activeMessage} ")

    ##
    ## processButton - Utility method used to send events to the 
    ## state machine. The only thing this event does is trigger
    ## a change in the outgoing message
    ##
    def processButton(self):
        print('*** processButton')
        self.toggleMessage()

    ##
    ## run - kickoff the transmit functionality in a separate execution thread
    ##
    def run(self):
        myThread = Thread(target=self.transmit)
        myThread.start()
        
    ##
    ## transmit - utility method used to continuously send a
    ## message
    ##
    def transmit(self):

        ##
        ## Loop until we are shutdown
        ##
        while not self.endTransmission:

            ## Display the active message in our 16x2 screen
            self.screen.updateScreen(f"Sending:\n{self.activeMessage}")

            ## Parse message for individual wordsTAM
            wordList = self.activeMessage.split()

            ## Setup counter to determine time buffer after words
            lenWords = len(wordList)
            wordsCounter = 1
            for word in wordList:
            
                ## Setup counter to determine time buffer after letters
                lenWord = len(word)
                wordCounter = 1
                for char in word:

                    ## Convert the character to its string in morse code
                    morse = self.morseDict.get(char)

                    ## Setup counter to determine time buffer after letters
                    lenMorse = len(morse)
                    morseCounter = 1
                    for x in morse:

                        ## Dot or dash?
                        if x == '.':
                            self.doDot()
                            self.doDot()
                        elif x == '-':
                            self.doDash()
                            self.doDash()
                       
                        ## .
                        
                        if morseCounter < lenMorse:
                            self.transition_twice(self.doDDP)
                            
                        morseCounter += 1

                        ## 
                        if wordCounter < lenWord:
                            self.transition_twice(self.doLP)
                            
                        wordCounter += 1

                        if wordsCounter < lenWords:
                            self.transition_twice(self.doWP)
                            
                        wordsCounter += 1

                #
        self.screen.cleanupDisplay()
    ## End class CWMachine definition
##
cwMachine = CWMachine()
cwMachine.run()


greenButton = Button(24)
greenButton.when_pressed = cwMachine.processButton

## TODO: Add the code necessary code to assign the
## appropriate function to the greenButton variable 
## so that when it is pressed, the message being sent
## changes to the alternate message - no matter which
## message is currently being send.
## Remove this TODO comment block when complete. 
## You should be able to accomplish this in a single
## line of code.

##
## Setup loop variable
##
repeat = True

##
## Repeat until the user creates a keyboard interrupt (CTRL-C)
##
while repeat:
    try:
        ## Only display if the DEBUG flag is set
        if(DEBUG):
            print("Killing time in a loop...")

        ## sleep for 20 seconds at a time. This value is not crucial, 
        ## all of the work for this application is handled by the 
        ## Button.when_pressed event process
        sleep(20)
    except KeyboardInterrupt:
        ## Catch the keyboard interrupt (CTRL-C) and exit cleanly
        ## we do not need to manually clean up the GPIO pins, the 
        ## gpiozero library handles that process.
        print("Cleaning up. Exiting...")

        ## Stop the loop
        repeat = False
        
        ## Cleanly exit the state machine after completing the last message
        cwMachine.endTransmission = True
        sleep(1)
