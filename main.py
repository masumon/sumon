import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ui.ui_main import main
from db import initialize_db  # ডাটাবেস ইনিশিয়ালাইজ করার ফাংশন ইমপোর্ট

if __name__ == "__main__":
    initialize_db()   # ডাটাবেস ও টেবিল তৈরি হবে
    main()            # UI চালু হবে
