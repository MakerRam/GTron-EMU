# com0com Installation - Step-by-Step Guide

## ✅ Prerequisites
- Windows machine (where LabVIEW will run)
- Administrator access
- Internet connection to download

---

## 📥 Step 1: Download com0com

### Option A: Direct Download (Recommended)
1. Open your web browser
2. Go to: https://sourceforge.net/projects/com0com/files/
3. Look for the latest version (usually at the top)
4. Download: **com0com-3.0.0.0-i386-and-x64-signed.zip**
   - The filename might be slightly different but should contain "3.0" or similar

### Option B: If you need help finding it
- The page shows multiple files
- Look for one that says **"signed.zip"** (not .exe)
- It should be 1-2 MB in size

### Where it goes:
- File downloads to your **Downloads** folder
- That's fine, leave it there for now

---

## 📂 Step 2: Extract the ZIP File

1. Open **File Explorer**
2. Navigate to **Downloads** folder
3. Find **com0com-3.0.0.0-i386-and-x64-signed.zip** file
4. **Right-click** on it
5. Select **"Extract All..."**
6. Choose a location (Downloads is fine)
7. Click **"Extract"**

**Wait for extraction to finish** (should take a few seconds)

### Result:
You'll see a new folder: **com0com-3.0.0.0** (or similar name)

---

## 🔧 Step 3: Run Setup as Administrator

1. Open the extracted **com0com-3.0.0.0** folder
2. Find **setup.exe** file
3. **Right-click** on setup.exe
4. Select **"Run as administrator"**

**A window will pop up asking for permission.** Click **"Yes"**

---

## 📋 Step 4: Installation Wizard - Welcome Screen

When setup opens, you'll see:
```
com0com Setup Wizard

Welcome to com0com Setup Wizard

This will install com0com on your computer.

[Next >] [Cancel]
```

Click **"Next >"**

---

## 🖱️ Step 5: License Agreement

You'll see:
```
License Agreement

Please read the following license agreement...

[I Agree] [I Disagree] [Cancel]
```

Click **"I Agree"** (you must agree to continue)

---

## 📍 Step 6: Installation Location

You'll see:
```
Installation Folder

Destination folder:
C:\Program Files (x86)\com0com

[Browse...] [Next >] [Cancel]
```

**Just click "Next >"** (default location is fine)

---

## ⚙️ Step 7: IMPORTANT - Install Port Pair

This is the KEY step! You'll see:

```
Installation Options

☑ Install port pair
  Port name 1: COM3
  Port name 2: COM4

[< Back] [Next >] [Cancel]
```

**MAKE SURE the checkbox is CHECKED (☑)**

**Verify the port names:**
- Port name 1: **COM3** ✅
- Port name 2: **COM4** ✅

If they're different, you can change them, but COM3 and COM4 are recommended.

Click **"Next >"**

---

## ⏳ Step 8: Ready to Install

You'll see:
```
Ready to Install

The wizard is ready to install com0com.

Destination folder: C:\Program Files (x86)\com0com
Port pair: COM3 <-> COM4

[< Back] [Install] [Cancel]
```

**Review the settings:**
- ✅ Destination folder looks good
- ✅ Port pair shows COM3 <-> COM4

Click **"Install"** to begin

---

## 🔄 Step 9: Installation In Progress

You'll see a progress bar:
```
Please wait while the installer completes...

[████████░░░░░░░░░░░░] 45%
```

**Wait for it to complete.** This usually takes 10-30 seconds.

You may see a security prompt from Windows:
```
Windows Security
The following software is trying to install device drivers:

"com0com 3.0 Device Drivers"

Do you want to install this software?

[Install] [Don't install]
```

Click **"Install"** (com0com needs to install drivers for the virtual ports)

---

## ✅ Step 10: Installation Complete

You'll see:
```
Installation Complete

com0com has been successfully installed.

☐ Run emulator immediately

[Finish]
```

**Do NOT check the "Run emulator immediately" box**

