# UniPi Marketplace 📚🎓
Telegram bot where UniPi's students can buy and sell used books, notes and so on.

## How to
```bash
git clone https://github.com/xLinkOut/unipi-marketplace
cd unipi-marketplace
python3 -m venv venv     # (optional)
source venv/bin/activate # (optional)
pip install -r requirements.txt
cd src/
cp .env.example .env
# Fill .env file with your data as written below
python Marketplace.py
```

### Config .env
* **API_TOKEN**: token given to you by [@BotFather](https://t.me/botfather)
* **DB_FILE**: name for the database file (empty for _Database.db_)
* **LANG_FILE**: two-word abbreviation of a language (IT, EN, XY...) matching file into src/lang/XY.lang
* **ADMIN_CHAT_ID**: chat ID of the admin (send a message to the bot while debug is True and get it from the console)
* **IMG_NOT_AVAILABLE**: file ID of the 'image not available' file (send the image to the bot while 'debug' is True and get it from the console)
* **DEBUG**: set this to True to activate verbose mode, False otherwise

## Future
- [x] Move `feedback` stuffs into a separate module
- [x] Move `chat action` into a separate module
- [x] Move `env config` into a separate, global, module
- [x] `build_item_caption` is used by several modules, should be moved in a ~~`Utility.py`~~ `Misc.py`
- [ ] Clean functions name, deleting `buy_*`, `sell_*`...
- [ ] Clean `import` sections for every file
- [ ] Organize `statements` in relevant sections
- [ ] ^ and load in each module only those that are needed
- [ ] Think of a better feedback mechanism, based on `reply to message`
- [ ] Remove test functions (`add_test`, `set_section`)
