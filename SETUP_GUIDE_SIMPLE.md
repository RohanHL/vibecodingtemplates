# Cursor + Claude Code Setup - Simple Step-by-Step Guide

**Total Time:** 20-30 minutes
**Difficulty:** Complete beginner (no coding experience needed)

---

## ✅ Before You Start

You need:
- [ ] A Mac computer (macOS 10.15 or newer)
- [ ] Internet connection
- [ ] Your Mac password (for installing software)
- [ ] A Claude.ai Pro account (sign up at https://claude.ai - $20/month)

---

## Step 1: Install Cursor (5 minutes)

### 1.1 Download Cursor

1. Open your web browser (Safari, Chrome, etc.)
2. Go to: **https://cursor.com/download**
3. The page will show a big button - click it
4. A file will download (about 1-2 minutes)

### 1.2 Install Cursor

1. **Find the downloaded file:**
   - Open **Finder**
   - Click **Downloads** on the left side
   - Look for a file called **"Cursor.dmg"** or similar

2. **Double-click** the Cursor.dmg file

3. **A window will open showing:**
   - A Cursor icon
   - An Applications folder icon

4. **Drag the Cursor icon** to the Applications folder
   - Click and hold on the Cursor icon
   - Drag it over to the Applications folder
   - Let go

5. **Close the installer window**

6. **Open Cursor:**
   - Open **Finder**
   - Click **Applications** on the left side
   - Find **Cursor** and double-click it

7. **If you see a security warning:**
   - Click **Cancel**
   - Open **System Preferences** (from Apple menu)
   - Click **Security & Privacy**
   - At the bottom, click **"Open Anyway"**
   - Click **Open** to confirm

8. **Cursor will open!**
   - You might see a welcome screen
   - You might be asked to sign in (optional for now)

✅ **You're done with Step 1!** Cursor is now installed.

---

## Step 2: Install Node.js (5 minutes)

**Why?** This is needed to install Claude Code.

### 2.1 Download Node.js

1. Go to: **https://nodejs.org**
2. You'll see two big green buttons
3. Click the **LEFT** button (says "LTS" - Long Term Support)
4. A file will download (takes 1-2 minutes)

### 2.2 Install Node.js

1. **Find the downloaded file:**
   - Open **Finder**
   - Click **Downloads**
   - Look for a file called **"node-v20.something.pkg"**

2. **Double-click** the .pkg file

3. **Follow the installer:**
   - Click **Continue**
   - Click **Continue** again
   - Click **Agree**
   - Click **Install**
   - **Enter your Mac password**
   - Wait for installation (1-2 minutes)
   - Click **Close**

✅ **You're done with Step 2!** Node.js is installed.

---

## Step 3: Open the Terminal in Cursor (IMPORTANT!)

**This is where people get confused - follow carefully!**

### 3.1 Make Sure Cursor is Open

1. If Cursor isn't open, open it from Applications
2. You should see the Cursor window

### 3.2 Find the Terminal

**The terminal is a black (or dark) box at the bottom of Cursor where you type commands.**

**LOOK FOR:**
- At the very **bottom** of the Cursor window
- A dark/black area with text in it
- It might say something like `bash` or `zsh` or show your username

**CAN'T SEE IT?** Open it using the keyboard:

1. **Press these keys together:**
   - On your keyboard, find the **`** key (backtick - it's next to the number 1, shares a key with ~)
   - Hold down **Command (⌘)**
   - While holding Command, press **`** (backtick)
   - Or use: **Control + `**

2. **Or use the menu:**
   - At the top of your screen, click **Terminal**
   - Click **New Terminal**

### 3.3 What You Should See

After opening the terminal, you'll see:
- A dark box at the bottom of Cursor
- Some text ending with a **$** or **%** symbol
- A blinking cursor (line that blinks)

**Example of what it might look like:**
```
MacBook-Pro:~ yourname$ _
```
or
```
yourname@MacBook ~ % _
```

The `_` represents the blinking cursor where you'll type.

✅ **You found the terminal!** Now we can install Claude Code.

---

## Step 4: Install Claude Code (5 minutes)

**Now you'll type commands in the terminal. Don't worry - just copy and paste exactly what we show you!**

### 4.1 Check Node.js is Installed

1. **In the terminal (the dark box at the bottom), type:**
   ```
   node --version
   ```

2. **Press Enter**

3. **You should see something like:**
   ```
   v20.11.0
   ```
   (The numbers might be different - that's okay!)

**If you see "command not found":**
- Close Cursor completely
- Reopen Cursor
- Try again

### 4.2 Install Claude Code

1. **Copy this command** (click and drag to select, then Command+C):
   ```
   npm install -g @anthropic-ai/claude-code
   ```

2. **Paste it in the terminal:**
   - Click in the terminal (the dark box)
   - Press **Command+V** to paste
   - You should see the command appear

3. **Press Enter**

4. **Wait patiently!**
   - You'll see lots of text scrolling
   - Progress bars might appear
   - **This takes 30 seconds to 2 minutes**
   - Don't close Cursor!

5. **When it's done:**
   - The scrolling text stops
   - You see the `$` or `%` symbol again
   - The blinking cursor is back

**If you see "permission denied":**
- Try this command instead:
  ```
  sudo npm install -g @anthropic-ai/claude-code
  ```
- Enter your Mac password when asked
- You won't see the password as you type (that's normal!)
- Press Enter

### 4.3 Verify Installation

1. **Type this command:**
   ```
   claude --version
   ```

2. **Press Enter**

3. **You should see:**
   ```
   claude-code version 1.x.x
   ```
   (x.x will be numbers)

✅ **Success!** Claude Code is installed!

**If you see "command not found":**
1. Close Cursor completely
2. Reopen Cursor
3. Open the terminal again (Command + `)
4. Try `claude --version` again

