###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["ProjectConfigWdg", "UserConfigWdg", "UserPanelWdg"]

from pyasm.common import Common, Environment
from pyasm.search import Search, SearchKey, SearchType
from pyasm.biz import Project
from pyasm.security import Sudo
from pyasm.web import DivWdg, Table, WebContainer, SpanWdg, HtmlElement
from pyasm.widget import ThumbWdg, IconWdg, CheckboxWdg
from tactic.ui.container import SmartMenu

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import IconButtonWdg, SingleButtonWdg, ActionButtonWdg
from tactic.ui.panel import ViewPanelWdg

class ProjectConfigWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    } 

    def get_help_alias(self):
        return 'project-startup-configuration'

    def get_panel_wdg(self, td, panel):

        title = panel.get("title")
        widget = panel.get("widget")
        width = panel.get("width")

        #height = panel.get("height")
        #if not height:
        #    height = "250px"
        #td.add_style("height: %s" % height)

        if width:
            td.add_style("width: %s" % width)

        #td.add_border()

        div = DivWdg()
        div.add_style("padding: 5px")
        #div.add_style("padding: 10px")


        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add_style("padding: 5px")
        #title_wdg.add_style("margin: -12px -12px 10px -12px")
        title_wdg.add_style("margin: -6px -6px 5px -6px")
        #title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("font-size: 25px")
        #title_wdg.add_style("height: 25px")

        if title:
            #title_wdg.add_color("background", "background", -5)
            title_wdg.add_color("color", "color", -10)
            #title_wdg.add_border()
            title_wdg.add(title)
            title_wdg.add_style("padding-top: 10px")
            title_wdg.add_style("padding-left: 10px")

            from tactic.ui.app import HelpButtonWdg
            help_wdg = HelpButtonWdg(alias=self.get_help_alias())
            help_wdg.add_style("float: right")
            help_wdg.add_style("margin-top: -5px")
            title_wdg.add(help_wdg)

            title_wdg.add("<hr/>")
        else:
            title_wdg.add_style("height: 10px")

        if widget:
            div.add(widget)

        return div


    def get_panels(self):

        panels = []

        search_type_panel = DivWdg()
        search_type_panel.add_style("padding-top: 3px")
        search_type_panel.add_style("overflow-y: auto")
        search_type_panel.add( SearchTypePanel() )
        search_type_panel.add_style("min-height: 100px")
        search_type_panel.add_style("height: calc(100vh - 180px)")
        search_type_panel.add_class("spt_resizable")


        panel = {
            'widget': search_type_panel,
            'title': 'Search Type Manager',
            'width': '50%'
        }
        panels.append(panel)

        """
        from tactic.ui.container import TabWdg
        config_xml = '''
        <config>
        <tab>
        <element name="Help">
            <display class='tactic.ui.app.HelpContentWideWdg'>
              <alias>main</alias>
              <width>1000px</width>
            </display>
        </element>
        </tab>
        </config>
        '''

        div = DivWdg()
        tab = TabWdg(show_add=False, config_xml=config_xml, tab_offset=5)
        div.add(tab)
        div.add_style("margin: 0px -6px -6px -6px")


        panel = {
            'widget': div,
            #'title': 'Data',
            'title': None,
            'width': '100%',
        }
        panels.append(panel)

        """

        return panels


    def get_display(self):

        # set the sobjects to all the widgets then preprocess
        for widget in self.widgets:
            widget.set_sobjects(self.sobjects)
            widget.set_parent_wdg(self)
            # preprocess the elements
            widget.preprocess()


        top = self.top
        self.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)
        inner.add_color("background", "background")
        inner.add_color("color", "color")
        inner.add_class("spt_dashboard_top")

        title = DivWdg()
        inner.add(title)
        title.add(self.get_title())
        title.add_style("font-size: 18px")
        title.add_style("font-weight: bold")
        title.add_style("text-align: center")
        title.add_style("padding: 10px")
        #title.add_style("margin: -10px -10px 10px -10px")

        #temp solution. Disable the frame title showing, so have more space for the view table
        title.add_style("display: none")

        title.add_color("background", "background3")

        #table = Table()
        from tactic.ui.container import ResizableTableWdg
        table = Table()
        inner.add(table)
        table.add_style("width: 100%")
        table.add_style("box-sizing: border-box")

        panels = self.get_panels()

        for panel in panels:
            tr = table.add_row()
            #td = table.add_cell(resize=False)
            td = table.add_cell()
            td.add_style("min-height: 100px")

            td.add_style("vertical-align: top")


            panel = self.get_panel_wdg(td, panel)
            td.add(panel)

        return top



    def get_title(self):
        return "Project Configuration"


