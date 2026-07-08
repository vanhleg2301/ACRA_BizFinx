===============================================================
  ACRA HELPER — USER GUIDE
===============================================================

This tool builds an XBRL filing package from financial statements
(Word/Excel) for submission to ACRA via BizFinx. It runs entirely on
your own computer — nothing is uploaded or sent anywhere.


STEP 1 — UNZIP
---------------
Extract the whole .zip file to any folder, for example:
   Desktop\ACRA-Helper\

After extracting, the folder must have exactly this structure:

   ACRA-Helper\
   ├── ACRA-Helper.exe      ← the program
   ├── companies\           ← company data (MUST stay next to the .exe)
   └── README.txt           ← this file

   ⚠ Do not separate "companies" from "ACRA-Helper.exe" — if they end
     up in different folders, the program won't find the company data.


STEP 2 — RUN THE PROGRAM
--------------------------
1. Double-click "ACRA-Helper.exe".

2. If Windows shows a blue "Windows protected your PC" screen:
      → Click "More info"
      → Click "Run anyway"
   This is Windows' default warning for any new app that hasn't
   purchased a commercial code-signing certificate (which costs a few
   hundred USD/year) — it is NOT a virus warning. The program only
   runs locally on your machine and does not send anything out.

3. Windows Defender Firewall may ask to "allow this app on private/
   public networks" — click "Allow access" (the program only uses
   your machine's local network, not the internet).

4. Wait about 3-5 seconds. Your default browser (Chrome/Edge/Firefox)
   will open automatically to the app's interface.

   If nothing opens after 10 seconds, open a browser yourself and go
   to:
        http://localhost:5000


STEP 3 — TRY IT WITH SAMPLE DATA
-----------------------------------
Click "Run Demo" in the bottom-left corner. The program will run
against built-in sample data (a company called "EVX Ventures") and
let you download the resulting ZIP package so you can see the whole
workflow end to end.


STEP 4 — PROCESS A REAL FILING
---------------------------------
1. Select a company in the left sidebar (if one is already listed).
2. Drag-and-drop (or click to browse) the Word (.docx) and/or Excel
   (.xlsx) financial statements into the two "Input Files" boxes.
3. Choose a mode under "Run Options":
      • Pre-fill (Excel + JSON)  → produces files to review
      • Full XBRL Package        → produces the ZIP for ACRA filing
4. Click the "Run" button (purple).
5. Check the result: a GREEN dot means success, a RED dot means
   there are errors to fix in the source Word/Excel file before
   re-running.
6. Click "Download ZIP" to get the result package.

For more detail, see the "How to use — filing workflow" section at
the top of the page inside the app (click it to expand).


STEP 5 — SUBMIT TO ACRA
--------------------------
1. Open the downloaded ZIP with the BizFinx Preparation Tool (ACRA's
   free Excel add-in — download it from the ACRA website if you don't
   have it yet).
2. In BizFinx: click "Validate" (offline check).
3. If there are no errors: click "Validate Online" → "Acknowledge and
   Upload" to file it officially.


CLOSING THE PROGRAM
----------------------
The program runs in the background with no window of its own (only
your browser tab). To close it: close the browser tab, then open
Task Manager (Ctrl+Shift+Esc) → find "ACRA-Helper.exe" → click
"End task".


FREQUENTLY ASKED QUESTIONS
-----------------------------
Q: Do I need an internet connection?
A: No. Everything runs locally on your computer.

Q: Will my uploaded files or results be lost when I close the app?
A: No. They're saved automatically in "inputs" and "output" folders
   that appear right next to ACRA-Helper.exe.

Q: The browser says "localhost refused to connect"?
A: The program may still be starting up, or it was closed earlier via
   Task Manager — relaunch "ACRA-Helper.exe" and wait a few seconds.

Q: The "Full set of financial statements" section in the XBRL package
   lost its table formatting (plain running text, no tables)?
A: This happens when LibreOffice isn't installed on this machine.
   LibreOffice is a free office suite the program uses to preserve
   tables and bold formatting from the original Word file. Download
   and install it (free, ~5 minutes) from:
        https://www.libreoffice.org/download/
   Nothing else to configure — once installed, just re-run the
   program and it will automatically pick it up.


-----------------------------------------------------------------
If you run into any issues while trying this out, please get back
in touch and we'll help.
-----------------------------------------------------------------
