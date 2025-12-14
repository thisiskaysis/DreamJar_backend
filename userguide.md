## Step-by-Step Usage Guide

- [Step-by-Step Usage Guide](#step-by-step-usage-guide)
  - [1️⃣ Register a New Parent Account](#1️⃣-register-a-new-parent-account)
  - [2️⃣ Create a Child Profile](#2️⃣-create-a-child-profile)
  - [3️⃣ Create a Campaign (DreamJar)](#3️⃣-create-a-campaign-dreamjar)
  - [4️⃣ Make a Donation](#4️⃣-make-a-donation)
  - [5️⃣ Browse Public Campaigns](#5️⃣-browse-public-campaigns)


### 1️⃣ Register a New Parent Account

**POST** `/parents/`

```json
{
  "username": "bruce_wayne",
  "email": "batman@batcave.com",
  "password": "batboy123"
}
```

**Response (201 Created):**

```json
{
  "user": {
    "id": 1,
    "username": "bruce_wayne",
    "email": "batman@batcave.com"
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

The API immediately returns JWT tokens for authentication.

---

### 2️⃣ Create a Child Profile

**POST** `/parents/1/children/`

**Headers:**
```
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "name": "Emma",
  "date_of_birth": "2015-03-15",
  "profile_picture": "https://example.com/emma.jpg"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "name": "Emma",
  "date_of_birth": "2015-03-15",
  "profile_picture": "https://example.com/emma.jpg",
  "parent": 1
}
```

---

### 3️⃣ Create a Campaign (DreamJar)

**POST** `/children/1/campaigns/`

**Headers:**
```
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "Emma's Soccer Dreams",
  "description": "Help Emma join the local soccer team and get proper equipment",
  "goal": 500,
  "image": "https://example.com/soccer.jpg",
  "category": "sports",
  "has_deadline": true,
  "deadline": "2025-03-01T00:00:00Z",
  "is_open": true
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "title": "Emma's Soccer Dreams",
  "description": "Help Emma join the local soccer team and get proper equipment",
  "goal": 500,
  "image": "https://example.com/soccer.jpg",
  "category": "sports",
  "has_deadline": true,
  "deadline": "2025-03-01T00:00:00Z",
  "is_open": true,
  "child": 1,
  "date_created": "2024-12-14T10:30:00Z"
}
```

---

### 4️⃣ Make a Donation

**Authenticated Donation:**

**POST** `/campaigns/1/donations/`

**Headers:**
```
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "amount": 50,
  "comment": "Good luck Emma!",
  "anonymous": false
}
```

**Anonymous Donation (No Account):**

**POST** `/campaigns/1/donations/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**

```json
{
  "amount": 25,
  "comment": "Best wishes!",
  "anonymous": true,
  "donor_name": "A Friend",
  "donor_email": "friend@example.com"
}
```

---

### 5️⃣ Browse Public Campaigns

**GET** `/campaigns/`

**No authentication required**

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "child_name": "Emma",
    "title": "Emma's Soccer Dreams",
    "description": "Help Emma join the local soccer team...",
    "goal": 500,
    "total_raised": 150,
    "donation_count": 6,
    "percentage_raised": 30.0,
    "image": "https://example.com/soccer.jpg",
    "category": "sports",
    "is_open": true,
    "is_expired": false,
    "seconds_remaining": 5184000,
    "date_created": "2024-12-14T10:30:00Z"
  }
]
```

**Note:** Only the child's first name is shown publicly for privacy.

---

**Built with ❤️ for children's dreams**