---

## Step 5: Login to Claude Code (3 minutes)

**Almost done! Now we connect Claude Code to your Claude Pro account.**

### 5.1 Start the Login Process

1. **In the terminal, type:**
   ```
   claude /login
   ```

2. **Press Enter**

### 5.2 Choose Login Method

You'll see options like:
```
1. Claude Console (API access with billing)
2. Claude App (Pro or Max subscription)
3. Enterprise (Bedrock/Vertex AI)
```

**Type the number 2** (because you have Claude Pro)

**Press Enter**

### 5.3 Complete in Browser

1. **Your web browser will open automatically**
2. **You'll see a Claude.ai login page**
3. **Log in** with your Claude Pro account
   - Enter your email
   - Enter your password
   - Or use Google/GitHub if that's how you signed up

4. **Click "Authorize"** when you see the authorization screen

5. **Return to Cursor**

### 5.4 Confirm Success

**Back in the Cursor terminal, you should see:**
```
✓ Authentication successful
```

✅ **You're logged in!**

---

## Step 6: Test Claude Code (2 minutes)

**Let's make sure everything works!**

### 6.1 Start Claude Code

1. **In the terminal, type:**
   ```
   claude
   ```

2. **Press Enter**

### 6.2 What You Should See

You'll see:
- Some welcome text
- Information about your session
- A prompt that looks like: `>`

**This means Claude Code is ready!**

### 6.3 Test It

1. **Type this question:**
   ```
   What files are in this directory?
   ```

2. **Press Enter**

3. **Claude should respond** with information about files in your current folder

### 6.4 Exit Claude Code

**To exit and return to the normal terminal:**

**Type:**
```
/exit
```

**Press Enter**

You're back to the regular terminal prompt.

---

## 🎉 You Did It!

**You've successfully installed:**
✅ Cursor - Your AI-powered code editor
✅ Node.js - Required software
✅ Claude Code - Your AI coding assistant
✅ Logged in to Claude Code

---

## 🚀 What's Next?

### Daily Usage

**Every time you want to use Claude Code:**

1. **Open Cursor**
2. **Open the terminal** (Command + `)
3. **Type:** `claude`
4. **Press Enter**
5. **Start asking Claude to help you code!**

### Example Things to Try

Once you're in Claude Code (after typing `claude`):

**Create a simple website:**
```
> Create a simple HTML page with a heading and a button
```

**Learn something:**
```
> Explain what Python is in simple terms
```

**Get help with code:**
```
> How do I create a folder in the terminal?
```

**Exit when done:**
```
> /exit
```

---

## 🆘 Troubleshooting

### Problem: HTML guide didn't open

**If the HTML file shows code instead of a webpage:**

1. **Right-click** the HTML file
2. Choose **"Open With"**
3. Select your **web browser** (Safari, Chrome, Firefox, Edge)

**Or:** Just use this Markdown guide instead! It works in any text editor.

### Problem: Can't find the terminal in Cursor

**The terminal is the dark box at the bottom of Cursor.**

**To open it:**
- Press **Command + `** (backtick key)
- Or: Top menu → Terminal → New Terminal

**If you still can't see it:**
- Look at the very bottom of the Cursor window
- You might need to drag the divider up to make it bigger

### Problem: "command not found: claude"

**Solution:**
1. Close Cursor completely (Command + Q)
2. Reopen Cursor
3. Open terminal (Command + `)
4. Try again

### Problem: Installation is taking forever (10+ minutes)

**Solution:**
1. Press **Control + C** to cancel
2. Close Cursor
3. Reopen Cursor
4. Try the installation command again

### Problem: "permission denied"

**Solution:**
Use `sudo` before the command:
```
sudo npm install -g @anthropic-ai/claude-code
```
Enter your Mac password when asked.

---

## 📞 Still Need Help?

**Common issues and what they mean:**

1. **"npm: command not found"**
   - Node.js didn't install correctly
   - Go back to Step 2 and reinstall Node.js

2. **"claude: command not found"**
   - Claude Code didn't install correctly
   - Make sure Step 4 completed without errors
   - Try closing and reopening Cursor

3. **Terminal won't open**
   - Try: Command + ` (backtick)
   - Or: Control + `
   - Or: Top menu → Terminal → New Terminal

4. **Can't see where to type**
   - Look for the dark box at the bottom
   - Look for a blinking cursor
   - Look for a `$` or `%` symbol

---

## 📋 Quick Reference Card

**Print or bookmark this!**

### Opening Terminal in Cursor
```
Keyboard: Command + `
or
Menu: Terminal → New Terminal
```

### Installing Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### Logging In
```bash
claude /login
```
Choose option 2, authorize in browser

### Starting Claude Code
```bash
claude
```

### Exiting Claude Code
```
/exit
```

### Checking Versions
```bash
node --version
npm --version
claude --version
```

---

**That's it! You're ready to start coding with AI assistance!** 🚀

**Created for complete beginners by someone who understands the struggle.**

---

## 💡 Pro Tips

1. **Keep this guide open** while you work through the steps
2. **Don't skip steps** - they're all important
3. **Read error messages** - they often tell you what's wrong
4. **Ask for help** - it's okay to not know everything!
5. **Take breaks** - if you're frustrated, step away for 5 minutes

**Good luck!** 🎉