Click **"Finish"**

---

## 🔄 Step 11: Restart (If Prompted)

After clicking Finish, you might see:
```
Restart Required

You must restart your computer for the changes to take effect.

[Restart Now] [Restart Later]
```

**Choose one:**
- Click **"Restart Now"** (recommended - faster)
- OR click **"Restart Later"** and restart manually later

### If you choose "Restart Now":
- Computer will restart
- Sign back in when it's done
- Continue to Step 12

### If you choose "Restart Later":
- Close any open applications
- Restart your computer manually
- Then continue to Step 12

---

## ✔️ Step 12: Verify Installation (After Restart)

After your computer restarts, verify that com0com is installed correctly:

1. Press **Windows key** on your keyboard
2. Type: **devmgmt.msc**
3. Press **Enter**
4. **Device Manager** window opens

### In Device Manager:
1. Look for **"Ports (COM & LPT)"** section
2. Click the arrow to expand it
3. You should see:
   ```
   ✅ COM3 (Virtual - This is from com0com)
   ✅ COM4 (Virtual - This is from com0com)
   ```

**Both should be there!** If you see them, com0com is installed correctly! 🎉

---

## 🎯 Step 13: You're Done!

**Congratulations!** com0com is now installed.

### What you now have:
- ✅ COM3 - Emulator will listen here
- ✅ COM4 - LabVIEW will connect here
- ✅ Both are connected (virtual pair)

### You never need to do this again!

---

## 🚀 Now You Can Test

### Terminal 1 (WSL2):
```bash
cd /mnt/d/TDD/Emulator
python3 firmware_emulator/src/main.py --port COM3 --verbose
```

### Terminal 2 (Windows):
```bash
labview &
```

### In LabVIEW:
1. Configure: **COM4** at **9600 baud**
2. Click **Connect**
3. Watch Terminal 1 for: `[QUERY] RECV: QUERY → SEND: YES`
4. LabVIEW is now connected! ✅

---

## ❌ Troubleshooting Installation

### Problem: Setup.exe won't run
**Solution:**
1. Make sure you extracted the ZIP first
2. Right-click setup.exe
3. Select "Run as administrator"
4. If still fails, try: properties → compatibility → run as admin

### Problem: Installer asks for reboot but doesn't show the dialog
**Solution:**
1. Just restart your computer manually
2. Click Start → Power → Restart
3. After restart, verify COM3/COM4 in Device Manager

### Problem: COM3/COM4 don't appear in Device Manager
**Solution:**
1. Make sure you checked "Install port pair" during setup
2. Make sure you restarted after installation
3. Try installing again (uninstall first via Control Panel)

### Problem: Installation fails with error
**Solution:**
1. Close all applications
2. Right-click setup.exe
3. Select "Run as administrator"
4. Click "Yes" to all permission prompts

---

## ✅ Verification Checklist

After installation, you should have:

- [ ] Downloaded com0com ZIP file
- [ ] Extracted the ZIP file
- [ ] Ran setup.exe as Administrator
- [ ] Clicked "I Agree" on license
- [ ] Confirmed "Install port pair" was checked (COM3 & COM4)
- [ ] Clicked "Install"
- [ ] Computer restarted
- [ ] Opened Device Manager
- [ ] Verified COM3 and COM4 appear in "Ports (COM & LPT)"

If all checkboxes are checked: **You're ready to test!** 🎉

---

## 📞 Need Help?

### If installation fails:
1. Try again from Step 1
2. Make sure you're using Administrator account
3. Close all other applications before installing

### If COM3/COM4 don't appear:
1. Restart computer again
2. Open Device Manager fresh
3. Expand "Ports (COM & LPT)" section again

### If you see different COM ports:
That's OK! As long as you see TWO new virtual COM ports, they should work.
Just note the port names for later.

---

**That's it!** You now have com0com installed and ready to use! 🚀

Let me know when you've completed the installation and verified COM3/COM4 in Device Manager.
