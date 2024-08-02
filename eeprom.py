import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import serial.tools.list_ports
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

class EEPROMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EEPROM Manager")

        self.port = None
        self.baudrate = 9600

        self.create_port_selection_frame()
        self.create_eeprom_interface_frame()

    def create_port_selection_frame(self):
        self.port_selection_frame = ttk.Frame(self.root)
        self.port_selection_frame.grid(row=0, column=0, padx=10, pady=10)

        self.port_label = ttk.Label(self.port_selection_frame, text="Porta Serial:")
        self.port_label.grid(row=0, column=0)
        self.port_combobox = ttk.Combobox(self.port_selection_frame, values=self.get_serial_ports())
        self.port_combobox.grid(row=0, column=1)

        self.baudrate_label = ttk.Label(self.port_selection_frame, text="Velocidade:")
        self.baudrate_label.grid(row=1, column=0)
        self.baudrate_combobox = ttk.Combobox(self.port_selection_frame, values=[9600, 19200, 38400, 57600, 115200])
        self.baudrate_combobox.grid(row=1, column=1)
        self.baudrate_combobox.set(9600)

        self.connect_button = ttk.Button(self.port_selection_frame, text="Conectar", command=self.connect_serial)
        self.connect_button.grid(row=2, column=0, columnspan=2)

    def create_eeprom_interface_frame(self):
        self.eeprom_frame = ttk.Frame(self.root)

        self.address_label = ttk.Label(self.eeprom_frame, text="Endereço:")
        self.address_label.grid(row=0, column=0)
        self.address_entry = ttk.Entry(self.eeprom_frame)
        self.address_entry.grid(row=0, column=1)

        self.value_label = ttk.Label(self.eeprom_frame, text="Valor:")
        self.value_label.grid(row=1, column=0)
        self.value_entry = ttk.Entry(self.eeprom_frame)
        self.value_entry.grid(row=1, column=1)

        self.read_button = ttk.Button(self.eeprom_frame, text="Ler Endereço", command=self.read_address)
        self.read_button.grid(row=2, column=0)

        self.write_button = ttk.Button(self.eeprom_frame, text="Escrever Endereço", command=self.write_address)
        self.write_button.grid(row=2, column=1)

        self.read_all_button = ttk.Button(self.eeprom_frame, text="Ler Toda EEPROM", command=self.read_all)
        self.read_all_button.grid(row=3, column=0)

        self.clear_button = ttk.Button(self.eeprom_frame, text="Limpar EEPROM", command=self.clear_eeprom)
        self.clear_button.grid(row=3, column=1)

        self.filepath_label = ttk.Label(self.eeprom_frame, text="Salvar saída em:")
        self.filepath_label.grid(row=4, column=0)
        self.filepath_entry = ttk.Entry(self.eeprom_frame)
        self.filepath_entry.grid(row=4, column=1)

        self.output_text = tk.Text(self.eeprom_frame, height=20, width=50)
        self.output_text.grid(row=5, column=0, columnspan=2)

        self.export_button = ttk.Button(self.eeprom_frame, text="Exportar Leitura", command=self.export_log)
        self.export_button.grid(row=6, column=0, columnspan=2)

        self.open_serial_monitor_button = ttk.Button(self.eeprom_frame, text="Abrir Monitor Serial", command=self.open_serial_monitor)
        self.open_serial_monitor_button.grid(row=7, column=0, columnspan=2)

        self.open_graph_button = ttk.Button(self.eeprom_frame, text="Abrir Gráfico Analógico", command=self.open_analog_graph)
        self.open_graph_button.grid(row=8, column=0, columnspan=2)

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect_serial(self):
        selected_port = self.port_combobox.get()
        selected_baudrate = self.baudrate_combobox.get()

        if not selected_port:
            messagebox.showerror("Erro", "Selecione uma porta serial")
            return

        self.port = selected_port
        self.baudrate = int(selected_baudrate)

        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=1)
            self.port_selection_frame.grid_remove()
            self.eeprom_frame.grid(row=0, column=0, padx=10, pady=10)
        except serial.SerialException as e:
            messagebox.showerror("Erro", f"Erro ao conectar na porta: {e}")

    def send_command(self, command, address=None, value=None):
        self.serial_port.write(command.encode())
        if address is not None:
            self.serial_port.write((str(address) + '\n').encode())
        if value is not None:
            self.serial_port.write((str(value) + '\n').encode())
        time.sleep(0.1)  # Esperar um pouco para o Arduino processar o comando

    def log_output(self, response):
        self.output_text.insert(tk.END, response + '\n')
        filepath = self.filepath_entry.get()
        if filepath:
            with open(filepath, 'a') as file:
                file.write(response + '\n')

    def export_log(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filepath:
            with open(filepath, 'w') as file:
                file.write(self.output_text.get("1.0", tk.END))

    def read_address(self):
        try:
            address = int(self.address_entry.get())
            self.send_command('R', address)
            response = self.serial_port.readline().decode().strip()
            self.log_output(response)
        except ValueError:
            messagebox.showerror("Erro", "Endereço inválido")

    def write_address(self):
        try:
            address = int(self.address_entry.get())
            value = int(self.value_entry.get())
            self.send_command('W', address, value)
            response = self.serial_port.readline().decode().strip()
            self.log_output(response)
        except ValueError:
            messagebox.showerror("Erro", "Endereço ou valor inválido")

    def read_all(self):
        self.send_command('r')
        while True:
            response = self.serial_port.readline().decode().strip()
            if not response:
                break
            self.log_output(response)

    def clear_eeprom(self):
        self.send_command('C')
        response = self.serial_port.readline().decode().strip()
        self.log_output(response)

    def open_serial_monitor(self):
        self.serial_monitor_window = tk.Toplevel(self.root)
        self.serial_monitor_window.title("Monitor Serial")

        self.command_label = ttk.Label(self.serial_monitor_window, text="Comando Serial:")
        self.command_label.grid(row=0, column=0)
        self.command_entry = ttk.Entry(self.serial_monitor_window)
        self.command_entry.grid(row=0, column=1)

        self.send_button = ttk.Button(self.serial_monitor_window, text="Enviar", command=self.send_commands)
        self.send_button.grid(row=0, column=2)

        self.serial_output_text = tk.Text(self.serial_monitor_window, height=10, width=50)
        self.serial_output_text.grid(row=1, column=0, columnspan=3)

    def send_commands(self):
        commands = self.command_entry.get().split(',')
        for command in commands:
            self.serial_port.write(command.strip().encode() + b'\n')
            response = self.serial_port.readline().decode().strip()
            self.serial_output_text.insert(tk.END, response + '\n')

    def open_analog_graph(self):
        self.analog_graph_window = tk.Toplevel(self.root)
        self.analog_graph_window.title("Gráfico Analógico")

        fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(fig, master=self.analog_graph_window)
        self.canvas.get_tk_widget().pack()

        self.analog_data = {f"A{i}": [] for i in range(6)}
        self.digital_data = {f"D{i}": [] for i in range(2, 14)}

        self.ani = animation.FuncAnimation(fig, self.update_graph, interval=144)
        self.canvas.draw()

    def update_graph(self, frame):
        self.serial_port.write(b'A\n')
        for i in range(6):
            response = self.serial_port.readline().decode().strip()
            if response:
                self.analog_data[f"A{i}"].append(float(response))

        for i in range(2, 14):
            response = self.serial_port.readline().decode().strip()
            if response:
                self.digital_data[f"D{i}"].append(float(response))

        self.ax.clear()
        for key, values in self.analog_data.items():
            self.ax.plot(values, label=key)
        for key, values in self.digital_data.items():
            self.ax.plot(values, label=key)

        self.ax.legend()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = EEPROMApp(root)
    root.mainloop()
