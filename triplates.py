#Consolidates triplates.ipynb into a single function
import os
def modify_nameplates(
  #Creates text files containing BigDebuffs spells split into buff, debuff, and cc,
  #that are used for a ThreatPlates profile allowed aura list.
  #Uses the "classes" dict to add new spells to the threatplates profile.
  #Optionally inserts "bigdebuffs" spells into the bigdebuffs addon,
  #and overwrites the threatplates "arena_widget" if given.
  #This overwrite replaces names of enemies and allies with their number (arena 1,2,3),
  #or letter (A for party1, B for party2), and class-colors the new names.
  #If not overwriting files, set "big_debuffs=None", and "aura_widget=None".
  #Must supply correct pathing arguments pointing to BigDebuffs and ThreatPlates addons,
  #as well as "outpath" pointing to where created text files will be placed.
    bd_path = r'C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns\BigDebuffs',
    outpath = r'',
    classes = dict(
        paladin = dict(
            buffs = """
Glimmer of Light
Blessing of Summer
Blessing of Spring
Blessing of Autumn
Blessing of Winter
""",
            debuffs = """
Judgment
Unworthy
Glimmer of Light
Searing Glare
Denounce
"""),
        monk = dict(
            buffs = """
Renewing Mist
Enveloping Mist
Essence Font
Sphere of Hope
""",
            debuffs = """
Recently Challenged
Skyreach Exhaustion
Sphere of Despair
Fae Accord
"""),
        evoker = dict(
            buffs = """
Dream Breath
Reversion
Lifebind
Dream Flight
Dream Projection
Echo
""",
            debuffs = """
Fire Breath
"""),
        druid = dict(
            buffs = """
Lifebloom
Rejuvenation
""",
            debuffs = """
Stellar Flare
Feral Frenzy
""")
),

    big_debuffs = {
        'Feral Frenzy':[[274838],'DEBUFF_OFFENSIVE'],
        'Phase Shift':[[408557],'IMMUNITY'],
        'Burrow':[[409293],'IMMUNITY']
    },

    tp_path = r'C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns\TidyPlates_ThreatPlates\Widgets',

    arena_widget = r"""
---------------------------------------------------------------------------------------------------
-- Arena Widget
---------------------------------------------------------------------------------------------------
local ADDON_NAME, Addon = ...

local Widget = (Addon.IS_CLASSIC and {}) or Addon.Widgets:NewWidget("Arena")

---------------------------------------------------------------------------------------------------
-- Imported functions and constants
---------------------------------------------------------------------------------------------------

-- Lua APIs

-- WoW APIs
-- local GetNumArenaOpponents = GetNumArenaOpponents
local IsInInstance = IsInInstance
local IsInBrawl, IsSoloShuffle = C_PvP.IsInBrawl, C_PvP.IsSoloShuffle
local MAX_ARENA_ENEMIES = MAX_ARENA_ENEMIES or 5 -- MAX_ARENA_ENEMIES is not defined in Wrath Clasic

-- ThreatPlates APIs
local Font = Addon.Font

local _G =_G
-- Global vars/functions that we don't upvalue since they might get hooked, or upgraded
-- List them here for Mikk's FindGlobals script
-- GLOBALS: CreateFrame, UnitGUID

---------------------------------------------------------------------------------------------------
-- Constants and local variables
---------------------------------------------------------------------------------------------------
local PATH = "Interface\\AddOns\\TidyPlates_ThreatPlates\\Widgets\\ArenaWidget\\"
local ICON_TEXTURE = PATH .. "BG"

local InArena = false
local PlayerGUIDToNumber = {}
--local ArenaID = {}

---------------------------------------------------------------------------------------------------
-- Cached configuration settings
---------------------------------------------------------------------------------------------------
local Settings

---------------------------------------------------------------------------------------------------
-- Arena Widget Functions
---------------------------------------------------------------------------------------------------
local alphabet = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                  "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                  "U", "V", "W", "X", "Y", "Z"}
local ArenaUnitIdToNumber = {}
for i = 1, MAX_ARENA_ENEMIES do
  ArenaUnitIdToNumber["arena" .. i] = i
  ArenaUnitIdToNumber["arenapet" .. i] = i
  --friendly
  ArenaUnitIdToNumber["party" .. i] = alphabet[i]
  ArenaUnitIdToNumber["partypet" .. i] = i
end

local function GetUnitArenaNumber(guid)
  return PlayerGUIDToNumber[guid]
end

function Widget:PLAYER_ENTERING_WORLD()
  local _, instance_type = IsInInstance()
  if instance_type == "arena" and not IsInBrawl() then
    InArena = true
  else
    InArena = false
    PlayerGUIDToNumber = {}
  end
end

function Widget:PVP_MATCH_ACTIVE()
  PlayerGUIDToNumber = {}
end

-- Parameters: unitToken, updateReason
--   updateReason: seen, destroyed, unseen, cleared
function Widget:ARENA_OPPONENT_UPDATE(unitid, update_reason)
  if update_reason == "seen" then
    local guid = _G.UnitGUID(unitid)
    PlayerGUIDToNumber[guid] = ArenaUnitIdToNumber[unitid]
    local widget_frame = self:GetWidgetFrameForUnit(unitid)
    if widget_frame then
      self:OnUnitAdded(widget_frame, unitid)
    end
  end
end

-- friendly
function Widget:PLAYER_JOINED_PVP_MATCH()
  for i = 1, 5 do
    local unitid = "party" .. i
    local guid = _G.UnitGUID(unitid)
    PlayerGUIDToNumber[guid] = ArenaUnitIdToNumber[unitid]
    local widget_frame = self:GetWidgetFrameForUnit(unitid)
    if widget_frame then
      self:OnUnitAdded(widget_frame, unitid)
    end
  end
end

function Widget:GROUP_ROSTER_UPDATE()
  for i = 1, 5 do
    local unitid = "party" .. i
    local guid = _G.UnitGUID(unitid)
    PlayerGUIDToNumber[guid] = ArenaUnitIdToNumber[unitid]
    local widget_frame = self:GetWidgetFrameForUnit(unitid)
    if widget_frame then
      self:OnUnitAdded(widget_frame, unitid)
    end
  end
end
---------------------------------------------------------------------------------------------------
-- Widget functions for creation and update
---------------------------------------------------------------------------------------------------

function Widget:Create(tp_frame)
  -- Required Widget Code
  local widget_frame = _G.CreateFrame("Frame", nil, tp_frame)
  widget_frame:Hide()
  widget_frame:SetFrameLevel(tp_frame:GetFrameLevel() + 7)
  widget_frame.Icon = widget_frame:CreateTexture(nil, "ARTWORK")
  widget_frame.Icon:SetAllPoints(widget_frame)
  widget_frame.Icon:SetTexture(ICON_TEXTURE)
  widget_frame.NumText = widget_frame:CreateFontString(nil, "ARTWORK")
  self:UpdateLayout(widget_frame)
  return widget_frame
end

function Widget:IsEnabled()
  return Addon.db.profile.arenaWidget.ON
end

function Widget:OnEnable()
  if Addon.IS_MAINLINE then
    self:RegisterEvent("PVP_MATCH_ACTIVE")
  end
  self:RegisterEvent("PLAYER_ENTERING_WORLD")
  self:RegisterEvent("GROUP_ROSTER_UPDATE")
  self:RegisterEvent("PLAYER_JOINED_PVP_MATCH")
  self:RegisterEvent("ARENA_OPPONENT_UPDATE")
end

function Widget:EnabledForStyle(style, unit)
  return not (style == "NameOnly" or style == "NameOnly-Unique" or style == "etotem")
end

function Widget:OnUnitAdded(widget_frame, unit)
  if not InArena then
    widget_frame:Hide()
    return
  end

  local arena_no = GetUnitArenaNumber(unit.guid)
  if not arena_no then
    widget_frame:Hide()
    return
  end

  if Settings.ShowOrb then
    local icon_color = Settings.colors[arena_no]
    widget_frame.Icon:SetVertexColor(icon_color.r, icon_color.g, icon_color.b, icon_color.a)
  end

  if Settings.ShowNumber then
    local db = Addon.db.profile
    local number_color
    number_color = db.Colors.Classes[unit.class]
    widget_frame.NumText:SetTextColor(number_color.r, number_color.g, number_color.b)
    widget_frame.NumText:SetText(arena_no)
  end

  if Settings.HideName then
    widget_frame:GetParent().visual.name:Hide()
  elseif Addon.db.profile.settings.name.show then
    widget_frame:GetParent().visual.name:Show()
  end

  widget_frame:Show()
end

function Widget:UpdateLayout(widget_frame)
  -- Updates based on settings
  widget_frame:SetPoint("CENTER", widget_frame:GetParent(), Settings.x, Settings.y)
  widget_frame:SetSize(Settings.scale, Settings.scale)

  if Settings.ShowOrb then
    widget_frame.Icon:Show()
  else
    widget_frame.Icon:Hide()
  end

  if Settings.ShowNumber then
    Font:UpdateText(widget_frame, widget_frame.NumText, Settings.NumberText)
    widget_frame.NumText:Show()
  else
    widget_frame.NumText:Hide()
  end
end

function Widget:UpdateSettings()
  Settings = Addon.db.profile.arenaWidget
end
"""

):
    #read bigdebuffs
    os.chdir(bd_path)
    file = r'BigDebuffs_Mainline.lua'
    with open(file) as f:
        lines = f.readlines()
    #add lines for new spells
    def add_bd_lines(d):
        F = lambda d,k,i=0 : f'\t[{d[k][0][i]}] = '+'{'+ f' type = {d[k][1]}'+' }'+f', -- {k}\n'
        lines=[]
        for k,v in d.items():
            for i in range(len(v[0])):
                lines+=[F(d=d,k=k,i=i)]
        return lines
    #insert new spells
    breakpoint=[i for i in range(len(lines)) if 'addon.Spells = {' in lines[i]][0]
    old_lines_first = lines[:breakpoint+1]
    old_lines_last = lines[breakpoint+1:]
    new_lines = old_lines_first + add_bd_lines(big_debuffs) + old_lines_last
    #rewrite file
    with open(file,'w') as f:
        f.writelines(new_lines)
    #parse spells
    categories = {'BUFF_DEFENSIVE','BUFF_OFFENSIVE','BUFF_OTHER','BUFF_SPEED_BOOST','DEBUFF_OFFENSIVE',
        'INTERRUPT','CROWD_CONTROL','ROOT','IMMUNITY','IMMUNITY_SPELL'}
    cc = ['CROWD_CONTROL']
    debuffs = ['DEBUFF_OFFENSIVE','INTERRUPT','ROOT']
    buffs = [c for c in categories if (c not in debuffs) and (c not in cc)]
    abilities = {'d':[],'b':[],'c':[]}
    #collect spells in each category
    for line in new_lines:
        try:
            key = line.split('=')[2].split('}')[0].strip()
            val = line.split('=')[0].split('[')[-1].split(']')[0]
            if key in cc:
                k = 'c'
            elif key in debuffs:
                k = 'd'
            elif key in buffs:
                k = 'b'
            else:
                pass
            abilities[k]+=[val]
        except:
            pass
    #add newline character to list of spells
    keys = list(abilities.keys())
    for t in keys:
        l = len(abilities[t])
        for i in range(l):
            abilities[t][i]+='\n'
    #collect as lists
    buffs = abilities['b']
    debuffs = abilities['d']+abilities['c']
    #create new containers
    all_buffs = []
    all_debuffs = []
    all_buffs += buffs
    all_debuffs += debuffs
    #output text files containing spells for each class
    os.chdir(outpath)
    for wowclass,auras in classes.items():
        bufflines = [i+'\n' for i in auras['buffs'].split('\n')[1:-1]]
        debufflines = [i+'\n' for i in auras['debuffs'].split('\n')[1:-1]]
        #save as class_aura.txt
        with open(wowclass+'_buffs.txt','w') as f:
            f.writelines(buffs+bufflines)
        with open(wowclass+'_debuffs.txt','w') as f:
            f.writelines(debuffs+debufflines)
        #increment total auras
        all_buffs += bufflines
        all_debuffs += debufflines
    #create file with all auras
    with open('all_buffs.txt','w') as f:
        f.writelines(all_buffs)
    with open('all_debuffs.txt','w') as f:
        f.writelines(all_debuffs)
    #rewrite arena widget
    if arena_widget is not None:
        os.chdir(tp_path)
        file = r'ArenaWidget.lua'
        with open(file,'w') as f:
          f.write(arena_widget)