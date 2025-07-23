import queue
import subprocess
import csv
import threading
import math
import tkinter as tk
from tkinter import ttk
from datetime import datetime


root = tk.Tk()
root.attributes("-fullscreen", True)
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
rows, chunks = [], []
currentInd, completeChunks, i, j = 0, 0, 0, 0
tree = None
UIqueue = queue.Queue()

runningChunks = {}

scrollPos = 0.0


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

def Worker(chunkInd: int):
    chunk = rows[chunkInd]
    for DeviceName, Ip in chunk["rows"]:
        UIqueue.put((chunkInd, DeviceName, Ip, isAlive(Ip)))
    UIqueue.put((chunkInd, None, None, None))
    print(f"Thread started for chunk {chunkInd}")

    print(f"logs: {runningChunks}")



def RemoveStuckChunks():
    now = datetime.now()
    for chunkInd, timeS in list(runningChunks.items()):
        if (now - timeS).total_seconds() > rows[chunkInd].get("timer"):
            print(f"chunk {chunkInd} stuck since {timeS}, removing now")
            runningChunks.pop(chunkInd)
            multiCheckIps(chunkInd)



def Reset():
    global rows, currentInd, i, j, tree, completeChunks, totalChunks

    print("Reset triggered")

    RemoveStuckChunks()

    for widget in frame.winfo_children():
        widget.destroy()

    global UIqueue
    UIqueue = queue.Queue()
    rows.clear()
    currentInd, i, j = 0, 0, 0

    rows[:] = openCSV()
    totalChunks = len(rows)

    for chunkInd in range(totalChunks):
        if j == 4:
            i += 2
            j = 0
        multiCheckIps(chunkInd)
        j+=1



def openCSV():
    chunks = []
    with open("ips.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)

        curChunk = None

        titleName = ""
        totalSplits = 1
        timer = 0

        for row in reader:
            DeviceName = row[0]
            Ip = row[1]

            if Ip == "":
                titleName = row[0]
                totalSplits = 1
                timer = int(row[2])
                if curChunk:
                    chunks.append(curChunk)
                curChunk = {"title": titleName, "rows":[], "timer": timer if timer else 60}

            else:
                if len(curChunk["rows"]) == 25:
                    totalSplits += 1
                    chunks.append(curChunk)
                    curChunk = {"title": f"{titleName} - {totalSplits}", "rows": [], "timer": timer if timer else 60}
                curChunk["rows"].append([DeviceName, Ip])

        chunks.append(curChunk)
    return chunks



def multiCheckIps(chunkInd=None):
    global rows, currentInd, i, j, tree

    if chunkInd is None:
        chunkInd = currentInd

    RemoveStuckChunks()

    if runningChunks.get(chunkInd):
        print(f"Chunk already running: {chunkInd}")
        return

    runningChunks[chunkInd] = datetime.now()

    rows[chunkInd].setdefault("pos", (i, j))

    title = TempTitle(rows[chunkInd]["title"], chunkInd, i, j)
    tree = makeTable(i, j)

    rows[chunkInd]["tree"] = tree
    rows[chunkInd]["label"] = title

    threading.Thread(target=Worker, args=(chunkInd,), daemon=True).start()



def ProccessUIqueue():
    global completeChunks, totalChunks
    try:
        while True:
            chunkInd, DeviceName, Ip, isAlive = UIqueue.get_nowait()

            if chunkInd < 0 or chunkInd >= len(rows):
                continue

            chunk = rows[chunkInd]

            tree = chunk.get("tree")
            label = chunk.get("label")

            if tree is None:
                continue

            if DeviceName is None:
                completeChunks +=1
                success = sum(1 for iid in tree.get_children("") if "success" in tree.item(iid, "tags"))
                makeTitle(label, chunk["title"], chunkInd, success)

                print(f"complete chunk: {chunkInd}")

                runningChunks.pop(chunkInd, None)

                print(f"logs remaining: {runningChunks}")

                root.after((chunk.get("timer")*1000), lambda chunkIndCopy = chunkInd: reCheckChunks(chunkIndCopy))
                continue
            iid = tree.insert("", tk.END, values=(DeviceName, Ip))
            tree.item(iid, tags=("success" if isAlive else "failed",))
    except queue.Empty:
        pass
    root.after(50, ProccessUIqueue)



def reCheckChunks(chunkInd):
    global i, j, currentInd, rows

    newChunks = openCSV()

    if chunkInd >= len(newChunks):
        return

    if len(newChunks) != totalChunks or any((newChunks[i]["title"] != rows[i]["title"] or newChunks[i]["timer"] != rows[i]["timer"]) for i in range(len(rows))):
        print(f"miss mach amount: {totalChunks} doesnt equal number of chunks {len(newChunks)} \nor new differnet timer added/edited")
        Reset()
        return

    updatedChunks = newChunks[chunkInd]

    tree = rows[chunkInd].pop("tree", None)
    if tree:
        tree.destroy()
    label = rows[chunkInd].pop("label", None)
    if label:
        label.destroy()

    i, j = rows[chunkInd].get("pos", (0, 0))

    rows[chunkInd]["title"] = updatedChunks["title"]
    rows[chunkInd]["rows"] = updatedChunks["rows"]

    multiCheckIps(chunkInd)



def TempTitle(tableTitle, currentInd, i, j):
    label = tk.Label(frame, text=tableTitle + ":\n ... / " + str(len(rows[currentInd]["rows"])), font=("Helvetica", 17, "bold"), bd=1.5, bg="lightblue", relief="solid", padx=5, pady=5)
    label.grid(row=i, column=j, sticky="N", padx=10, pady=10)
    return label

def makeTitle(title, tableTitle, currentInd, numberSuccess):
    title.config(text=tableTitle + ":\n" + str(numberSuccess) + " / " + str(len(rows[currentInd]["rows"])))

def makeTable(i, j):
    ttk.Style().configure("Treeview", rowheight=35, bd=1, font=('Helvetica', 20))

    tree = ttk.Treeview(frame, columns = ("DeviceName","IPAddress"), show="headings", style="Treeview", height=25)

    tree.heading("DeviceName", text="Device Name", anchor="center")
    tree.heading("IPAddress", text="IP Address", anchor="center")

    tree.column("DeviceName", width=175, anchor="center")
    tree.column("IPAddress", width=225, anchor="center")

    tree.tag_configure("failed", background="#E14B2A")
    tree.tag_configure("success", background="#98fb98")

    tree.grid(row=i+1, column=j, sticky="w", padx=10, pady=10)

    return tree

def autoScroll(step=1):
    global totalChunks, scrollPos
    rowPercent = 1.0/(math.ceil(totalChunks / 4))

    scrollPos += rowPercent
    if scrollPos >= 1.0:
        scrollPos = 0.0

    canvas.yview_moveto(scrollPos)

    root.after(5000 ,autoScroll)

Reset()
ProccessUIqueue()
autoScroll()
root.mainloop()