class UserConfigWdg(ProjectConfigWdg):

    def get_title(self):
        return "Manage Users"

    def get_help_alias(self):
        return 'project-startup-manage-users'


    def get_panels(self):

        panels = []

        show_security = self.kwargs.get("show_security") or ""
        show_add = self.kwargs.get("show_add") or ""
        view = self.kwargs.get("view") or ""
        filter_mode = self.kwargs.get("filter_mode") or ""
        show_help = self.kwargs.get("show_help") or ""
        show_search_limit = self.kwargs.get("show_search_limit") or ""

        from tactic.ui.container import TabWdg
        config_xml = []

        config_xml.append('''
        <config>
        ''')

        config_xml.append('''
        <tab>
        <element name="Users">
            <display class='tactic.ui.startup.UserPanelWdg'>
                <show_security>%s</show_security>
                <show_add>%s</show_add>
                <view>%s</view>
                <filter_mode>%s</filter_mode>
                <show_help>%s</show_help>
                <show_search_limit>%s</show_search_limit>
            </display>
        </element>
          ''' %(show_security, show_add, view, filter_mode, show_help, show_search_limit))

        config_xml.append('''
        <element name="Group Assignment">
            <display class='tactic.ui.startup.UserSecurityWdg'/>
        </element>
          ''')


        config_xml.append('''
        <element name="Group Security">
            <display class='tactic.ui.startup.SecurityWdg'/>
        </element>
        ''')

        config_xml.append('''
        </tab>
        </config>
        ''')



        config_xml = "\n".join(config_xml)

        tab = TabWdg(show_add=False, config_xml=config_xml)


        panel = {
            'widget': tab,
            'title': None,
            'width': '100%',
            'height': '100%'
        }
        panels.append(panel)

        return panels



