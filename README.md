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
- [x] Show page number in every section (my items, search...), like '3/7'
- [ ] Think of a better feedback mechanism, based on 'reply to message'
- [ ] Less monolithic, more modules
- [ ] Translate statements to other languages
- [ ] Add screenshots
- [ ] Remove complex uuid key with an integer auto-increment
- [ ] ??