#---------------------------
#   Import Libraries
#---------------------------
import clr, codecs, json, os, re, sys, threading, datetime, random
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references
random = random.WichmannHill()  #Use in place of Parent.GetRandom()
clr.AddReference("IronPython.Modules.dll")
clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)) + "\References", "TwitchLib.PubSub.dll"))
from TwitchLib.PubSub import TwitchPubSub
#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "LanceLake's Source Toggle Rewards"
Website = "https://www.awakeneddragons.com"
Description = "Custom script for toggling sources on reward redemption."
Creator = "AwakenedDragons"
Version = "1.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
ThreadQueue = []
CurrentThread = None
NextRewardAt = datetime.datetime.now()
SceneRevert = ""

#---------------------------
#   Define Settings, Defaults and Settings Functions
#---------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile=None):
        if settingsFile and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')

        else:
            self.Username = ""
            self.OauthToken = ""
            self.RewardName1 = ""
            self.RewardName2 = ""
            self.RewardName3 = ""
            self.RewardName4 = ""
            self.RewardName5 = ""
            self.RewardName6 = ""
            self.RewardName7 = ""
            self.RewardName8 = ""
            self.RewardName9 = ""
            self.RewardName10 = ""
            self.RewardName11 = ""
            self.RewardName12 = ""
            self.RewardName13 = ""
            self.RewardName14 = ""
            self.RewardName15 = ""
            self.SourceName1 = ""
            self.SourceName2 = ""
            self.SourceName3 = ""
            self.SourceName4 = ""
            self.SourceName5 = ""
            self.SourceName6 = ""
            self.SourceName7 = ""
            self.SourceName8 = ""
            self.SourceName9 = ""
            self.SourceName10 = ""
            self.SourceName11 = ""
            self.SourceName12 = ""
            self.SourceName13 = ""
            self.SourceName14 = ""
            self.SourceName15 = ""
            self.ToggleTime1 = 0
            self.ToggleTime2 = 0
            self.ToggleTime3 = 0
            self.ToggleTime4 = 0
            self.ToggleTime5 = 0
            self.ToggleTime6 = 0
            self.ToggleTime7 = 0
            self.ToggleTime8 = 0
            self.ToggleTime9 = 0
            self.ToggleTime10 = 0
            self.ToggleTime11 = 0
            self.ToggleTime12 = 0
            self.ToggleTime13 = 0
            self.ToggleTime14 = 0
            self.ToggleTime15 = 0
            self.SceneName1 = ""
            self.SceneName2 = ""
            self.SceneName3 = ""
            self.SceneName4 = ""
            self.SceneName5 = ""
            self.SceneName6 = ""
            self.SceneName7 = ""
            self.SceneName8 = ""
            self.SceneName9 = ""
            self.SceneName10 = ""
            self.SceneName11 = ""
            self.SceneName12 = ""
            self.SceneName13 = ""
            self.SceneName14 = ""
            self.SceneName15 = ""
            pass
        
    def ReloadSettings(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    # Save settings to files (json and js)
    def SaveSettings(self, settingsFile):
        """Save settings to files (json and js)"""
        with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))
        return
    
#---------------------------
# Classes
#---------------------------
#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():
    """data on Load, required function"""
    global MySet
    MySet = Settings(settingsFile)
    MySet.SaveSettings(settingsFile)
    Start()
    return

def OauthToken():
    os.startfile("https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=o2g8b0t9s2ib3ozn0aghowgsaz7phn&redirect_uri=https://twitchapps.com/tokengen/&scope=channel%3Aread%3Aredemptions")
    return

def Start():
    global EventReceiver
    EventReceiver = TwitchPubSub()
    EventReceiver.OnPubSubServiceConnected += EventReceiverConnected
    EventReceiver.OnListenResponse += EventReceiverListenResponse
    EventReceiver.OnRewardRedeemed += EventReceiverRewardRedeemed
    EventReceiver.OnPubSubServiceError += EventReceiverError
    EventReceiver.OnPubSubServiceClosed += EventReceiverDisconnected
    
    EventReceiver.Connect()

def EventReceiverConnected(sender, e):
    #get channel id for username
    headers = { 'Client-ID': 'o2g8b0t9s2ib3ozn0aghowgsaz7phn',"Authorization": "Bearer " + MySet.OauthToken}
    result = json.loads(Parent.GetRequest("https://api.twitch.tv/helix/users?login=" + MySet.Username,headers))
    user = json.loads(result["response"])
    id = user["data"][0]["id"]
    
    EventReceiver.ListenToRewards(id)
    EventReceiver.SendTopics()
    return

def EventReceiverError(sender, e):
    Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Error: " + e.Response.Error);
    return

def EventReceiverDisconnected(sender, e):
    Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Disconnected")
    return

def EventReceiverListenResponse(sender, e):
    if e.Successful:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Successfully verified listening to topic: " + e.Topic);
    else:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Failed to listen! Error: " + e.Response.Error);
    return

