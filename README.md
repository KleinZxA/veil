# V.E.I.L.

A real-time web dashboard that displays Suricata IDS/IPS alerts and logs using Flask and Socket.IO. Built with modern web technologies for live monitoring of network security events.

## Features

- Real-time display of Suricata alerts and events
- Live-updating charts and statistics
- Critical alert highlighting and counting
- Traffic flow visualization
- Automated threat analysis logging
- Responsive design with dark mode support

## Prerequisites

- Python 3.11 or higher
- Suricata IDS/IPS installed and running
- Access to Suricata's eve.json log file
- npcap installed

## Project Structure

```
flask-suricata-dashboard/
├── src/
│   ├── services/
│   │   ├── __init__.py           # Package marker
│   │   └── suricata_client.py    # Suricata log reader
│   ├── static/
│   │   └── css/
│   │       └── styles.css
│   ├── templates/
│   │   └── index.html            # Dashboard template
│   ├── app.py                    # Flask application
│   └── sockets.py                # Socket.IO event handlers
├── requirements.txt
└── README.md
```

## Installation

> [!NOTE]
> Currently only Working in Windows.

1. Clone the repository:
```powershell
git clone <repository-url>
cd flask-suricata-dashboard
```

2. Create and activate a virtual environment:
```powershell
python -m venv <Project Directory>
```

3. Install dependencies:
```powershell
<Project DIR>/bin/pip install -r requirements.txt
```

4. Configure Suricata path:
```powershell
$env:SURICATA_EVE_PATH="C:\Program Files\Suricata\log\eve.json"
# Or edit src/config.py to set the path
```

## Running the Application

1. Start the Flask server:
```powershell
cd src
<Project DIR>/bin/python ../app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Configuration
- Configure Your Suricata Installation: https://docs.suricata.io/en/latest/quickstart.html

The application can be configured through environment variables or `config.py`:

- `SURICATA_EVE_PATH`: Path to Suricata's eve.json file
- `SECRET_KEY`: Flask secret key for session security
- `DEBUG`: Enable/disable debug mode (default: True)

## Troubleshooting

Common issues and solutions:

1. **No events showing up:**
   - Verify Suricata is running and writing to eve.json
   - Check the eve.json path in your configuration
   - Look for error messages in the Flask console

2. **Socket.IO connection errors:**
   - Ensure you're using a compatible browser
   - Check browser console for specific error messages
   - Verify eventlet is installed and working

3. **Permission errors:**
   - Run Suricata as Administrator
   - Ensure your user has read access to eve.json
   - Run Flask with appropriate permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Flask and Socket.IO
- Uses Tailwind CSS for styling
- Inspired by modern security dashboards
