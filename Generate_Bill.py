# Replace this line (around line 8):
# target_folder = r"C:\Users\Pranav\Desktop\bill_app\Bookings"

# With this:
import tempfile
target_folder = os.path.join(tempfile.gettempdir(), 'Bookings')

# Replace logo path (around line 74):
# logo_path = "C:/Users/Pranav/Desktop/bill_app/static/logo.png"

# With this:
logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo.png')