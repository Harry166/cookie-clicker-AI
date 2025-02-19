from flask import Flask, render_template, jsonify
import threading
import time

app = Flask(__name__)
bot = None
bot_thread = None
bot_status = "stopped"

@app.route('/')
def home():
    return render_template('index.html', status=bot_status)

@app.route('/start')
def start_bot():
    global bot, bot_thread, bot_status
    if bot_status == "stopped":
        try:
            from ai import CookieClickerBot  # Import here to avoid startup issues
            print("Attempting to start bot...")
            bot = CookieClickerBot()
            print("Bot instance created...")
            bot_thread = threading.Thread(target=bot.play)
            bot_thread.daemon = True
            bot_thread.start()
            bot_status = "running"
            return jsonify({"status": "success", "message": "Bot started successfully"})
        except Exception as e:
            print(f"Error starting bot: {str(e)}")
            return jsonify({"status": "error", "message": str(e)})
    return jsonify({"status": "error", "message": "Bot is already running"})

@app.route('/stop')
def stop_bot():
    global bot, bot_status
    if bot and bot_status == "running":
        try:
            bot.driver.quit()
            bot_status = "stopped"
            return jsonify({"status": "success", "message": "Bot stopped successfully"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    return jsonify({"status": "error", "message": "Bot is not running"})

@app.route('/status')
def get_status():
    global bot_status
    message = "Bot is running and clicking cookies" if bot_status == "running" else "Bot is stopped"
    return jsonify({
        "status": bot_status,
        "message": message,
        "timestamp": time.strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(debug=True)
