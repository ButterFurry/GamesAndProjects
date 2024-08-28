import serial
import time

class ArduinoController:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Give time for Arduino to reset

    def send_command(self, command):
        self.ser.write((command + '\n').encode())
        time.sleep(0.1)
        response = self.ser.read_all().decode().strip()
        return response

    def define_command(self, command_name, command_actions):
        command = f"def {command_name}:{command_actions};"
        return self.send_command(command)

    def execute_command(self, command_name):
        command = f"exec {command_name}"
        return self.send_command(command)

    def list_commands(self):
        return self.send_command("list")

    def clear_data(self):
        return self.send_command("clear")

    def erase_custom_commands(self):
        return self.send_command("erase")

    def surf_eeprom(self, address, mode, value=None):
        if mode == "R":
            command = f"surf {address},R"
        elif mode == "W" and value is not None:
            command = f"surf {address},W,{value}"
        else:
            return "Invalid surf command."
        return self.send_command(command)

    def close(self):
        self.ser.close()

if __name__ == "__main__":
    port = input("Enter the Arduino COM port (e.g., COM3): ")
    arduino = ArduinoController(port)

    try:
        while True:
            print("\nAvailable commands:")
            print("1. Define command")
            print("2. Execute command")
            print("3. List commands")
            print("4. Clear data")
            print("5. Erase custom commands")
            print("6. Surf EEPROM")
            print("7. Exit")

            choice = input("Select an option: ")

            if choice == "1":
                command_name = input("Enter the command name: ")
                command_actions = input("Enter the command actions (e.g., 'K A;M 10,20;'): ")
                print(arduino.define_command(command_name, command_actions))
            elif choice == "2":
                command_name = input("Enter the command name to execute: ")
                print(arduino.execute_command(command_name))
            elif choice == "3":
                print(arduino.list_commands())
            elif choice == "4":
                print(arduino.clear_data())
            elif choice == "5":
                print(arduino.erase_custom_commands())
            elif choice == "6":
                address = input("Enter the EEPROM address: ")
                mode = input("Enter mode (R for Read, W for Write): ")
                if mode == "W":
                    value = input("Enter value to write: ")
                    print(arduino.surf_eeprom(address, mode, value))
                else:
                    print(arduino.surf_eeprom(address, mode))
            elif choice == "7":
                break
            else:
                print("Invalid option. Please try again.")

    finally:
        arduino.close()
