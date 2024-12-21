
# StokNinja

StokNinja, çeşitli e-ticaret sitelerindeki ürünlerin stok durumunu takip etmenize yardımcı olan bir Telegram botudur. Bir ürün linkini bota gönderin, ürün stokta olduğunda size bildirimde bulunsun.

![1734783714593](image/README/1734783714593.jpg)

## Özellikler

- Desteklenen sitelerdeki ürünlerin stok durumunu takip edin.
- Stok durumu değiştiğinde bildirim alın.
- Komutlarla takip edilen ürün listenizi yönetin.

## Gereksinimler

- Python 3.7+
- [BotFather](https://core.telegram.org/bots#botfather) üzerinden alınmış bir Telegram bot token'ı
- Desteklenen e-ticaret sitelerinde bir hesap

## Kurulum

1. Depoyu klonlayın:

   ```bash
   git clone https://github.com/yourusername/StokNinja.git
   cd StokNinja
   ```
2. Sanal bir ortam oluşturun ve etkinleştirin:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows için `venv\Scripts\activate` kullanın
   ```
3. Gerekli paketleri yükleyin:

   ```bash
   pip install -r requirements.txt
   ```
4. `.env.example` dosyasını `.env` olarak kopyalayın ve bilgilerinizi doldurun:

   ```bash
   cp .env.example .env
   ```

   `.env` dosyasını düzenleyin ve Telegram bot token'ınızı, bot kullanıcı adınızı ve test sayfası URL'sini ekleyin:

   ```env
   TELEGRAM_TOKEN="your_telegram_token_here"
   BOT_USERNAME="your_bot_username_here"
   TEST_PAGE_URL="your_test_page_url_here"
   ```

## Kullanım

1. Botu başlatın:

   ```bash
   python main.py
   ```
2. Telegram'ı açın ve botunuzla bir sohbet başlatın. Botla etkileşim kurmak için aşağıdaki komutları kullanın:

   - `/start` - Botu başlat ve hoş geldin mesajı al.
   - `/list` - Takip edilen ürünleri listele.
   - `/remove <numara>` - Takip listesinden bir ürünü numarasına göre kaldır.
3. Bir ürün linkini bota göndererek stok durumunu takip etmeye başlayın.

## Desteklenen Siteler

- Trendyol
- TrendyolMilla

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.
