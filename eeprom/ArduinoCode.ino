#include <EEPROM.h>
#include <Keyboard.h>
#include <Mouse.h>

const int maxDataLength = 512;
const int customCommandStart = maxDataLength / 2; // Start custom commands in the second half of EEPROM
const int ledPin = 13;

// Error patterns
const int EEPROM_FULL_PATTERN[] = {100, 300, 100, 300, 100, 300};
const int NO_DATA_STORED_PATTERN[] = {100, 100, 300, 300};
const int INVALID_FORMAT_PATTERN[] = {100, 300, 300, 100};
const int INDEX_OUT_OF_RANGE_PATTERN[] = {100, 100, 100, 300, 100, 100, 100, 300};
const int COMMAND_NOT_FOUND_PATTERN[] = {300, 100, 300};
const int UNKNOWN_ERROR_PATTERN[] = {100, 100, 100};

// Error codes
enum ErrorCode {
    EEPROM_FULL,
    NO_DATA_STORED,
    INVALID_FORMAT,
    INDEX_OUT_OF_RANGE,
    COMMAND_NOT_FOUND
};

// LED Flashing Class
class LEDFlasher {
public:
    LEDFlasher(int pin) : ledPin(pin) {
        pinMode(ledPin, OUTPUT);
    }

    void flashPattern(const int pattern[], int length) {
        for (int i = 0; i < length; i++) {
            digitalWrite(ledPin, HIGH);
            delay(pattern[i]);
            digitalWrite(ledPin, LOW);
            delay(100);
        }
    }

    void flashError(ErrorCode errorCode) {
        switch (errorCode) {
            case EEPROM_FULL:
                flashPattern(EEPROM_FULL_PATTERN, sizeof(EEPROM_FULL_PATTERN) / sizeof(EEPROM_FULL_PATTERN[0]));
                break;
            case NO_DATA_STORED:
                flashPattern(NO_DATA_STORED_PATTERN, sizeof(NO_DATA_STORED_PATTERN) / sizeof(NO_DATA_STORED_PATTERN[0]));
                break;
            case INVALID_FORMAT:
                flashPattern(INVALID_FORMAT_PATTERN, sizeof(INVALID_FORMAT_PATTERN) / sizeof(INVALID_FORMAT_PATTERN[0]));
                break;
            case INDEX_OUT_OF_RANGE:
                flashPattern(INDEX_OUT_OF_RANGE_PATTERN, sizeof(INDEX_OUT_OF_RANGE_PATTERN) / sizeof(INDEX_OUT_OF_RANGE_PATTERN[0]));
                break;
            case COMMAND_NOT_FOUND:
                flashPattern(COMMAND_NOT_FOUND_PATTERN, sizeof(COMMAND_NOT_FOUND_PATTERN) / sizeof(COMMAND_NOT_FOUND_PATTERN[0]));
                break;
            default:
                flashPattern(UNKNOWN_ERROR_PATTERN, sizeof(UNKNOWN_ERROR_PATTERN) / sizeof(UNKNOWN_ERROR_PATTERN[0]));
                break;
        }
    }

private:
    int ledPin;
};

// EEPROM Manager Class
class EEPROMManager {
public:
    EEPROMManager() : eepromAddress(0), customCommandAddress(customCommandStart) {}

    void clearData() {
        for (int i = 0; i < customCommandStart; i++) {
            EEPROM.write(i, 0);
        }
        eepromAddress = 0;
        Serial.println("Entries and macros cleared.");
    }

    void eraseCustomCommands() {
        for (int i = customCommandStart; i < maxDataLength; i++) {
            EEPROM.write(i, 0);
        }
        customCommandAddress = customCommandStart;
        Serial.println("Custom commands erased.");
    }

    void defineCommand(String commandDefinition, LEDFlasher &flasher) {
        int colonIndex = commandDefinition.indexOf(':');
        if (colonIndex == -1) {
            flasher.flashError(INVALID_FORMAT);
            return;
        }

        String commandName = commandDefinition.substring(0, colonIndex);
        String commandActions = commandDefinition.substring(colonIndex + 1);

        if (customCommandAddress + commandName.length() + commandActions.length() + 3 >= maxDataLength) {
            flasher.flashError(EEPROM_FULL);
            return;
        }

        // Store command
        for (int i = 0; i < commandName.length(); i++) {
            EEPROM.write(customCommandAddress++, commandName[i]);
        }
        EEPROM.write(customCommandAddress++, ':');
        for (int i = 0; i < commandActions.length(); i++) {
            EEPROM.write(customCommandAddress++, commandActions[i]);
        }
        EEPROM.write(customCommandAddress++, ';');

        Serial.println("Command defined: " + commandName);
    }

