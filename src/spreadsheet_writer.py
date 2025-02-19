#!/usr/bin/env python3
# coding=utf-8
"""

 Writes a table with all the abilitis in it and their costs.
 Used to try and tweak game balance.

    attack
    defence
    stategy??  no damage or defense directly but useful in combat
    rp/colour

 max to hit for a level
 max damage for a level
 max defence for a level


  list abilities and rate them
  look up max value by level and group or ability


"""

import xlsxwriter


def write_game_balance_spreadsheet(spreadsheet_fname,
                                   ability_groups,
                                   archetypes):

    workbook = xlsxwriter.Workbook(spreadsheet_fname)
    worksheet = workbook.add_worksheet()    
    
    #
    LABEL_COL = 1

    r = 1
    c = LABEL_COL

    worksheet.write(r, c, "Level"); c += 1
    for level in range(1, 10):
        worksheet.write(r, c, level); c += 1

    ABILITY_LABEL_COL = 2
    r += 2
    for ability_group in ability_groups:
        worksheet.write(r, LABEL_COL, ability_group.get_title())        
        r += 1

        for ability in ability_group:
            worksheet.write(r, ABILITY_LABEL_COL, ability.get_title())
            r += 1

    r += 2
    c = LABEL_COL
    
    for archetype in archetypes:
        worksheet.write(r, c, archetype.get_title())
        # c += 1
        r += 1
        
    workbook.close()
    return




def write_ability_summary_spreadsheet(spreadsheet_fname, ability_groups):
    workbook = xlsxwriter.Workbook(spreadsheet_fname)
    ws = workbook.add_worksheet()    

    title_format = workbook.add_format({'bold': True, 'font_size': 14})
    
    r = 1
    FAMILY_COL = 1
    GROUP_COL = FAMILY_COL+1
    ABILITY_COL = GROUP_COL+1
    CHECK_COL = ABILITY_COL+1
    KEYWORDS_COL = CHECK_COL+1
    # COST_COL = KEYWORDS_COL+1
    # RANGE_COL = COST_COL+1
    RANGE_COL = KEYWORDS_COL+1
    ACTION_TYPE_COL = RANGE_COL+1
    TRIGGER_COL = ACTION_TYPE_COL+1

    # 
    CRIT_SUCCESS_COL = TRIGGER_COL+1
    RIGHTEOUS_SUCCESS_COL = CRIT_SUCCESS_COL+1
    SUCCESS_COL = RIGHTEOUS_SUCCESS_COL+1
    FAIL_COL = SUCCESS_COL+1
    GRIM_FAIL_COL = FAIL_COL+1
    CRIT_FAIL_COL = GRIM_FAIL_COL+1

    # Fate
    BLESSED_COL = CRIT_FAIL_COL+1
    BOON_COL = BLESSED_COL+1
    BANE_COL = BOON_COL+1
    DAMNED_COL = BANE_COL+1

    ws.write(r, FAMILY_COL, "Family", title_format)
    ws.write(r, GROUP_COL, "Group", title_format)
    ws.write(r, ABILITY_COL, "Ability", title_format)
    ws.write(r, CHECK_COL, "Check", title_format)
    ws.write(r, KEYWORDS_COL, "Keywords", title_format)
    # ws.write(r, COST_COL, "Cost", title_format)
    ws.write(r, RANGE_COL, "Range", title_format)
    ws.write(r, ACTION_TYPE_COL, "Action Type", title_format)
    ws.write(r, TRIGGER_COL, "Trigger", title_format)


    ws.write(r, CRIT_SUCCESS_COL, "Crit Success", title_format)
    ws.write(r, RIGHTEOUS_SUCCESS_COL, "Righteous Success", title_format)
    ws.write(r, SUCCESS_COL, "Success", title_format)
    ws.write(r, FAIL_COL, "Fail", title_format)
    ws.write(r, GRIM_FAIL_COL, "Grim Fail", title_format)
    ws.write(r, CRIT_FAIL_COL, "Crit Fail", title_format)
    
    ws.write(r, BLESSED_COL, "Blessed", title_format)
    ws.write(r, BOON_COL, "Boon", title_format)
    ws.write(r, BANE_COL, "Bane", title_format)
    ws.write(r, DAMNED_COL, "Damned", title_format)
    
    r += 2
    for ability_group in ability_groups:
        for ability in ability_group:
            for check in ability.get_checks():
                ws.write(r, FAMILY_COL, ability_group.get_family())
                ws.write(r, GROUP_COL, ability_group.get_title())        
                ws.write(r, ABILITY_COL, ability.get_title())
                ws.write(r, CHECK_COL, check.get_name())
                ws.write(r, KEYWORDS_COL, ", ".join(check.get_keywords()))
                #ws.write(r, COST_COL, check.get_cost())
                ws.write(r, RANGE_COL, check.get_range())
                ws.write(r, ACTION_TYPE_COL, check.get_action_type())
                ws.write(r, TRIGGER_COL, check.get_trigger())

                ws.write(r, CRIT_SUCCESS_COL, check.critsuccess)
                ws.write(r, RIGHTEOUS_SUCCESS_COL, check.righteoussuccess)
                ws.write(r, SUCCESS_COL, check.success)
                ws.write(r, FAIL_COL, check.fail)
                ws.write(r, GRIM_FAIL_COL, check.grimfail)
                ws.write(r, CRIT_FAIL_COL, check.critfail)
                
                ws.write(r, BLESSED_COL, check.blessed)
                ws.write(r, BOON_COL, check.boon)
                ws.write(r, BANE_COL, check.bane)
                ws.write(r, DAMNED_COL, check.damned)
                r += 1

    ws.autofit()
    workbook.close()
    return


if __name__ == "__main__":
    from os.path import join # abspath, join, splitext, dirname, exists, basename    
    from db import DB
    from utils import root_dir, build_dir
    
    db = DB()
    db.load(root_dir=root_dir, fail_fast=True)

    ability_summary_fname = join(build_dir, "ability_summary.xlsx")
    write_ability_summary_spreadsheet(
        ability_summary_fname,
        ability_groups=db.ability_groups)    
  
    


