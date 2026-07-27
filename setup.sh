cat > setup.sh << 'EOF'
#!/bin/bash

# FaceToJoystick Setup Script
echo "🎮 Setting up FaceToJoystick..."

if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  This setup script is for Linux only."
    exit 1
fi

echo "📦 Updating package manager..."
sudo apt-get update -y

echo "📚 Installing system libraries..."
sudo apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libevdev2 \
    libsm6 \
    libxext6 \
    libxrender-dev

echo "🐍 Installing Python packages..."
pip install -r requirements.txt

echo "✅ Setup complete! You can now run: python main.py"
EOF
chmod +x setup.sh