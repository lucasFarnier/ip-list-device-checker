import subprocess

import csv

import tkinter as tk
from tkinter import ttk


def isAlive(ip):
    try:

        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 6

        result = subprocess.run(
            ['ping', '-n', '1', '-w', '500',
            str(ip)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo = si
        )
        return result.returncode == 0
    except:
        return False


def checkIps():
    with open("ips.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)
        for row in reader:
            print(row[1])
            isIpAlive = isAlive(row[1])
            ID = treeviews["All IPs"].insert("", tk.END, values=(row[0], row[1]))
            if isIpAlive:
                treeviews["All IPs"].item(ID, tags=("success"))
            else:
                treeviews["All IPs"].item(ID, tags=("failed"))
                FailedID = treeviews["Failed"].insert("", tk.END, values=(row[0], row[1]))
                treeviews["Failed"].item(FailedID, tags=("failed"))


root = tk.Tk()
root.title("IP List Device Checker")
frame = tk.Frame(root)
frame.grid(pady=10)

ttk.Style().configure("Treeview", rowheight=75)

tables = ("All IPs", "Failed")
columns = ("Device-Name", "IP-Address")
treeviews = {}
i = 0
for tab in tables:
    label = tk.Label(frame, text=tab, font=("Arial", 12, "bold"))
    label.grid(row=0, column=i)

    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, width=450, anchor="center", font=("Arial", 18, "bold"))
    tree.grid(row=1, column=i, padx=10, sticky="nsew")

    treeviews[tab] = tree

    i += 1

root.after(0, checkIps)

treeviews["All IPs"].tag_configure("success", background="#ADEA33")
treeviews["All IPs"].tag_configure("failed", background="#E14B2A")
treeviews["Failed"].tag_configure("failed", background="#E14B2A")

root.mainloop()