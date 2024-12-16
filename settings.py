from dotenv import load_dotenv

class SettingsManager:
    
    def __init__(self):
        load_dotenv()
    
    # Updates a .env variable's value with a new one
    def set_env(self, variable, value):
        
        # Reads the .env file
        with open(".env", "r") as file:
            lines = file.readlines()
        
        # Writes the update in the file
        with open(".env", "w") as file:
            updated = False
            
            # Rewrites all lines updating the one to update
            for line in lines:
                if line.startswith(variable):
                    file.write(f"{variable}={value}\n")
                    updated = True
                else:
                    file.write(line)
            
            # If didn't find variable, creates it
            if not updated:
                file.write(f"{variable}={value}\n")

        # Reloads .env variables
        load_dotenv(".env", override=True)
    
    def edit_yt_api_key(self, key):
        self.set_env("YT_API_KEY", key)