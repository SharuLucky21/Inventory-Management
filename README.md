
# 📦 Inventory Management System (IMS)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A **role-based web application** built with **Flask + SQLite + Bootstrap** to manage products, suppliers, stock transactions, and low-stock alerts.  
This project helps organizations keep track of inventory, streamline supplier management, and generate quick insights through dashboards.  

---

## ✨ Features
- 🔑 **User Authentication & Roles** (Admin, Manager, Staff)  
- 📦 **Product Management** (CRUD operations, search, filters)  
- 🏢 **Supplier Management** (CRUD operations, contact info)  
- 🔄 **Stock Transactions** (in/out with live stock updates)  
- ⚠️ **Low Stock Alerts** (dashboard notifications when stock falls below reorder point)  
- 📊 **Dashboard** (total products, low/out-of-stock items, recent transactions)  
- 📥 **CSV Import & Export** (bulk product upload and download)  

---

## 🛠️ Tech Stack
- **Backend:** Flask (Python), SQLAlchemy  
- **Frontend:** HTML, Bootstrap 5, Jinja2  
- **Database:** SQLite (can be swapped with MySQL/PostgreSQL)  
- **Other:** Pandas (CSV import/export), Flask-WTF (forms), Werkzeug (password hashing)  

---

## ⚡ Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/inventory-management-system.git
   cd inventory-management-system