class SearchTypePanel(BaseRefreshWdg):

    def get_display(self):

        web = WebContainer.get_web()
        show_multi_project = web.get_form_value('show_multi_project')
        project = Project.get()
        search_type_objs = project.get_search_types(include_multi_project=show_multi_project)


        top = self.top
        top.add_class("spt_panel_stype_list_top")
        #top.add_style("min-width: 400px")
        #top.add_style("max-width: 1000px")
        #top.add_style("width: 100%")
        top.center()


        shelf_wdg = DivWdg()
        top.add(shelf_wdg)
        shelf_wdg.add_style("display: flex")
        shelf_wdg.add_style("align-items: center")

        button = ActionButtonWdg(title="Add", tip="Add New Searchable Type (sType)", icon="FAS_PLUS")
        shelf_wdg.add(button)
        button.add_style("display: inline-block")
        button.add_style("vertical-align: middle")
        button.add_style("margin-top: 0px")
        button.add_style("margin-right: 15px")
        button.add_style("margin-left: 5px")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.app.SearchTypeCreatorWdg';

            var kwargs = {
            };
            var popup = spt.panel.load_popup("Create New Searchable Type", class_name, kwargs);

            var top = bvr.src_el.getParent(".spt_panel_stype_list_top");
            popup.on_register_cbk = function() {
                spt.panel.refresh(top);
            }

            '''
        } )

        cb = CheckboxWdg('show_multi_project', label=' show multi-project')
        if show_multi_project:
            cb.set_checked()
        cb.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
                var panel = bvr.src_el.getParent('.spt_panel_stype_list_top')
                spt.panel.refresh(panel, {show_multi_project: bvr.src_el.checked});
            '''
            })
        span = SpanWdg(css='small')
        shelf_wdg.add(span)
        shelf_wdg.add(cb)


        button = ActionButtonWdg(title="Setup", tip="Advanced Setup", icon=IconWdg.ADVANCED, color="secondary")
        shelf_wdg.add(button)
        button.add_style("margin-top: 0px")
        button.add_style("margin-left: 15px")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.app.ProjectStartWdg';
            spt.tab.set_main_body_tab()
            spt.tab.add_new("project_setup", "Project Setup", class_name)
            '''
        } )




        top.add("<br clear='all'/>")
        top.add("<br clear='all'/>")

        #search_type_objs = []
        if not search_type_objs:
            """
            arrow_div = DivWdg()
            #top.add(arrow_div)
            icon = IconWdg("Click to Add", IconWdg.ARROW_UP_LEFT_32)
            icon.add_style("margin-top: -20")
            icon.add_style("margin-left: -15")
            icon.add_style("position: absolute")
            arrow_div.add(icon)
            arrow_div.add("&nbsp;"*5)
            arrow_div.add("<b>Click to Add</b>")
            arrow_div.add_style("position: relative")
            arrow_div.add_style("margin-top: 5px")
            arrow_div.add_style("margin-left: 20px")
            arrow_div.add_style("float: left")
            arrow_div.add_style("padding: 25px")
            arrow_div.set_box_shadow("0px 5px 20px")
            arrow_div.set_round_corners(30)
            arrow_div.add_color("background", "background")
            """

            div = DivWdg()
            top.add(div)
            div.add_border()
            div.add_style("min-height: 180px")
            div.add_style("width: 600px")
            div.add_style("margin: 30px auto")
            div.add_style("padding: 20px")
            div.add_color("color", "color3")
            div.add_color("background", "background3")
            div.add_style("box-shadow: 0px 0px 15px %s" % div.get_color("shadow"))
            div.add_style("border-radius: 10px")


            icon = IconWdg( "WARNING", IconWdg.WARNING )
            div.add(icon)
            div.add("<b>No Searchable Types have been created</b>")
            div.add("<br/><br/>")
            div.add("Searchables Types contain lists of items that are managed in this project.  Each item will automatically have the ability to have files checked into it, track tasks and status and record work hours.")
            div.add("<br/>"*2)
            div.add("For more information, read the help docs: ")
            from tactic.ui.app import HelpButtonWdg
            help = HelpButtonWdg(alias="main")
            help.add_style("text-align: center")
            div.add("<br/>")
            div.add("<br/>")
            div.add(help)
            div.add("<br/>")
            div.add("Click on the 'Add' button above to start adding new types.")
            return top


        div = DivWdg()
        top.add(div)
        #div.add_style("max-height: 300px")
        #div.add_style("overflow-y: auto")



        table = Table()
        div.add(table)
        table.add_style("margin-top: 14px")
        table.add_style("width: 100%")
        table.add_color("color", "color")



        # group mouse over
        table.add_relay_behavior( {
            'type': "mouseover",
            'bvr_match_class': 'spt_row',
            'cbjs_action': "spt.mouse.table_layout_hover_over({}, {src_el: bvr.src_el, add_color_modifier: -2})"
        } )
        table.add_relay_behavior( {
            'type': "mouseout",
            'bvr_match_class': 'spt_row',
            'cbjs_action': "spt.mouse.table_layout_hover_out({}, {src_el: bvr.src_el})"
        } )

        border_color = table.get_color("border")


        tr = table.add_row()
        tr.add_style("height: 30px")
        tr.add_color("color", "color")
        tr.add_color("background", "background", -3)
        tr.add_style("border-bottom: solid 1px %s" % border_color)
        th = table.add_header("")
        th.add_style("text-align: left")
        th = table.add_header("Title")
        th.add_style("text-align: left")
        th = table.add_header("# Items")
        th.add_style("text-align: left")
        th = table.add_header("View")
        th.add_style("text-align: left")
        th = table.add_header("Add")
        th.add_style("text-align: left")
        th = table.add_header("Import")
        th.add_style("text-align: left")
        th = table.add_header("Custom<br/>Columns")
        th.add_style("text-align: left")
        th = table.add_header("Column<br/>Definition")
        th.add_style("text-align: left")
        th = table.add_header("Workflow")
        th.add_style("text-align: left")
        th = table.add_header("Notifications")
        th.add_style("text-align: left")
        th = table.add_header("Triggers")
        th.add_style("text-align: left")
        th = table.add_header("Edit")
        th.add_style("text-align: left")
        #th = table.add_header("Security")
        #th.add_style("text-align: left")



        for i, search_type_obj in enumerate(search_type_objs):
            tr = table.add_row()
            tr.add_class("spt_row")

            if not i or not i%2:
                tr.add_color("background", "background")
            else:
                tr.add_color("background", "background", -2 )


            thumb = ThumbWdg()
            thumb.set_sobject(search_type_obj)
            thumb.set_icon_size(30)
            td = table.add_cell(thumb)



            search_type = search_type_obj.get_value("search_type")
            title = search_type_obj.get_title()

            table.add_cell(title)

            try:
                search = Search(search_type)
                count = search.get_count()
                if count:
                    table.add_cell("%s item/s" % count)
                else:
                    table.add_cell("&nbsp;")
            except:
                td = table.add_cell("&lt; No table &gt;")
                td.add_style("font-style: italic")
                td.add_style("color: #F00")
                continue



            #search = Search(search_type)
            #search.add_interval_filter("timestamp", "today")
            #created_today = search.get_count()
            #table.add_cell(created_today)



            td = table.add_cell()
            button = IconButtonWdg(title="View", icon="FA_SEARCH")
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'title': title,
                'cbjs_action': '''

                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    view: 'table',
                    'simple_search_view': 'simple_search'
                };

                // use tab
                var top = bvr.src_el.getParent(".spt_dashboard_top");
                spt.tab.set_tab_top(top);
                spt.tab.add_new(bvr.title, bvr.title, class_name, kwargs);
                //spt.panel.load_popup(bvr.title, class_name, kwargs);

                '''
            } )
            button.add_style("float: left")


            arrow_button = IconButtonWdg(tip="More Views", icon=IconWdg.ARROWHEAD_DARK_DOWN)
            arrow_button.add_style("margin-left: 20px")
            td.add(arrow_button)

            cbk = '''
            var activator = spt.smenu.get_activator(bvr);

            var class_name = bvr.class_name;
            var layout = bvr.layout;

            var kwargs = {
                search_type: bvr.search_type,
                layout: layout,
                view: bvr.view,
                simple_search_view: 'simple_search',
                element_names: bvr.element_names,
            };

            // use tab
            var top = activator.getParent(".spt_dashboard_top");
            spt.tab.set_tab_top(top);
            spt.tab.add_new('%s', '%s', class_name, kwargs);
            ''' % (title, title)


            from tactic.ui.panel import SwitchLayoutMenu
            SwitchLayoutMenu(search_type=search_type, activator=arrow_button, cbk=cbk, is_refresh=False)

            td = table.add_cell()
            button = IconButtonWdg(title="Add", icon="FA_PLUS")
            td.add(button)
            button.add_behavior( {
                'type': 'listen',
                'search_type': search_type,
                'event_name': 'startup_save:' + search_type_obj.get_title(),
                'title': search_type_obj.get_title(),
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_dashboard_top");
                spt.tab.set_tab_top(top);
                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    view: 'table',
                    'simple_search_view': 'simple_search'
                };

                spt.tab.add_new(bvr.title, bvr.title, class_name, kwargs);
 

                '''
            } )
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'title': search_type_obj.get_title(),
                'cbjs_action': '''

                var top = bvr.src_el.getParent(".spt_dashboard_top");
                spt.tab.set_tab_top(top);

                var class_name = 'tactic.ui.panel.EditWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    view: "insert",
                    save_event: "startup_save:" + bvr.title
                }
                spt.panel.load_popup("Add New Items ("+bvr.title+")", class_name, kwargs);

                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    view: 'table',
                    'simple_search_view': 'simple_search'
                };

                spt.tab.add_new(bvr.title, bvr.title, class_name, kwargs);
                '''
            } )


            """
            td = table.add_cell()
            button = IconButtonWdg(title="Check-in", icon=IconWdg.PUBLISH)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'title': title,
                'cbjs_action': '''

                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    view: 'checkin',
                    element_names: ['preview','code','name','description','history','general_checkin','notes']
                };

                // use tab
                var top = bvr.src_el.getParent(".spt_dashboard_top");
                spt.tab.set_tab_top(top);
                spt.tab.add_new(bvr.title, bvr.title, class_name, kwargs);
                //spt.panel.load_popup(bvr.title, class_name, kwargs);

                '''
            } )
            """





            td = table.add_cell()
            button = IconButtonWdg(title="Import", icon="FA_UPLOAD")
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'title': "Import Data",
                'cbjs_action': '''

                var class_name = 'tactic.ui.widget.CsvImportWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                };

                spt.panel.load_popup(bvr.title, class_name, kwargs);

                '''
            } )



            td = table.add_cell()
            button = IconButtonWdg(title="Custom Columns", icon="FAS_DATABASE")
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'title': "Add Custom Columns",
                'cbjs_action': '''
                var class_name = 'tactic.ui.startup.ColumnEditWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                };
                spt.panel.load_popup(bvr.title, class_name, kwargs);

                '''
            } )




            td = table.add_cell()
            button = IconButtonWdg(title="Edit Definition", icon="FAS_COLUMNS")
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'cbjs_action': '''

                var class_name = 'tactic.ui.panel.EditWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                }
                var class_name = 'tactic.ui.panel.SearchTypeManagerWdg';
                spt.panel.load_popup("Column Definiton for ("+bvr.search_type+")", class_name, kwargs);

                '''
            } )


            td = table.add_cell()
            button = IconButtonWdg(title="Workflow", icon="FA_SITEMAP")
            button.add_class("fa-rotate-270")
            button.add_style("float: left")
            td.add(button)

            search = Search("sthpw/pipeline")
            search.add_filter("search_type", search_type)
            count = search.get_count()
            if count:
                check = IconWdg( "Has Items", IconWdg.CHECK, width=8 )
                td.add(check)
                #check.add_style("margin-left: 0px")
                check.add_style("margin-top: 4px")




            button.add_behavior( {
                'type': 'click_up',
                'title': 'Workflow',
                'search_type': search_type,
                'cbjs_action': '''
                var class_name = 'tactic.ui.startup.PipelineEditWdg';
                var kwargs = {
                    search_type: bvr.search_type
                };
                spt.panel.load_popup(bvr.title, class_name, kwargs);
                '''
            } )
 


            td = table.add_cell()
            button = IconButtonWdg(title="Notifications", icon="FA_ENVELOPE")
            button.add_style("float: left")
            td.add(button)

            search = Search("sthpw/notification")
            search.add_filter("search_type", search_type)
            count = search.get_count()
            if count:
                check = IconWdg( "Has Items", IconWdg.CHECK, width=8 )
                td.add(check)
                #check.add_style("margin-left: 0px")
                check.add_style("margin-top: 4px")






            button.add_behavior( {
                'type': 'click_up',
                'title': 'Trigger',
                'search_type': search_type,
                'cbjs_action': '''

                var class_name = 'tactic.ui.tools.TriggerToolWdg';
                var kwargs = {
                    mode: "search_type",
                    search_type: bvr.search_type
                };
                spt.panel.load_popup(bvr.title, class_name, kwargs);
                '''
            } )


            td = table.add_cell()
            button = IconButtonWdg(title="Triggers", icon="FA_BOLT")
            td.add(button)
            button.add_style("float: left")

            search = Search("config/trigger")
            search.add_filter("search_type", search_type)
            count = search.get_count()
            if count:
                check = IconWdg( "Has Items", IconWdg.CHECK, width=8 )
                td.add(check)
                #check.add_style("margin-left: 0px")
                check.add_style("margin-top: 4px")


            button.add_behavior( {
                'type': 'click_up',
                'title': 'Trigger',
                'search_type': search_type,
                'cbjs_action': '''

                var class_name = 'tactic.ui.tools.TriggerToolWdg';
                var kwargs = {
                    mode: "search_type",
                    search_type: bvr.search_type
                };
                spt.panel.load_popup(bvr.title, class_name, kwargs);
                '''
            } )





            td = table.add_cell()
            button = IconButtonWdg(title="Edit Searchable Type", icon="FA_EDIT")
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_key': search_type_obj.get_search_key(),
                'cbjs_action': '''

                var class_name = 'tactic.ui.panel.EditWdg';
                var kwargs = {
                    search_type: "sthpw/sobject",
                    view: "edit_startup",
                    search_key: bvr.search_key
                }
                spt.panel.load_popup("Edit Searchable Type", class_name, kwargs);


                '''
            } )





 
            """
            td = table.add_cell()
            button = IconButtonWdg(title="Security", icon=IconWdg.LOCK)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'title': 'Trigger',
                'search_type': search_type,
                'cbjs_action': '''
                alert("security");
                '''
            } )
            """


        columns_wdg = DivWdg()
        top.add(columns_wdg)


        return top



