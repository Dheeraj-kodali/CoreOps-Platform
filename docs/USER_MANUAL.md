# User Manual - v2.0
## Temple Visitor Management System Enterprise Edition

### 1. Overview for Temple Staff & Volunteers
This guide explains how volunteers and temple managers operate the mobile application and administrative web tools for offline devotee registration, visitor check-in, search, broadcast messaging, and dashboard monitoring.

---

### 2. Devotee Registration (Offline Edge Terminal)

1. **Launch App**: Open the Flutter mobile application on an Android or iOS tablet/phone terminal.
2. **Offline Registration**: Navigate to **Register Devotee**.
3. **Fill Form Fields**:
   - Devotee Full Name (Required)
   - Mobile Number (Required)
   - Village / City (Required)
   - Visit Purpose (e.g. Special Darshan, Seva, Annadanam)
4. **Submit**: Tap **Register**.
5. **Instant Local Storage**: The record is instantly saved to local SQLite storage and queued in local outbox events without waiting for internet connectivity.

---

### 3. Master Devotee Directory & Search

1. Navigate to **Devotee Search / Directory**.
2. Input devotee name, mobile number, or village in the search bar.
3. System returns matching historical devotee profiles alongside total visit counts (`total_visits`) and first/last visit dates.

---

### 4. Broadcast Messaging (Festival & Event Notifications)

1. Navigate to **Broadcast Center**.
2. Select target **Audience Filter**:
   - `ALL_DEVOTEES`: Send to all historical devotees in the temple database.
   - `VILLAGE_MATCH`: Target devotees from a specific village (e.g. "Vijayawada").
   - `DATE_RANGE`: Target devotees who visited within specific dates.
   - `REPEAT_VISITORS`: Target devotees with more than N visits.
3. Select a pre-defined **Message Template** or enter a custom festival announcement.
4. Review recipient count and tap **Confirm & Dispatch Broadcast**.

---

### 5. Owner Dashboard & System Visibility

1. Open the **Owner Dashboard**.
2. View real-time cards:
   - **Live Visitors**: Devotees currently on premises.
   - **Today's & Monthly Totals**: Attendance trends.
   - **First-Time vs Repeat Ratio**: Devotee loyalty analytics.
   - **Sync Status**: Pending outbox items and last sync timestamp.
   - **Communication Health**: Broadcast delivery success rate.
