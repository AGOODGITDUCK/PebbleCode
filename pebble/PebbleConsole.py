import sys
import os
import tkinter as tk

class PebbleConsole:
    def __init__(self):
        self.running = True
        self.variables = {}
        self.gui_elements = {}  # store GUI elements by ID
        self.in_gui_mode = False
        self.last_cd = os.getcwd()
        self.current_cd = os.getcwd()
        self.gui_window = None
        self.gui_canvas = None
        self.next_element_id = 1  # unique ID for GUI elements

    # -----------------------
    # Main loop
    # -----------------------
    def run(self):
        print("Pebble Console – type help for help type credits for credits")  # Startup message
        while self.running:
            try:
                prompt = "GUI:\\" if self.in_gui_mode else ">>>"
                cmd = input(prompt + " ").strip()
                if cmd == "":
                    continue
                self.handle_command(cmd)
                # Update GUI window if exists
                if self.gui_window:
                    self.gui_window.update()
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    # -----------------------
    # Command Dispatcher
    # -----------------------
    def handle_command(self, cmd):
        parts = cmd.split(maxsplit=1)
        action = parts[0]
        argument = parts[1] if len(parts) > 1 else None

        if self.in_gui_mode:
            if action == "leavegui":
                self.leave_gui_mode()
            else:
                self.run_gui_command(cmd)
            return

        if action == "exit":
            self.running = False
        elif action == "credits":
            print("Adam Nassar")
        elif action == "help":
            self.show_help()
        elif action == "cd":
            if argument:
                self.change_directory(argument)
            else:
                print("No task")
        elif action == "pebble":
            if argument:
                self.run_peg_file(argument)
            else:
                print("No task")
        elif action == "print":
            if argument:
                value = self.evaluate_expression(argument)
                print(value)
            else:
                print("No task")
        elif action == "gui":
            if argument == "mode":
                self.enter_gui_mode()
            elif argument:
                self.run_gui_command(argument)
            else:
                print("No task")
        else:
            print("Invalid command")

    # -----------------------
    # GUI Mode
    # -----------------------
    def enter_gui_mode(self):
        self.in_gui_mode = True
        self.last_cd = self.current_cd
        print("Entered GUI mode. Type 'leavegui' to return to console.")

        if not self.gui_window:
            self.gui_window = tk.Tk()
            self.gui_window.title("Pebble GUI")
            self.gui_canvas = tk.Canvas(self.gui_window, width=400, height=300, bg="white")
            self.gui_canvas.pack()

    def leave_gui_mode(self):
        self.in_gui_mode = False
        print("Leaving GUI mode but as python so dont cd pebble\help peb to test and also do not pebble help.peb.")
        self.change_directory(self.last_cd)
        if self.gui_window:
            self.gui_window.destroy()
            self.gui_window = None
            self.gui_canvas = None
            self.gui_elements.clear()

    # -----------------------
    # GUI Commands
    # -----------------------
    def run_gui_command(self, cmd):
        if not self.gui_canvas:
            print("No GUI initialized. Use 'gui mode' first.")
            return

        parts = cmd.split()
        if parts[0] == "canvas" and len(parts) == 3:
            width, height = int(parts[1]), int(parts[2])
            self.gui_canvas.config(width=width, height=height)
            print(f"Canvas resized to {width}x{height}")
        elif parts[0] == "color" and len(parts) == 2:
            self.gui_canvas.config(bg=parts[1])
            print(f"Canvas color set to {parts[1]}")
        elif parts[0] == "text":
            try:
                text_index = cmd.index('"')
                text_end = cmd.index('"', text_index+1)
                text_content = cmd[text_index+1:text_end]
                pos_index = cmd.index("pos")
                pos_parts = cmd[pos_index:].split()
                x = int(pos_parts[1].split(":")[1])
                z = int(pos_parts[2].split(":")[1])
                element_id = self.next_element_id
                self.next_element_id += 1
                self.gui_elements[element_id] = self.gui_canvas.create_text(x, z, text=text_content, anchor="nw")
                print(f"Text added with ID {element_id}")
            except Exception as e:
                print(f"Invalid GUI text command: {e}")
        elif parts[0] in ["oval", "rect", "line"]:
            try:
                args = {p.split(":")[0]: int(p.split(":")[1]) for p in parts[1:] if ":" in p}
                fill = [p.split(":")[1] for p in parts[1:] if "fill" in p or "color" in p]
                color = fill[0] if fill else "black"
                element_id = self.next_element_id
                self.next_element_id += 1
                if parts[0] == "oval":
                    self.gui_elements[element_id] = self.gui_canvas.create_oval(
                        args["x"], args["z"], args["x2"], args["z2"], fill=color
                    )
                elif parts[0] == "rect":
                    self.gui_elements[element_id] = self.gui_canvas.create_rectangle(
                        args["x"], args["z"], args["x2"], args["z2"], fill=color
                    )
                elif parts[0] == "line":
                    self.gui_elements[element_id] = self.gui_canvas.create_line(
                        args["x"], args["z"], args["x2"], args["z2"], fill=color
                    )
                print(f"{parts[0].capitalize()} added with ID {element_id}")
            except Exception as e:
                print(f"Invalid GUI {parts[0]} command: {e}")
        elif parts[0] == "move":
            try:
                element_id = int(parts[1].split(":")[1])
                x = int(parts[2].split(":")[1])
                z = int(parts[3].split(":")[1])
                self.gui_canvas.move(self.gui_elements[element_id], x, z)
                print(f"Moved element {element_id}")
            except Exception as e:
                print(f"Invalid GUI move command: {e}")
        elif parts[0] == "delete":
            try:
                element_id = int(parts[1].split(":")[1])
                self.gui_canvas.delete(self.gui_elements[element_id])
                del self.gui_elements[element_id]
                print(f"Deleted element {element_id}")
            except Exception as e:
                print(f"Invalid GUI delete command: {e}")
        elif parts[0] == "clear":
            self.gui_canvas.delete("all")
            self.gui_elements.clear()
            print("Canvas cleared")
        else:
            print("Invalid command")

    # -----------------------
    # Console Commands
    # -----------------------
    def change_directory(self, folder):
        try:
            os.chdir(folder)
            self.current_cd = os.getcwd()
            print(f"Current directory: {self.current_cd}")
        except FileNotFoundError:
            print(f"Error: Directory '{folder}' not found")
        except Exception as e:
            print(f"Error: {e}")

    def run_peg_file(self, filename):
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found")
            return
        try:
            with open(filename, "r") as f:
                code = f.read()
            # auto-enter GUI mode if PEG contains GUI commands
            if any(line.strip().startswith("gui") for line in code.splitlines()):
                self.enter_gui_mode()
            self.run_peg_code(code)
        except Exception as e:
            print(f"Error running file '{filename}': {e}")

    def run_peg_code(self, code):
        for line in code.splitlines():
            line = line.strip()
            if line == "":
                continue
            try:
                if line.startswith("print "):
                    expr = line[6:].strip()
                    value = self.evaluate_expression(expr)
                    print(value)
                elif "=" in line:
                    var, expr = line.split("=", maxsplit=1)
                    self.variables[var.strip()] = self.evaluate_expression(expr.strip())
                else:
                    self.handle_command(line)
            except Exception as e:
                print(f"Error: {e}")

    def evaluate_expression(self, expr):
        for var in self.variables:
            expr = expr.replace(var, str(self.variables[var]))
        try:
            return eval(expr, {"__builtins__": {}})
        except Exception:
            return expr

    # -----------------------
    # Help
    # -----------------------
    def show_help(self):
        print("Available commands:")
        print("  exit           - Exit the Pebble console")
        print("  credits        - Show console credits")
        print("  help           - Show this help message")
        print("  cd <folder>    - Change current directory")
        print("  pebble <file>  - Run a .peg file in this console")
        print("  print <expr>   - Evaluate and print an expression")
        print("  gui <command>  - GUI commands or 'gui mode'")
        print("  leavegui       - Exit GUI mode if in it")
        print("\nSimple GUI instructions:")
        print("  1. gui canvas <width> <height>")
        print("  2. gui color <color>")
        print("  3. gui text \"<text>\" pos x:<num> z:<num>")
        print("  4. gui oval x:<startX> z:<startZ> x2:<endX> z2:<endZ> fill:<color>")
        print("  5. gui rect x:<startX> z:<startZ> x2:<endX> z2:<endZ> fill:<color>")
        print("  6. gui line x:<startX> z:<startZ> x2:<endX> z2:<endZ> color:<color>")
        print("  7. gui move id:<elementID> x:<newX> z:<newZ>")
        print("  8. gui delete id:<elementID>")
        print("  9. gui clear")
        print("More instructions at: https://pastebin.com/pjuw88a9")

if __name__ == "__main__":
    console = PebbleConsole()
    if len(sys.argv) > 1:
        console.run_peg_file(sys.argv[1])
    else:
        console.run()
