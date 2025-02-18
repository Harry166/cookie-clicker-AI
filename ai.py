from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import sys
import os
import platform
import tempfile
import base64
import requests
import zipfile
import io
import re
from selenium.webdriver.chrome.service import Service

class CookieClickerBot:
    def __init__(self):
        try:
            print("Initializing bot...")
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--headless=new')  # Updated headless mode
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-extensions')
            options.add_argument('--window-size=1920,1080')
            options.add_argument(f'--user-data-dir=/tmp/chrome-data-{time.time()}')
            
            if 'RENDER' in os.environ:
                print("Running on Render, using system Chrome")
                options.binary_location = '/usr/bin/google-chrome-stable'
            
            print("Starting Chrome...")
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)  # Add timeout
            print("Chrome started, loading Cookie Clicker...")
            self.driver.get("https://orteil.dashnet.org/cookieclicker/")
            time.sleep(5)
            
            self.initialize_game()
            self.last_save = time.time()
            self.last_ascend_check = time.time()
            self.last_sugar_lump_check = time.time()
            self.last_wrinkler_check = time.time()
            print("Bot initialization complete")
        except Exception as e:
            print(f"Detailed error in bot initialization: {str(e)}")
            if hasattr(self, 'driver'):
                self.driver.quit()
            raise

    def get_chrome_version(self):
        system = platform.system().lower()
        try:
            if system == 'linux':
                chrome_version = os.popen('google-chrome --version').read().strip()
            elif system == 'darwin':  # macOS
                chrome_version = os.popen('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --version').read().strip()
            else:  # Windows
                chrome_version = os.popen('reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version').read()
                chrome_version = re.search(r'version\s+REG_SZ\s+([\d.]+)', chrome_version).group(1)
            
            # Extract version number
            version = re.search(r'[\d.]+', chrome_version).group(0)
            major_version = version.split('.')[0]
            return major_version
        except Exception as e:
            print(f"Error getting Chrome version: {e}")
            return None

    def setup_chromedriver(self):
        try:
            system = platform.system().lower()
            temp_dir = tempfile.gettempdir()
            driver_path = os.path.join(temp_dir, 'chromedriver')
            
            if system == 'windows':
                driver_path += '.exe'
                platform_name = 'win32'
            elif system == 'darwin':  # macOS
                platform_name = 'mac-x64'  # Updated platform name
            else:  # Linux
                platform_name = 'linux64'
            
            # Get Chrome version and matching ChromeDriver version
            chrome_version = self.get_chrome_version()
            if not chrome_version:
                raise Exception("Could not determine Chrome version")
                
            # Get the ChromeDriver version
            version_url = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{chrome_version}"
            response = requests.get(version_url)
            if response.status_code != 200:
                raise Exception(f"Could not get ChromeDriver version: {response.status_code}")
            version = response.text.strip()
            
            # Updated download URL format
            download_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{version}/linux64/chromedriver-linux64.zip"
            
            print(f"Downloading ChromeDriver from: {download_url}")
            response = requests.get(download_url)
            if response.status_code != 200:
                raise Exception(f"Could not download ChromeDriver: {response.status_code}")
            
            # Extract ChromeDriver
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                if system == 'windows':
                    zip_file.extract('chromedriver.exe', temp_dir)
                else:
                    zip_file.extract('chromedriver-linux64/chromedriver', temp_dir)
                    os.rename(
                        os.path.join(temp_dir, 'chromedriver-linux64/chromedriver'),
                        os.path.join(temp_dir, 'chromedriver')
                    )
                    os.rmdir(os.path.join(temp_dir, 'chromedriver-linux64'))
            
            # Make executable on Unix systems
            if system != 'windows':
                os.chmod(driver_path, 0o755)
            
            self.service = Service(driver_path)
            
        except Exception as e:
            print(f"Error setting up ChromeDriver: {e}")
            raise

    def initialize_game(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "cc_btn_accept_all").click()
            time.sleep(2)
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
                // Auto-harvest ripe sugar lumps
                if (Game.canLumps() && Game.lumps > 0) {
                    if (Game.lumpRipeAge === Game.lumpMatureAge) {
                        Game.clickLump();
                    }
                    
                    // Prioritize important building levels
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

    def handle_wrinklers(self):
        try:
            self.driver.execute_script("""
                // Pop wrinklers when they're full
                Game.wrinklers.forEach(function(wrinkler) {
                    if (wrinkler.sucked > Game.cookiesPs * 18000) { // Pop after 5 hours worth
                        wrinkler.hp = 0;
                    }
                });
            """)
        except:
            pass

    def handle_krumblor(self):
        try:
            self.driver.execute_script("""
                // Train dragon if available
                if (Game.Has('A crumbly egg')) {
                    if (!Game.dragonLevel || Game.dragonLevel < Game.dragonLevels.length-1) {
                        Game.UpgradeDragon();
                    }
                    // Set aura to best options
                    if (Game.dragonLevel >= 5) {
                        Game.SelectDragonAura(15); // Radiant Appetite
                    }
                    if (Game.dragonLevel >= 23) {
                        Game.SelectDragonAura(1, 1); // Breath of Milk as secondary
                    }
                }
            """)
        except:
            pass

    def handle_santa(self):
        try:
            self.driver.execute_script("""
                // Upgrade Santa if available
                if (Game.Has('A festive hat')) {
                    if (Game.santaLevel < 14) {
                        Game.UpgradeSanta();
                    }
                }
            """)
        except:
            pass

    def handle_minigames(self):
        try:
            self.driver.execute_script("""
                // Stock Market (Bank minigame)
                if (Game.Objects['Bank'].minigame) {
                    let market = Game.Objects['Bank'].minigame;
                    let goods = market.goods;
                    
                    // Process each stock
                    for (let i = 0; i < goods.length; i++) {
                        let stock = goods[i];
                        let price = stock.val;
                        let prevPrice = stock.vals[stock.vals.length-2] || price;
                        let delta = price - prevPrice;
                        
                        // Buy low strategy
                        if (price < stock.basePrice * 0.5 && market.getGoodMaxStock(i) - stock.stock > 0) {
                            // Buy when price is less than 50% of base value
                            let amount = Math.min(
                                market.getGoodMaxStock(i) - stock.stock,
                                Math.floor(market.profit / price)
                            );
                            if (amount > 0) market.buyGood(i, amount);
                        }
                        // Sell high strategy
                        else if (price > stock.basePrice * 1.5 && stock.stock > 0) {
                            // Sell when price is more than 150% of base value
                            market.sellGood(i, stock.stock);
                        }
                        
                        // Emergency sell if crashing hard
                        if (delta < -3 && stock.stock > 0 && price > stock.basePrice) {
                            market.sellGood(i, stock.stock);
                        }
                        
                        // Loan management
                        if (market.brokers >= 1) {
                            // Take loans when profitable
                            if (market.profit > market.loanLimit * 2) {
                                for (let i = 0; i < 3; i++) {
                                    if (market.takeLoan(i)) break;
                                }
                            }
                            // Repay loans when possible
                            for (let i = 0; i < 3; i++) {
                                market.repayLoan(i);
                            }
                        }
                    }
                }
                
                // Grimoire
                if (Game.Objects['Wizard tower'].minigame) {
                    var grimoire = Game.Objects['Wizard tower'].minigame;
                    if (grimoire.magic >= grimoire.magicM) {
                        grimoire.castSpell(grimoire.spells['hand of fate']);
                    }
                }
                
                // Garden
                if (Game.Objects['Farm'].minigame) {
                    var garden = Game.Objects['Farm'].minigame;
                    // Plant optimization strategy
                    for(let y=0; y<6; y++) {
                        for(let x=0; x<6; x++) {
                            if(garden.isTileUnlocked(x,y)) {
                                let tile = garden.getTile(x,y);
                                if(!tile[0]) {
                                    // Plant Baker's Wheat for early game
                                    garden.seedSelected = garden.plants['bakerWheat'].id;
                                    garden.clickTile(x,y);
                                } else if(tile[0] && garden.plantsById[tile[0]-1].mature) {
                                    garden.harvest(x,y);
                                }
                            }
                        }
                    }
                }
                
                // Pantheon
                if (Game.Objects['Temple'].minigame) {
                    var pantheon = Game.Objects['Temple'].minigame;
                    // Optimal god slots
                    if (pantheon.slot[0] == -1) pantheon.slotGod(pantheon.gods['asceticism'],0);
                    if (pantheon.slot[1] == -1) pantheon.slotGod(pantheon.gods['decadence'],1);
                    if (pantheon.slot[2] == -1) pantheon.slotGod(pantheon.gods['ruin'],2);
                }
            """)
        except:
            pass

    def check_ascension(self):
        try:
            self.driver.execute_script("""
                // Ascend at optimal times
                if (Game.prestige < 1 && Game.HowMuchPrestige(Game.cookiesReset) >= 1) {
                    // First ascension
                    Game.Ascend(1);
                } else if (Game.prestige > 0) {
                    let prestigeGain = Game.HowMuchPrestige(Game.cookiesReset) - Game.prestige;
                    // Ascend when we'll at least double our prestige
                    if (prestigeGain > Game.prestige) {
                        Game.Ascend(1);
                    }
                }
                
                // After ascending, buy important permanent upgrades
                if (Game.AscendTimer > 0) {
                    let priorities = [
                        'Legacy',
                        'Persistent memory',
                        'Dragon flight',
                        'Fortune cookies',
                        'Twin Gates of Transcendence'
                    ];
                    
                    for (let upgrade of priorities) {
                        let up = Game.Upgrades[upgrade];
                        if (up && !up.bought && Game.heavenlyChips >= up.getPrice()) {
                            up.buy();
                        }
                    }
                    
                    Game.Reincarnate(1);
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
        while True:
            try:
                # Click golden cookies and reindeer
                self.driver.execute_script("""
                    for (let shimmer of Game.shimmers) {
                        shimmer.pop();
                    }
                """)
                
                # Click big cookie
                self.driver.execute_script("Game.ClickCookie();")
                
                # Handle all mechanics
                self.strategic_purchase()
                self.handle_minigames()
                self.handle_sugar_lumps()
                self.handle_wrinklers()
                self.handle_krumblor()
                self.handle_santa()
                
                # Periodic checks
                current_time = time.time()
                if current_time - self.last_save > 300:
                    self.driver.execute_script("Game.WriteSave(1);")
                    self.last_save = current_time
                
                if current_time - self.last_ascend_check > 600:
                    self.check_ascension()
                    self.last_ascend_check = current_time
                
                # Status update
                if current_time % 30 < 1:
                    cps = self.driver.execute_script("return Game.cookiesPs")
                    cookies = self.driver.execute_script("return Game.cookies")
                    prestige = self.driver.execute_script("return Game.prestige")
                    print(f"CPS: {cps:.1f} | Cookies: {cookies:.0f} | Prestige: {prestige}")
                
                time.sleep(0.05)
                
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)

def main():
    try:
        bot = CookieClickerBot()
        bot.play()
    except Exception as e:
        print(f"Critical error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()