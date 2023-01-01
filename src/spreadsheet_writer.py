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

# FIXME: WE CAN PROBABLY DELETE THIS?
import datetime
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
        