class UserPanelWdg(BaseRefreshWdg):

    def get_help_alias(self):
        return 'project-startup-manage-users'

    def get_display(self):

        filter_mode = self.kwargs.get("filter_mode")
        show_add = self.kwargs.get("show_add") or True
        show_security = self.kwargs.get("show_security") or True
        show_search_limit = self.kwargs.get("show_search_limit") or True
        show_help = self.kwargs.get("show_help") or True

        show_toolbar = self.kwargs.get("show_toolbar") or True

        project = Project.get().get_code()

        if filter_mode == "project":
            new_filter = "sthpw/login_group['project_code', '%s'].sthpw/login_in_group." % project 
        else:
            new_filter = ""

        expr_filter = "%ssthpw/login['login','not in','admin|guest']['begin']['license_type','user']['license_type','is','NULL']['or']" % new_filter
        sudo = Sudo()
        try:
            current_users = Search.eval("@COUNT(%s)" %expr_filter)
        finally:
            sudo.exit()

        top = self.top
        top.add_class("spt_panel_user_top")
        top.add_style("min-width: 400px")
        
        tool_div = DivWdg()
        tool_div.add_style('display','inline-flex')
        tool_div.add_style("align-items: center")
        tool_div.add_style('width','50%')
        tool_div.add_style('margin-top','5px')
     
        if show_add not in ['false', False]:
            button = ActionButtonWdg(title="Add", tip="Add New User", color="secondary")
            tool_div.add(button)
        
            button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''

                var class_name = 'tactic.ui.panel.EditWdg';
                
                var kwargs = {
                    search_type: "sthpw/login",
                    view: "insert",
                    show_header: false
                }
                var popup = spt.panel.load_popup("Create New User", class_name, kwargs);
                var tab_top = bvr.src_el.getParent(".spt_tab_top");
                popup.on_save_cbk = function(){
                    spt.tab.set_tab_top(tab_top);
                    spt.tab.reload_selected();
                }

                '''
            } )
        else:
            tool_div.add_style('position','relative')
            tool_div.add_style('top','-8px')


        show_count = self.kwargs.get("show_count")
        show_count = True
        if show_count in ['true', True]:
            security = Environment.get_security()
            license = security.get_license()
            num_left = license.get_num_licenses_left()
            current_users = license.get_current_users()
            #max_users = license.get_max_users()


            if current_users:
                div = DivWdg('Users')
                badge_span = SpanWdg(css='badge')
                badge_span.add_style('margin-left','6px')
                badge_span.add(current_users)
                div.add(badge_span)
                tool_div.add(div)

            tool_div2 = DivWdg()
            # tool_div.add_style('margin-bottom','8px')
            tool_div2.add_style('display','inline-flex')
            tool_div2.add_style('width','50%')


        
            if num_left < 1000:
                div = DivWdg('Users Left')
                div.add_styles("margin: 0 0 6px 20px")
                badge_span = SpanWdg(css='badge')
                badge_span.add_style('margin-left','6px')
                badge_span.add(num_left)
                div.add(badge_span)
                tool_div.add(div)


            if show_security not in ['false', False]:
                button = ActionButtonWdg(title="Security", color="secondary")
                button.add_style('align-self: flex-end')
                #button.add_styles("position: absolute; right: 10px;")
                tool_div2.add(button)
                #button.add_style("margin-top: -8px")
                button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var class_name = 'tactic.ui.startup.SecurityWdg';
                spt.tab.set_main_body_tab()
                spt.tab.add_new("Security", "Security", class_name)
                '''
                } )
            else:
                tool_div.add_style('position','relative')
                tool_div.add_style('top','0px')


        if show_toolbar in ['true', True]:
            top.add(tool_div)
            top.add(tool_div2)

        br = HtmlElement.br(clear=True)
        top.add(br)



        if not current_users:
            div = DivWdg()
            top.add(div)
            div.add_style("text-align: center")
            div.add_border()
            div.add_style("min-height: 150px")
            div.add_style("margin: 30px auto")
            div.add_style("padding: 30px 20px 30px 20px")
            div.add_style("width: 60%")
            div.add_style("max-width: 800px")
            div.add_color("color", "color3")
            div.add_color("background", "background3")
            icon = IconWdg( "WARNING", "FA_WARNING" )
            div.add(icon)
            div.add("<b> No users have been added</b>")
            div.add("<br/><br/>")
            div.add("For more information, read the help docs: ")
            from tactic.ui.app import HelpButtonWdg
            help = HelpButtonWdg(alias=self.get_help_alias())
            help.add_style("margin-top: 3px")
            div.add(help)
            div.add("<br/>")
            div.add("Click on the 'Add' button above to start adding new users.")

            return top




        div = DivWdg()
        top.add(div)
        #div.add_style("max-height: 300px")
        #div.add_style("overflow-y: auto")

        view = self.kwargs.get("view")

        if not view:
            view = "manage_user"

        expr = "@SEARCH(%s)" %expr_filter
        panel = ViewPanelWdg(
                search_type='sthpw/login',
                view=view,
                show_shelf=False,
                show_insert='true',
                show_gear='false',
                show_select='false',
                #height='700',
                expression=expr,
                simple_search_view='login_filter',
                show_column_manager='false',
                show_layout_switcher='false',
                show_expand='false',
                show_search_limit=show_search_limit,
                show_help=show_help,
                show_border="horizontal",


        )
        div.add(panel)
        div.add_style('margin-top', '4px')

        return top







