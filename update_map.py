import tgmlib

old_map_path = 'ECM1.TGM'
new_map_path = 'KG-0.9.6.TGM'
name_mapping_path = ''
old_map = tgmlib.tgmFile(old_map_path)
new_map = tgmlib.tgmFile(new_map_path)
old_map.load()
print('---------------------------------------------------------------------')
new_map.load()

# Use this mapping to go from pre KG-0.9.5 (includes AG-1.3.7 and 1.3.10) to KG-0.9.6
name_mapping = {
    'CREATURE': 'RHAKSHA',
    'DHAVRUM_BELRAAG': 'DHAVRUM_BELRAAG_CAPTAIN',
    'Dhavrum BelraagAscended': 'DHAVRUM_BELRAAG_CAPTAIN',
    'Dhavrum BelraagEnlightened': 'DHAVRUM_BELRAAG_CAPTAIN',
    'Dhavrum BelraagRestored': 'DHAVRUM_BELRAAG_CAPTAIN',
    'DHAVRUM_BELRAAG corpse': 'DHAVRUM_BELRAAG_CAPTAIN corpse',
    "GAROJ'MOK": "GAROJ'MOK_CAPTAIN",
    "GAROJ'MOK corpse": "GAROJ'MOK_CAPTAIN corpse",
    "Garoj'mokAscended": "GAROJ'MOK_CAPTAIN",
    "Garoj'mokEnlightened": "GAROJ'MOK_CAPTAIN",
    "Garoj'mokRestored": "GAROJ'MOK_CAPTAIN",
    'GideonAscended': 'Gideon XarrAscended',
    'GideonEnlightened': 'Gideon XarrEnlightened',
    'GideonRestored': 'Gideon XarrRestored',
    'KARG': 'KARG_CAPTAIN',
    'KARG corpse': 'KARG_CAPTAIN corpse',
    'KargAscended': 'KARG_CAPTAIN',
    'KargEnlightened': 'KARG_CAPTAIN',
    'KargRestored': 'KARG_CAPTAIN',
    'KING_ULRIC': 'KING_ULRIC_CAPTAIN',
    'KING_ULRIC corpse': 'KING_ULRIC_CAPTAIN corpse',
    'King UlricAscended': 'KING_ULRIC_CAPTAIN',
    'King UlricEnlightened': 'KING_ULRIC_CAPTAIN',
    'King UlricRestored': 'KING_ULRIC_CAPTAIN',
    'SLAAN_CHAMPION': 'SLAANRI_CHAMPION',
    'SLAAN_MILITIA': 'SLAANRI_MILITIA',
    'DALI_AZADE': 'DHAVRUM_BELRAAG',
    'DALI_AZADE corpse': 'DHAVRUM_BELRAAG corpse',
    'DARYA_AZAR': "GAROJ'MOK",
    'DARYA_AZAR corpse': "GAROJ'MOK corpse",
    'JHAENGUS': 'KARG',
    'JHAENGUS corpse': 'KARG corpse',
    'JILLA_JANNAT': 'KING_ULRIC',
    'JILLA_JANNAT corpse': 'KING_ULRIC corpse',
    'LUCIUS_AJAM': 'LORD_JAVIDAN',
    'LUCIUS_AJAM corpse': 'LORD_JAVIDAN corpse',
    'LORD_JAVIDAN': 'DARIUS_JAVIDAN',
    'LORD_JAVIDAN corpse': 'DARIUS_JAVIDAN corpse',
    'Lord JavidanAscended': 'Darius JavidanAscended',
    'Lord JavidanEnlightened': 'Darius JavidanEnlightened',
    'Lord JavidanRestored': 'Darius JavidanRestored',
    'MAUSALLAS_BAHRAM': 'MISTRESS_ROXANNA',
    'MAUSALLAS_BAHRAM corpse': 'MISTRESS_ROXANNA corpse',
    'MISTRESS_ROXANNA': 'VASHTI',
    'MISTRESS_ROXANNA corpse': 'VASHTI corpse',
    'Mistress JavidanAscended': 'VashtiAscended',
    'Mistress JavidanEnlightened': 'VashtiEnlightened',
    'Mistress JavidanRestored': 'VashtiRestored',
    'MISTRESS_VASHTI': 'VASHTI',
    'MISTRESS_VASHTI corpse': 'VASHTI corpse',
    'Mistress VashtiAscended': 'VashtiAscended',
    'Mistress VashtiEnlightened': 'VashtiEnlightened',
    'Mistress VashtiRestored': 'VashtiRestored',
    'Samman RavidAscended': 'Samman OsahyrAscended',
    'Samman RavidEnlightened': 'Samman OsahyrEnlightened',
    'Samman RavidRestored': 'Samman OsahyrRestored',
    'SEBASTIAN_ATAFEH': 'SAR_LASHKAR2',
    'SEBASTIAN_ATAFEH corpse': 'SAR_LASHKAR2 corpse',
    'SAR_LASHKAR2': 'SAR_LASHKAR',
    'SAR_LASHKAR2 corpse': 'SAR_LASHKAR corpse',
    'Lord Sar LashkarAscended': 'Sar LashkarAscended',
    'Lord Sar LashkarEnlightened': 'Sar LashkarEnlightened',
    'Lord Sar LashkarRestored': 'Sar LashkarRestored',
    'SOLOMON_GHAFFAR': 'SHOHN_MAHT2',
    'SOLOMON_GHAFFAR corpse': 'SHOHN_MAHT2 corpse',
    'SHOHN_MAHT2': 'SHOHN_MAHT',
    'SHOHN_MAHT2 corpse': 'SHOHN_MAHT corpse',
    'Lord Shohn MahtAscended': 'Shohn MahtAscended',
    'Lord Shohn MahtEnlightened': 'Shohn MahtEnlightened',
    'Lord Shohn MahtRestored': 'Shohn MahtRestored',
    'BANDIT_CAMP': 'BRIGAND_CAMP',
    'BANDIT_CAMP ruin': 'BRIGAND_CAMP ruin',
    'NEST': 'RHAKSHA_NEST',
    'NEST ruin': 'RHAKSHA_NEST ruin',
    'NEW_AHRIMAN_CITADEL': 'AHRIMAN_CITADEL',
    'NEW_AHRIMAN_CITADEL ruin': 'AHRIMAN_CITADEL ruin',
    }

index_mapping = {}

for k, v in old_map.TYPE.by_name.items():
    if k in name_mapping:
        name = name_mapping[k]
    else:
        name = k
        
    new_index = new_map.TYPE.by_name[name]['index']
    old_index = v['index']
    index_mapping[old_index] = new_index
    
for obj in old_map.OBJS.objs:
    print(f'obj id:{obj.header.editor_id} ix:{obj.header.index} -> {index_mapping[obj.header.index]}')
    obj.header.index = index_mapping[obj.header.index]
    match obj.header.obj_class:
        case 0x24:
            # Building specific stuff goes here
            pass
        case 0x3C:
            # company specific stuff goes here
            #company speed
            #company modifiers provided
            #unit modifiers provided
            #all company modifiers
            #unit current speed
            #unit modifiers gained
            #unit base speed
            #unit max hp
            #unit mana
            pass

    
    
    
# Items to update:
    #main index and all references
        #copy correct index (TYPE) from correct blank map
        #index locations are FTRS, OBJS, and individual units
        #include list of overrides for ini swaps
        #apply overrides to HROS
        #add adtl heroes to HROS
    

#Adtl TODO
    #Add HROS chunk
    #Add FTRS Chunk
    #Add companies
    #Add repacking to .TGM