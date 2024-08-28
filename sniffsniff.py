from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import json
import os
import psutil  # Importing psutil for checking active processes

PATH_NAME = r"C:\Users\CPSCSTUDENT1\LaunchBox\Emulators\RetroArch"
FILE_NAME = "content_history.lpl"
FULL_PATH = os.path.join(PATH_NAME, FILE_NAME)

def is_process_running(process_name):
    """Check if there is any running process that contains the given name."""
    for proc in psutil.process_iter(attrs=['name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

class GameLaunchHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(FILE_NAME):
            with open(event.src_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            most_recent_game = data['items'][0]
            if most_recent_game['path'] == "read_filepath":
                return

            game_name = os.path.basename(most_recent_game['path'])
            print(f"Most Recently Launched Game: {game_name}")

            data['items'][0]['path'] = "read_filepath"
            with open(event.src_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)

if __name__ == "__main__":
    event_handler = GameLaunchHandler()
    observer = Observer()
    observer.schedule(event_handler, PATH_NAME, recursive=False)
    observer.start()

    print("Monitoring for game launches...")
    retroarch_running = False

    try:
        while True:
            time.sleep(1)
            if is_process_running("retroarch"):
                retroarch_running = True
            elif retroarch_running and not is_process_running("retroarch"):
                print("Game Ended")
                retroarch_running = False
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
