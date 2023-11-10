# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Attendance from Web-My Account using Portal User as Employee',
    'version': '16.0.1.0',
    'license': 'Other proprietary',
    'category': 'Website',
    'summary':  """This module allow you to employee(s) who are not real users of system but portal users / external user and it will allow to record check in and checkout as attendance""",
    'description': """
     Odoo Portal Employee Attendance
     
     Tags:
Odoo attendance Portal User Employee
attendance Portal User
Odoo attendances
Attendance Check In Check Out
Attendance Sign In Sign Out
Employee Attendance Check In Check Out
Employee Attendance Sign In Sign Out
Portal Employee Attendance Check In Check Out
Attendance Sign In Sign Out
Your attendances
My attendances
Project attendance
User attendances
Employee attendances
Portal user attendances
portal attendance
website attendance
enterprise user attendance
enterprise attendance user
enterprise employee attendance
enterprise attendance employee
attendance for enterprise user
attendance for enterprise employee
attendance recording
attendance entry for enterprise
attendance entry employee enterprise
enterprise paid users
enterprise free users
enterprise employee user
enterprise user employee
attendance user fill
attendance employee fill
enterprise attendance encoding
attendance fill
enterprise attendance
hr attendance
hr attendance enterprise employee
hr attendance enterprise user
enterprise fill attendance activities
attendance activities
attendance lines enterprise user
attendance lines enterprise employee
attendance work enterprise user
attendance work user
attendance work employee enterprise
portal attendance enterprise
portal attendance
website attendance
attendance data
attendance import
attendance export
odoo enterprise user
odoo enterprise employee
odoo external employee
odoo external user
external user attendance
worker attendance
This module allow you to employee(s) who are not real users of system but portal users / external user and it will allow to record attendances.
labour attendance
external employee attendance
external user attendance
attendance Entry from Web-My Account using Portal User as Employee
external attendance employee
external attendance user
Portal Users who are employee of system but not real users can fill/record attendance Activities.
If your company using attendance application but not purchased real users from Odoo Enterprise then your employee can fill attendance as portal users.
No need to create real users in system if you are only using attendance module to make attendance entry for your all employees. So you can create portal users and set it on employee form and employee can use that portal user logged to fill attendance activities.
Make sure you have set Portal attendance group on portal user form on settings of users.
No need to purchase users from Odoo Enterprise only to fill attendance any more.
For more details please watch Video or contact us before buy.

employee login
emloyee information
employee detail
sse
ess employee
Self Service
Self Service/Calendar
Self Service/Employee
Self Service/Employee/Employee Details
Self Service/Expenses
Self Service/Expenses/Expenses to Submit
Self Service/Leave Request
Self Service/Leave Request/Leaves Requests
Self Service/Maintenance
Self Service/Maintenance/Maintenance Requests
Self Service/PaySlip
Self Service/PaySlip/Contracts
Self Service/PaySlip/Employee Payslips
Self Service/Projects
Self Service/Projects/Projects
Self Service/Projects/Tasks
Self Service/attendance
Self Service/attendance/Attendences
Self Service/attendance/Detailed Activities
Self Service/attendance/My attendances
employee self service
ESS
ess
self service odoo
portal
self service
self portal
odoo self service employee
employee portal
employee job portal
self service odoo employee
employee details
employee leave
employee attendance
employee holidays
self service portal​
     """,
    'author': 'Soltein SA de CV',
    'website': 'https://www.soltein.net',
    'live_test_url': 'https://youtu.be/4uXNlgB5Q_8',
    'depends': [
        'hr_attendance',
        'portal',
        ],
    'data': [
      'security/security.xml',
      'security/ir.model.access.csv',
      'views/website_portal_templates.xml',
      
     ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