def EventReceiverRewardRedeemed(sender, e):
    Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Redemption Recieved, " + e.RewardTitle)
    if e.RewardTitle == MySet.RewardName1:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 1 Redeemed Successfully")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName1,MySet.SourceName1, MySet.ToggleTime1,)))
    elif e.RewardTitle == MySet.RewardName2:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 2 Redeemed Successfully")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName2,MySet.SourceName2, MySet.ToggleTime2,)))
    elif e.RewardTitle == MySet.RewardName3:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 3 Redeemed Successfully")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName3,MySet.SourceName3, MySet.ToggleTime3,)))
    elif e.RewardTitle == MySet.RewardName4:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 4 Redeemed Successfully")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName4,MySet.SourceName4, MySet.ToggleTime4,)))
    elif e.RewardTitle == MySet.RewardName5:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 5 Redeemed Successfully")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName5,MySet.SourceName5, MySet.ToggleTime5,)))
    elif e.RewardTitle == MySet.RewardName6:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 6 Redeemed Successfully")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName6,MySet.SourceName6, MySet.ToggleTime6,)))
    elif e.RewardTitle == MySet.RewardName7:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 7 Redeemed")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName7,MySet.SourceName7, MySet.ToggleTime7,)))
    elif e.RewardTitle == MySet.RewardName8:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 8 Redeemed")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName8,MySet.SourceName8, MySet.ToggleTime8,)))
    elif e.RewardTitle == MySet.RewardName9:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 9 Redeemed")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName9,MySet.SourceName9, MySet.ToggleTime9,)))
    elif e.RewardTitle == MySet.RewardName10:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 10 Redeemed")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName10,MySet.SourceName10, MySet.ToggleTime10,)))
    elif e.RewardTitle == MySet.RewardName11:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 11 Redeemed")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName11,MySet.SourceName11, MySet.ToggleTime11,)))
    elif e.RewardTitle == MySet.RewardName12:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 12 Redeemed")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName12,MySet.SourceName12, MySet.ToggleTime12,)))
    elif e.RewardTitle == MySet.RewardName13:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 13 Redeemed")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName13,MySet.SourceName13, MySet.ToggleTime13,)))
    elif e.RewardTitle == MySet.RewardName14:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 14 Redeemed")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName14,MySet.SourceName14, MySet.ToggleTime14,)))
    elif e.RewardTitle == MySet.RewardName15:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Reward 15 Redeemed")
        ThreadQueue.append(threading.Thread(target=SourceToggle,args=(MySet.SceneName15,MySet.SourceName15, MySet.ToggleTime15,)))
    else:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + e.RewardTitle + " reward is not set in settings.")
    return

def SourceToggle(SceneTarget, SourceTarget, ToggleDuration):
    if SourceTarget == "":
        Parent.SetOBSCurrentScene(SceneTarget, callback)
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Scene Changed")
        if ToggleDuration == 0:
            return
        else:
            return
    else:
        Parent.SetOBSSourceRender(SourceTarget, True, SceneTarget, callback)
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Source Toggled")
        if ToggleDuration == 0:
            return
        else:
            global NextRewardAt
            NextRewardAt = datetime.datetime.now() + datetime.timedelta(0,ToggleDuration)
            ThreadQueue.insert(0,threading.Thread(target=SourceToggleOff,args=(SceneTarget,SourceTarget,)))
            return
    return


def SourceToggleOff(SceneTarget, SourceTarget):
    if SourceTarget == "":
        return
    else:
        Parent.SetOBSSourceRender(SourceTarget, False, SceneTarget, callback)
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + "Source Toggled Back")
    global NextRewardAt
    NextRewardAt = datetime.datetime.now()
    return

def callback(jsonString):
   return

#---------------------------
# Reward Queue
#---------------------------

def RewardQueue():
    global NextRewardAt
    if NextRewardAt > datetime.datetime.now():
        return
    
    global CurrentThread
    if CurrentThread and CurrentThread.isAlive() == False:
        CurrentThread = None

    if CurrentThread == None and len(ThreadQueue) > 0:
        CurrentThread = ThreadQueue.pop(0)
        CurrentThread.start()
    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    return
#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    RewardQueue()
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------

def ReloadSettings(jsondata):
    """Reload settings on Save"""
    # Reload saved settings
    MySet.ReloadSettings(jsondata)
    # End of ReloadSettings
    return

def SaveSettings(self, settingsFile):
    """Save settings to files (json and js)"""
    with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
        json.dump(self.__dict__, f, encoding='utf-8-sig')
    with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
        f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig')))
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    global EventReceiver
    try:
        if EventReceiver:
            EventReceiver.Disconnect()
            Parent.Log(ScriptName,"[" + str(datetime.datetime.now()) + "]" + "Disconnected")
            
    except Exception as e:
        Parent.Log(ScriptName, "[" + str(datetime.datetime.now()) + "]" + str(e))
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return
