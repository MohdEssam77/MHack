# MHack

Hackathon project

## Project Structure

MHack/ .gitignore README.md MHack/ .gitignore README.md UdS OP/ .gitignore desktop_app.py main.py README.md requirements.txt some prompt examples.txt app/ config/ webo/ app.py main.py vid.mp4

## Setup and Installation

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/sigmabotech/MHack.git
   cd MHack
   ```

2. Navigate to the `UdS OP` directory:

   ```sh
   cd MHack/UdS\ OP
   ```

3. Install the required Python packages:

   ```sh
   pip install -r requirements.txt
   ```

### Running the Application

#### Desktop Application

To run the desktop application, execute the following command:

```sh
python desktop_app.py

#### Web Application

To run the web application, navigate to the webo directory and execute the following command:

Directory Structure
MHack/: Root directory containing project files.
MHack/UdS OP/: Contains the desktop application and related files.
MHack/webo/: Contains the web application and related files.

APIs, Frameworks, and Tools Utilized
APIs
Example API 1: Used for fetching data from an external source.
Example API 2: Used for authentication and user management.
Frameworks
Flask: A micro web framework used for building the web application.
Tkinter: A standard GUI library for Python used for building the desktop application.
Tools
Git: Version control system used for tracking changes in the source code.
Visual Studio Code: Code editor used for development.
Postman: Tool used for testing APIs.

Technical Documentation
Desktop Application
The desktop application is built using Python and Tkinter. It provides a graphical user interface for users to interact with the application.

Entry Point: desktop_app.py
Dependencies: Listed in requirements.txt
Web Application
The web application is built using Python and Flask. It provides a web-based interface for users to interact with the application.

Entry Point: app.py (located in the webo directory)
Dependencies: Listed in requirements.txt
Additional Information
For more details, refer to the individual README.md files in the respective directories:

MHack/UdS OP/README.md
MHack/webo/README.md