# Magento Config Tool 🛠️

A **Python terminal-based Magento configuration management tool** that allows users to **search, edit, and manage** Magento's `core_config_data` table using a **curses-based CLI UI**.

## 🚀 Features
✅ **Search by Path** – Find Magento configurations by their `path`.  
✅ **View All Records** – Paginated list of `core_config_data` entries.  
✅ **Edit Configuration by ID** – Modify values in `core_config_data`.  
✅ **View Database Configuration** – Fetch DB settings from `env.php`.  
✅ **Curses-Based UI** – Keyboard-friendly navigation.  

---

## 📦 Installation

### 1️⃣ **Install via `pip` (from PyPI)**
Once published, you can install it via:
```sh
pip3 install magento-config-tool
```
### 1️⃣ **Install via `pip` (from Git)**
```sh
pip3 install https://github.com/Genaker/magento-config-tool
```

### 2️⃣ **Install from Source**
If installing from a local clone:
```sh
git clone https://github.com/yourusername/magento-config-tool.git
cd magento-config-tool
pip3 install --editable .
```

---

## 🛠 **Usage**

### **Run the tool**
After installation, run:
```sh
mage-conf
```

### **Keyboard Shortcuts**
- **Arrow Keys (`↑` `↓`)** – Navigate the menu.
- **Enter (`↵`)** – Select an option.
- **ESC (`⎋`)** – Exit to the main menu.

---

## 📂 **Commands & Functionality**
| Feature               | Description |
|----------------------|------------|
| **Search by Path** | Search for records in `core_config_data` by `path`. |
| **Show All Records** | Displays a paginated list of all configuration records. |
| **Edit by ID** | Edit any configuration value by entering its ID. |
| **View DB Config** | Reads and displays Magento's DB credentials from `env.php`. |
| **Exit** | Quit the application (ESC key). |

---

## ⚙️ **How It Works**
### **1️⃣ Read Magento DB Configuration**
The tool automatically fetches database credentials from:
```
app/etc/env.php
```
### **2️⃣ Connect to Magento Database**
It connects using `SQLAlchemy` and `MySQL Connector`.

### **3️⃣ Perform Queries on `core_config_data`**
- Searches by **path**
- Lists all records with **pagination**
- Allows **editing** values

---

## 🏗 **Development**
### **Clone and Run Locally**
```sh
git clone https://github.com/yourusername/magento-config-tool.git
cd magento-config-tool
pip3 install --editable .
mage-conf
```

### **Build and Publish to PyPI**
```sh
python3 setup.py sdist bdist_wheel
pip3 install twine
rm -rf build/ dist/ *.egg-info
python3 -m build
twine upload dist/*
```

# Reinstall
```sh
pip3 uninstall magento-config-tool
## or
pip install --upgrade --force-reinstall magento-config-tool
```

---

## 📝 **License**
This project is **open-source** and licensed under the **MIT License**.

---

### 👨‍💻 **Contributions & Support**
💡 Have ideas or found an issue?  
Feel free to **open an issue** or **submit a pull request** on GitHub!  

🔗 **GitHub Repository**: [yourusername/magento-config-tool](https://github.com/yourusername/magento-config-tool)

---
**🚀 Now you can manage Magento configs right from your terminal using Python! 🔥**
