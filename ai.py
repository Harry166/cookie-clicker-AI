from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

class CookieClickerBot:
    def __init__(self):
        try:
            print("Initializing bot...")
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.get("https://orteil.dashnet.org/cookieclicker/")
            time.sleep(5)
            
            self.initialize_game()
            self.last_save = time.time()
            self.last_ascend_check = time.time()
            print("Bot initialization complete")
        except Exception as e:
            print(f"Error initializing bot: {e}")
            if hasattr(self, 'driver'):
                self.driver.quit()
            raise

    def initialize_game(self):
        try:
            # Accept cookies if present
            try:
                self.driver.find_element(By.CLASS_NAME, "cc_btn_accept_all").click()
                time.sleep(2)
            except:
                pass

            # Set game preferences
            self.driver.execute_script("""
                Game.prefs.particles = 0;
                Game.prefs.numbers = 1;
                Game.prefs.autosave = 1;
                Game.prefs.fancy = 0;
                Game.volume = 0;
            """)
        except:
            pass

    def handle_sugar_lumps(self):
        try:
            self.driver.execute_script("""
                if (Game.canLumps() && Game.lumps > 0) {
                    if (Game.lumpRipeAge === Game.lumpMatureAge) {
                        Game.clickLump();
                    }
                    let priorities = ['Wizard tower', 'Temple', 'Farm'];
                    for (let building of priorities) {
                        if (Game.Objects[building].level < 1 && Game.lumps >= 1) {
                            Game.Objects[building].levelUp();
                        }
                    }
                }
            """)
        except:
            pass

    def handle_minigames(self):
        try:
            self.driver.execute_script("""
                // Grimoire
                if (Game.Objects['Wizard tower'].minigame) {
                    let grimoire = Game.Objects['Wizard tower'].minigame;
                    if (grimoire.magic >= grimoire.magicM) {
                        grimoire.castSpell(grimoire.spells['hand of fate']);
                    }
                }
                
                // Garden
                if (Game.Objects['Farm'].minigame) {
                    let garden = Game.Objects['Farm'].minigame;
                    for(let y=0; y<6; y++) {
                        for(let x=0; x<6; x++) {
                            if(garden.isTileUnlocked(x,y)) {
                                let tile = garden.getTile(x,y);
                                if(!tile[0]) {
                                    garden.seedSelected = garden.plants['bakerWheat'].id;
                                    garden.clickTile(x,y);
                                } else if(tile[0] && garden.plantsById[tile[0]-1].mature) {
                                    garden.harvest(x,y);
                                }
                            }
                        }
                    }
                }
            """)
        except:
            pass

    def check_ascension(self):
        try:
            self.driver.execute_script("""
                if (Game.prestige < 1 && Game.HowMuchPrestige(Game.cookiesReset) >= 1) {
                    Game.Ascend(1);
                } else if (Game.prestige > 0) {
                    let prestigeGain = Game.HowMuchPrestige(Game.cookiesReset) - Game.prestige;
                    if (prestigeGain > Game.prestige) {
                        Game.Ascend(1);
                    }
                }
            """)
        except:
            pass

    def strategic_purchase(self):
        try:
            self.driver.execute_script("""
                // Buy upgrades first
                Game.UpgradesInStore.forEach(function(upgrade) {
                    if (upgrade.canBuy() && !upgrade.bought && Game.cookies > upgrade.getPrice() * 1.5) {
                        upgrade.buy();
                    }
                });
                
                // Calculate best building based on ROI
                var bestBuilding = null;
                var bestROI = 0;
                Game.ObjectsById.forEach(function(building) {
                    if (Game.cookies >= building.getPrice()) {
                        var roi = building.storedCps / building.getPrice();
                        if (roi > bestROI) {
                            bestROI = roi;
                            bestBuilding = building;
                        }
                    }
                });
                
                if (bestBuilding && Game.cookies > bestBuilding.getPrice() * 2) {
                    bestBuilding.buy(1);
                }
            """)
        except Exception as e:
            print(f"Purchase error: {e}")

    def play(self):
        try:
            print("Bot starting to play...")
            while True:
                try:
                    # Click the cookie
                    cookie = self.driver.find_element(By.ID, "bigCookie")
                    cookie.click()
                    
                    # Every 30 seconds, check for upgrades
                    current_time = time.time()
                    if current_time - self.last_save >= 30:
                        self.strategic_purchase()
                        self.handle_minigames()
                        self.handle_sugar_lumps()
                        self.last_save = current_time
                    
                    # Every 5 minutes, check for ascension
                    if current_time - self.last_ascend_check >= 300:
                        self.check_ascension()
                        self.last_ascend_check = current_time
                    
                except Exception as e:
                    print(f"Error during play loop: {str(e)}")
                    time.sleep(1)
                
        except Exception as e:
            print(f"Fatal error in play loop: {str(e)}")
            if hasattr(self, 'driver'):
                self.driver.quit()

def main():
    try:
        bot = CookieClickerBot()
        bot.play()
    except Exception as e:
        print(f"Critical error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()