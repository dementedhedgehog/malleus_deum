from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch


 
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


# doc = SimpleDocTemplate("simple_table.pdf", pagesize=A4)

# # container for the 'Flowable' objects
# elements = []
 
# data= [['00', '01', '02', '03', '04'],
#        ['10', '11', '12', '13', '14'],
#        ['20', '21', '22', '23', '24'],
#        ['30', '31', '32', '33', '34']]
# table = Table(data)
# table.setStyle(TableStyle([('BACKGROUND',(1,1),(-2,-2),colors.green),
#                            ('TEXTCOLOR',(0,0),(1,-1),colors.red)]))
# elements.append(table)
# # write the document to disk
# doc.build(elements)


#from reportlab.pdfgen import canvas
#def hello(c):
#    c.drawString(100,100,"Hello World")
#
#    
#c = canvas.Canvas("hello.pdf")
#hello(c)
#c.showPage()
#c.save()



from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table
from reportlab.lib.styles import getSampleStyleSheet

page_size = A4
width, height = page_size
#left_margin = 1 * inch
#right_margin = 1 * inch
#top_margin = 1 * inch
#bottom_margin = 4.6 * inch

doc = SimpleDocTemplate("complex_cell_values.pdf",
                        pagesize=page_size,
                        debug=True,
                        #topMargin = top_margin,
                        #bottomMargin = bottom_margin,
)
# container for the 'Flowable' objects
elements = []
 
styleSheet = getSampleStyleSheet()


n_rows = 5
#row_height = (height - doc.topMargin - doc.bottomMargin)  / (n_rows+0.0) # (n_rows+1)
#row_height = (doc.height - doc.topMargin - doc.bottomMargin)  / (n_rows+0.0) # (n_rows+1)
row_height = (doc.height - 0.2 * inch)  / (n_rows+0.0) # (n_rows+1)
row_heights = n_rows * [row_height, ]

print height
print doc.topMargin
print doc.bottomMargin
print (height - doc.topMargin - doc.bottomMargin)

print row_heights

n_cols = 2
col_width = (width - doc.leftMargin - doc.rightMargin)/ n_cols
col_widths = n_cols * [ col_width, ]
 
# I = Image('x.png')
# I.drawHeight = 1.25*inch*I.drawHeight / I.drawWidth
# I.drawWidth = 1.25*inch
# P0 = Paragraph('''
#                <b>A pa<font color=red>r</font>a<i>graph</i></b>
#                <super><font color=yellow>1</font></super>''',
#                styleSheet["BodyText"])
# P = Paragraph("""
#     <para align=center spaceb=3>The <b>ReportLab Left
#     <font color=red>Logo</font></b>
#     Image</para>""",
#     styleSheet["BodyText"])

P = Paragraph("""Name:""",
    styleSheet["BodyText"])



data = [[P, 'Name:', ], ] * n_rows
#[#['A', P0, ],
       #['00', [I,P], ],
       #[[P,I], '14'],
       #['20', '21', ],
       #['20', '21', ],
       #['20', '21', ],
       #['30', '31', ],
       # ['20', '21', ],
       # ['20', '21', ],
       # ['20', '21', ],
       # ['20', '21', ],
       # ['20', '21', ],
#]
 
table = Table(data,
              colWidths = col_widths,
              rowHeights = row_heights,
              #rowHeights = "*",
              style=[
              # style=[
                  ('GRID',(0,0),(-1,-1),1,colors.green),
                  ('BOX',(0,0),(-1,-1),2,colors.black),
              #        ('LINEABOVE',(1,2),(-2,2),1,colors.blue),
              #        ('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
              #    ('BACKGROUND', (0, 0), (0, 1), colors.pink),
              #        ('BACKGROUND', (1, 1), (1, 2), colors.lavender),
              #        ('BACKGROUND', (2, 2), (2, 3), colors.orange),
              #        ('BOX',(0,0),(-1,-1),2,colors.black),
              #        ('GRID',(0,0),(-1,-1),0.5,colors.black),
                  ('VALIGN',(0,0),(-1,-1),'TOP'),
              #        ('BACKGROUND',(3,0),(3,0),colors.limegreen),
              #        ('BACKGROUND',(3,1),(3,1),colors.khaki),
              #        ('ALIGN',(3,1),(3,1),'CENTER'),
              #        ('BACKGROUND',(3,2),(3,2),colors.beige),
              #        ('ALIGN',(3,2),(3,2),'LEFT'),
              ])

#table._argW[3]=1.5*inch
#table._argW[3]=1.5*inch
 
elements.append(table)
# write the document to disk
doc.build(elements)
