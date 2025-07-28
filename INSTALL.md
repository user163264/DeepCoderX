# DeepCoderX Installation Guide

This guide provides instructions for setting up and running the DeepCoderX application. 

---

## For Testers (Running the Packaged Application)

These instructions are for running the pre-packaged, standalone version of DeepCoderX. You do **not** need to have Python or any libraries installed to run this version.

### Prerequisites

- You will be given a `.zip` file (e.g., `DeepCoderX-macOS.zip` or `DeepCoderX-Linux.zip`).
- You will also be given the local AI model file: `qwen2.5-coder-1.5b-instruct-q8_0.gguf`.

### Instructions

1.  **Unzip the Application**: Unzip the `.zip` file you received. This will create a folder, likely named `dist` or `DeepCoderX`.

2.  **Place the Model File**: Find the AI model file (`qwen2.5-coder-1.5b-instruct-q8_0.gguf`) and place it **inside the same folder** as the `DeepCoderX` executable.

    Your folder should look like this:
    ```
    DeepCoderX/
    ├── DeepCoderX  (the application)
    └── qwen2.5-coder-1.5b-instruct-q8_0.gguf (the model)
    ```

3.  **Run the Application**:

    *   **On macOS**:
        *   The first time you run the application, you may see a security warning ("DeepCoderX can't be opened because it is from an unidentified developer.").
        *   To bypass this, **right-click** the `DeepCoderX` application and select **Open**. You will only need to do this once.

    *   **On Ubuntu/Linux**:
        *   Open a terminal and navigate to the folder containing the application.
        *   You may need to make the application executable. Run the following command:
            ```bash
            chmod +x DeepCoderX
            ```
        *   Now, run the application from your terminal:
            ```bash
            ./DeepCoderX
            ```

4.  **Add Your API Key**: The first time you run the application, it will create a `.env` file in the same directory. Open this file and add your DeepSeek API key to enable the `@deepseek` commands.

---

## For Developers (Building from Source)

These instructions are for developers who want to build the application from the source code. This is necessary if you are creating a new distributable package for a different operating system (e.g., building the Linux version on an Ubuntu machine).

### Prerequisites

- Python 3.10 or higher
- `git` (for cloning the repository)

### Instructions

1.  **Clone the Repository**:
    ```bash
    git clone <your-repository-url>
    cd DeepCoderX
    ```

2.  **Create and Activate a Virtual Environment**:
    ```bash
    python3 -m venv VENV
    source VENV/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Your Environment**:
    *   The application will automatically create a `.env` file on the first run.
    *   Open the `.env` file and add your `DEEPSEEK_API_KEY`.
    *   Ensure the `LOCAL_MODEL_PATH` in `.env` or `config.py` points to the correct location of your `.gguf` model file.

5.  **Run the Application in Development**:
    ```bash
    python app.py
    ```

6.  **Build the Standalone Executable**:
    *   Make sure you have `PyInstaller` installed (`pip install pyinstaller`).
    *   Run the build command from the root of the project directory:
        ```bash
        pyinstaller --onefile --name DeepCoderX app.py
        ```
    *   The final executable will be located in the `dist/` folder.
