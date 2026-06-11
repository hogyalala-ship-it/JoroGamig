import os
import time
import base64
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8813676463:AAHXrJ_p6ENXucNHeYgUxkS87TQlOF3Q4zo"
GITHUB_USERNAME = "dolflexff-sudo"
GITHUB_TOKEN = "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"
GITHUB_REPO = "my-files"

async def start(update, context):
    keyboard = [[InlineKeyboardButton("📤 SEND FILE", callback_data="how")]]
    await update.message.reply_text(
        "🚀 *FILE TO LINK BOT*\n\nSend me any file - I'll give Chrome download link!\n\n✅ Lifetime links\n✅ Direct download",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def how_to(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📤 Send me any photo, video, document or audio file!\n\nI'll upload to GitHub and give you a permanent Chrome download link.")

async def handle_file(update, context):
    msg = update.message
    
    if msg.document:
        file = msg.document
        name = file.file_name.replace('/', '_').replace(' ', '_')
    elif msg.photo:
        file = msg.photo[-1]
        name = f"photo_{int(time.time())}.jpg"
    elif msg.video:
        file = msg.video
        name = file.file_name or f"video_{int(time.time())}.mp4"
        name = name.replace('/', '_').replace(' ', '_')
    elif msg.audio:
        file = msg.audio
        name = file.file_name or f"audio_{int(time.time())}.mp3"
        name = name.replace('/', '_').replace(' ', '_')
    else:
        await msg.reply_text("Please send a file!")
        return
    
    status = await msg.reply_text(f"📤 Uploading `{name}`...", parse_mode='Markdown')
    
    try:
        file_obj = await file.get_file()
        temp_path = f"temp_{int(time.time())}_{name}"
        await file_obj.download_to_drive(temp_path)
        
        with open(temp_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode()
        
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        
        # Check if repo exists, if not create it
        repo_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}"
        repo_check = requests.get(repo_url, headers=headers)
        
        if repo_check.status_code == 404:
            create_url = "https://api.github.com/user/repos"
            repo_data = {"name": GITHUB_REPO, "private": False}
            requests.post(create_url, json=repo_data, headers=headers)
        
        # Upload file
        upload_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{name}"
        data = {"message": f"Upload {name}", "content": content, "branch": "main"}
        
        response = requests.put(upload_url, json=data, headers=headers)
        os.remove(temp_path)
        
        if response.status_code in [200, 201]:
            download_url = f"https://cdn.jsdelivr.net/gh/{GITHUB_USERNAME}/{GITHUB_REPO}/{name}"
            keyboard = [[InlineKeyboardButton("🌐 DOWNLOAD IN CHROME", url=download_url)]]
            await status.edit_text(
                f"✅ *Upload Successful!*\n\n📁 `{name}`\n\n🔗 `{download_url}`\n\n👇 Click below to download!",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            error_msg = response.json().get('message', 'Unknown error')
            await status.edit_text(f"❌ Upload failed!\n\nError: {error_msg}")
            
    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)[:150]}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(how_to, pattern="how"))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, handle_file))
    
    print("="*40)
    print("🚀 JORO FILE TO LINK BOT")
    print("="*40)
    print(f"✅ Bot Running!")
    print(f"📁 GitHub: {GITHUB_USERNAME}/{GITHUB_REPO}")
    print("="*40)
    app.run_polling()

if __name__ == '__main__':
    main()
