#!/usr/bin/env python
"""
ClauseWise Setup Script
Automates installation and configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(step, text):
    """Print step information"""
    print(f"[{step}] {text}")

def run_command(command, description):
    """Run shell command with error handling"""
    print(f"\n→ {description}...")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {description} failed")
        print(f"  {str(e)}")
        return False

def main():
    """Main setup function"""
    
    print_header("ClauseWise Setup Script")
    print("This script will set up ClauseWise on your system.\n")
    
    # Check Python version
    print_step("1", "Checking Python version")
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"✗ Python 3.8+ is required. You have {python_version.major}.{python_version.minor}")
        sys.exit(1)
    print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Check if virtual environment exists
    print_step("2", "Checking virtual environment")
    venv_path = Path("venv")
    if not venv_path.exists():
        print("→ Virtual environment not found. Creating one...")
        if not run_command(f"{sys.executable} -m venv venv", "Create virtual environment"):
            sys.exit(1)
    else:
        print("✓ Virtual environment already exists")
    
    # Determine pip path
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Upgrade pip
    print_step("3", "Upgrading pip")
    run_command(f"{pip_path} install --upgrade pip", "Upgrade pip")
    
    # Install requirements
    print_step("4", "Installing dependencies")
    if not run_command(f"{pip_path} install -r requirements.txt", "Install requirements"):
        print("\n⚠️  Some packages may have failed to install.")
        print("   You can try installing them manually:")
        print(f"   {pip_path} install -r requirements.txt")
    
    # Download spaCy model (optional)
    print_step("5", "Downloading spaCy model (optional)")
    response = input("Do you want to download spaCy English model? (y/n): ").lower()
    if response == 'y':
        run_command(f"{python_path} -m spacy download en_core_web_sm", "Download spaCy model")
    else:
        print("⊙ Skipped spaCy model download")
    
    # Create .env file
    print_step("6", "Setting up environment variables")
    env_path = Path(".env")
    if not env_path.exists():
        response = input("Do you want to create .env file for IBM watsonx.ai? (y/n): ").lower()
        if response == 'y':
            print("\n→ Creating .env file...")
            api_key = input("Enter your IBM watsonx API key (or press Enter to skip): ").strip()
            project_id = input("Enter your IBM watsonx Project ID (or press Enter to skip): ").strip()
            
            with open(".env", "w") as f:
                f.write(f"IBM_WATSONX_API_KEY={api_key}\n")
                f.write(f"IBM_WATSONX_PROJECT_ID={project_id}\n")
                f.write("DEBUG=False\n")
                f.write("MAX_FILE_SIZE=10\n")
            
            print("✓ .env file created")
            
            if not api_key or not project_id:
                print("\n⚠️  Note: No IBM credentials provided.")
                print("   The application will use HuggingFace models instead.")
        else:
            print("⊙ Skipped .env file creation")
            print("   The application will use HuggingFace models by default.")
    else:
        print("✓ .env file already exists")
    
    # Create Streamlit config
    print_step("7", "Creating Streamlit configuration")
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    config_path = streamlit_dir / "config.toml"
    if not config_path.exists():
        with open(config_path, "w") as f:
            f.write("""[theme]
primaryColor="#1f77b4"
backgroundColor="#ffffff"
secondaryBackgroundColor="#f0f2f6"
textColor="#262730"

[server]
maxUploadSize=10
enableXsrfProtection=true
headless=false

[browser]
gatherUsageStats=false
""")
        print("✓ Streamlit configuration created")
    else:
        print("✓ Streamlit configuration already exists")
    
    # Final summary
    print_header("Setup Complete!")
    print("✓ ClauseWise is ready to use!\n")
    print("To start the application, run:")
    print("  → On Windows:")
    print("     venv\\Scripts\\activate")
    print("     streamlit run app.py")
    print("\n  → On macOS/Linux:")
    print("     source venv/bin/activate")
    print("     streamlit run app.py")
    print("\nThe application will open at: http://localhost:8501")
    print("\nFor help, see README.md or visit the documentation.")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        sys.exit(1)