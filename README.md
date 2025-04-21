# 🚀 Interactive PySpark Event Simulator

Welcome to the **Interactive PySpark Event Simulator**, a hands‑on toolkit for exploring real‑time stream processing with Apache PySpark. Generate events in your browser, stream them into Spark, and watch aggregations (sum, average, min, max) update live!

---

## 📁 Project Structure

- **`event_server.py`**  
  - Starts an HTTP server on port **8080**  
  - Receives incoming events and writes each event to the `input_stream/` folder as a file

- **`spark_stream.py`**  
  - A simple PySpark streaming job  
  - Reads new files from `input_stream/`, applies windowed aggregations, and writes results to `output/`

- **`simulator_page.html`**  
  - A static HTML page you open in your browser  
  - Lets you tweak event frequency and send events to `event_server.py`

---

## 🛠️ Prerequisites

1. **Python** 3.8+  
2. **Apache Spark** installed and on your `PATH`  
3. **Pipenv** for dependency management  
4. Port **8080** must be free on your machine

---

## 🚀 Quick Start

1. **Clone the repo**  
   ```bash
   git clone <your‑repo‑url>
   cd <your‑repo‑dir>

2. **Install Dependencies**
    ```bash
    pipenv install
   ```

3. **Install the event server**
    ```bash
    pipenv run python event_server.py
    ```
- Listens on http://localhost:8080/
- Creates files under input_stream/ for each event

4. **Start the Spark Stream**

    ```bash
    pipenv run python spark_stream.py
    ```
- Monitors input_stream/ for new files 
- Outputs aggregated results to output/

5. **Open the Simulator Page**

- Simply double‑click or open simulator_page.html in your browser 
- Adjust “Event frequency (seconds)” and click Start

⚠️ Make sure both Python processes (steps 3 & 4) are running first!

---
### 🧹 Cleanup / Reset

If you are having issues or you’d like to clear out old data or free up disk space:

```bash
rm -rf input_stream/ output/ checkpoint/
```

---
### 🙌 Have Fun!
Feel free to:

- Change the window size or aggregation type in spark_stream.py 
- Tweak the server logic in event_server.py 
- Style or extend simulator_page.html with new controls 

This project is all about experimentation—break things, fix them, and spark new ideas! 🔥