import os
import subprocess
import csv
import tkinter as tk
from tkinter import ttk



root = tk.Tk()
root.title("IP List Device Checker")
outFrame = tk.Frame(root)
outFrame.pack(fill="both", expand=True)

canvas = tk.Canvas(outFrame, highlightthickness=0)
Ybar = tk.Scrollbar(outFrame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=Ybar.set)
Ybar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

frame = tk.Frame(canvas)
canvasWindow = canvas.create_window((0, 0), window=frame, anchor="nw")

def onFrameConfig(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
frame.bind("<Configure>", onFrameConfig)

treeviews = {}



rows = []
currentInd, numberOfIPs, numberOn, i, j = 0, 0, 0, 0, 0
tableTitle,tree = None, None



def Reset():
    global rows, currentInd, numberOfIPs, numberOn, i, j, tableTitle, tree

    for widget in frame.winfo_children():
        widget.destroy()

    rows = []
    currentInd, numberOfIPs, numberOn, i, j = 0, 0, 0, 0, 0
    tableTitle, tree = None, None

    openCSV()
    root.after(0, checkIps)



def openCSV():
    global rows
    with open("ips.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)
        rows = list(reader)
    csvfile.close()



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
    global currentInd, numberOfIPs, numberOn, i, j, tableTitle, tree

    if currentInd >= len(rows):
        if numberOfIPs != 0 and tableTitle:
            makeTitle(tableTitle, i, j, numberOfIPs, numberOn)
        root.after(5000, Reset)
        return
    row = rows[currentInd]
    currentInd += 1

    if row[1] == "":
        if numberOfIPs > 0:
            numberOfIPs, numberOn = makeTitle(tableTitle, i, j, numberOfIPs, numberOn)
        tableTitle = row[0]
        tree, i, j = makeTable(i, j)
    else:
        isIpAlive = isAlive(row[1])
        numberOfIPs += 1
        ID = tree.insert("", tk.END, values=(row[0], row[1]))
        if not isIpAlive:
            tree.item(ID, tags=("failed"))
        else:
            tree.item(ID, tags=("success"))
            numberOn += 1

        tree.tag_configure("failed", background="#E14B2A")
        tree.tag_configure("success", background="#98fb98")

        tree.see(ID)
        root.after(100)

    root.after(100, checkIps)



def makeTitle(tableTitle, i, j, numberOfIPs, numberOn):
    if numberOfIPs != 0 and "tableTitle" in locals():
        label = tk.Label(frame, text=tableTitle + ":\n" + str(numberOn) + " / " + str(numberOfIPs), font=("Helvetica", 17, "bold"), bd=1.5, bg="lightblue", relief="solid", padx=5, pady=5)
        label.grid(row=i, column=j, sticky="N", padx=10, pady=10)
        return 0, 0



def makeTable(i, j):
    if (j == 5):
        i += 2
        j = 1
    else:
        j += 1

    ttk.Style().configure("Treeview", rowheight=50)


    tree = ttk.Treeview(frame, columns = ("DeviceName","IPAddress"), show="headings")
    tree.heading("DeviceName", text="Device Name", anchor="center")
    tree.heading("IPAddress", text="IP Address", anchor="center")
    tree.column("DeviceName", minwidth=100, anchor="center")
    tree.column("IPAddress", minwidth=100, anchor="center")

    tree.grid(row=i+1, column=j, sticky="w", padx=10, pady=10)

    return tree, i, j



Reset()
root.mainloop()