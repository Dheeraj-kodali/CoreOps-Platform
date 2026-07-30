# 🛡️ Administrator User Guide — Temple Visitor System

This guide is intended exclusively for Temple Executives and Administrators.

---

## 🔒 Security PIN Management
- **Default PIN**: `1234`
- **Brute-Force Lockout**: 5 consecutive incorrect PIN entries will lock out access for 5 minutes.
- **Changing PIN**:
  1. Open ⚙️ **Settings** (enter active PIN).
  2. Tap **Security PIN Settings**.
  3. Enter Current PIN and New PIN, then tap **Update PIN**.

---

## 📝 Communication Template Management
1. Tap **Communication Templates** in Settings.
2. Select **Check-In Template** or **Check-Out Template**.
3. Edit text in the multi-line editor.
4. Tap placeholder chips (`{{name}}`, `{{phone}}`, `{{village}}`, `{{time}}`, `{{activities}}`, etc.) to insert dynamic tags.
5. Review real-time rendering in **Live WhatsApp Preview**.
6. Tap **SAVE TEMPLATES**.

---

## 📅 Today's Activities & Festivals
1. **Activities**: Add daily seva hours, annadanam schedules, or notices.
2. **Festivals**: Toggle upcoming brahmotsavam or festival announcements.
3. Active items are automatically substituted into `{{activities}}` and `{{festival}}` message placeholders.

---

## 🧪 Gateway Testing
1. Tap **Communication Gateway Test**.
2. Enter a test mobile number.
3. Select template to test and tap **SEND TEST MESSAGE**.
4. Dispatches test payload without altering visitor counts or report metrics.