    void executeCommand(String commandName, LEDFlasher &flasher) {
        int currentAddress = customCommandStart;
        String storedCommand = "";
        while (currentAddress < customCommandAddress) {
            char c = EEPROM.read(currentAddress++);
            if (c == ':') {
                if (storedCommand == commandName) {
                    String commandActions = "";
                    char action;
                    while ((action = EEPROM.read(currentAddress++)) != ';') {
                        commandActions += action;
                    }
                    Serial.println("Executing command: " + commandName);
                    processCommandActions(commandActions);
                    return;
                } else {
                    while (EEPROM.read(currentAddress++) != ';') {}
                }
                storedCommand = "";
            } else {
                storedCommand += c;
            }
        }
        flasher.flashError(COMMAND_NOT_FOUND);
    }

    void listCommands() {
        Serial.println("Stored commands:");
        int currentAddress = customCommandStart;
        String commandName = "";
        while (currentAddress < customCommandAddress) {
            char c = EEPROM.read(currentAddress++);
            if (c == ':') {
                Serial.println(commandName);
                while (EEPROM.read(currentAddress++) != ';') {}
                commandName = "";
            } else {
                commandName += c;
            }
        }
    }

    void surfEEPROM(int address, bool isWrite, byte value = 0) {
        if (isWrite) {
            EEPROM.write(address, value);
            Serial.print("Wrote 0x");
            Serial.print(value, HEX);
            Serial.print(" to address ");
            Serial.println(address);
        } else {
            byte readValue = EEPROM.read(address);
            Serial.print("Address ");
            Serial.print(address);
            Serial.print(" contains 0x");
            Serial.println(readValue, HEX);
        }
    }

private:
    int eepromAddress;
    int customCommandAddress;

    void processCommandActions(String commandActions) {
        int pos = 0;
        while (pos < commandActions.length()) {
            if (commandActions[pos] == 'K') {
                pos += 2;
                Keyboard.press(commandActions[pos]);
                delay(100);
                Keyboard.release(commandActions[pos]);
            } else if (commandActions[pos] == 'M') {
                pos += 2;
                int commaPos = commandActions.indexOf(',', pos);
                int x = commandActions.substring(pos, commaPos).toInt();
                int y = commandActions.substring(commaPos + 1).toInt();
                Mouse.move(x, y);
            }
            pos = commandActions.indexOf(';', pos) + 1;
        }
    }
};

LEDFlasher ledFlasher(ledPin);
EEPROMManager eepromManager;

void setup() {
    Serial.begin(9600);
    Keyboard.begin();
    Mouse.begin();
    Serial.println("Enter a command: ");
}

void loop() {
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');
        input.trim();

        if (input.startsWith("def ")) {
            String commandDefinition = input.substring(4);
            eepromManager.defineCommand(commandDefinition, ledFlasher);
        } else if (input.startsWith("exec ")) {
            String commandName = input.substring(5);
            eepromManager.executeCommand(commandName, ledFlasher);
        } else if (input.equals("clear")) {
            eepromManager.clearData();
        } else if (input.equals("erase")) {
            eepromManager.eraseCustomCommands();
        } else if (input.equals("list")) {
            eepromManager.listCommands();
        } else if (input.startsWith("surf ")) {
            int spaceIndex = input.indexOf(' ');
            String params = input.substring(spaceIndex + 1);
            int commaIndex = params.indexOf(',');
            int address = params.substring(0, commaIndex).toInt();
            String mode = params.substring(commaIndex + 1, commaIndex + 2);
            if (mode == "R") {
                eepromManager.surfEEPROM(address, false);
            } else if (mode == "W") {
                int value = params.substring(commaIndex + 3).toInt();
                eepromManager.surfEEPROM(address, true, value);
            } else {
                Serial.println("Invalid surf command. Use: surf <address>,R or surf <address>,W,<value>");
            }
        } else {
            Serial.println("Unknown command.");
        }
    }
}
