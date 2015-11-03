""" Action definitions for HexEdit task

"""
# Enthought library imports.
from traits.api import on_trait_change, Any, Int
from pyface.action.api import Action, ActionItem
from pyface.tasks.action.api import TaskAction, EditorAction

from omnimon.framework.actions import *
from commands import *

class FontChoiceGroup(TaskDynamicSubmenuGroup):
    """Dynamic menu group to display the available fonts
    """
    #### 'DynamicSubmenuGroup' interface ######################################

    event_name = 'fonts_changed'

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_items(self, event_data=None):
        items = []
        print event_data
        if event_data is not None:
            for font in event_data:
                action = UseFontAction(font=font)
                items.append(ActionItem(action=action))
            
        return items

class UseFontAction(EditorAction):
    font = Any
    
    def _name_default(self):
        return "%s" % (self.font['name'])
    
    def perform(self, event):
        self.active_editor.set_font(self.font)

class LoadFontAction(EditorAction):
    name = 'Load Font...'
    
    def perform(self, event):
        dialog = FileDialog(parent=event.task.window.control)
        if dialog.open() == OK:
            self.active_editor.load_font(dialog.path)

class GetFontFromSelectionAction(EditorAction):
    name = 'Get Font From Selection'
    enabled_name = 'grid_range_selected'
    
    def perform(self, event):
        self.active_editor.get_font_from_selection()


class FontStyleBaseAction(EditorAction):
    """Radio buttons for changing font style
    """
    # Traits
    style = 'radio'
    
    font_mode = Int

    def perform(self, event):
        self.active_editor.set_font(font_mode=self.font_mode)

    @on_trait_change('active_editor.font_mode')
    def _update_checked(self):
        if self.active_editor:
            self.checked = self.active_editor.font_mode == self.font_mode


class DisassemblerBaseAction(EditorAction):
    """Radio buttons for changing font style
    """
    # Traits
    style = 'radio'
    
    disassembler = Any
    
    def _name_default(self):
        return self.disassembler.menu_name

    def perform(self, event):
        self.active_editor.set_disassembler(self.disassembler)

    @on_trait_change('active_editor.disassembler')
    def _update_checked(self):
        if self.active_editor:
            self.checked = self.active_editor.disassembler == self.disassembler


class SegmentParserAction(EditorAction):
    """Radio buttons for changing font style
    """
    # Traits
    style = 'radio'
    
    segment_parser = Any
    
    def _name_default(self):
        return self.segment_parser.menu_name

    def perform(self, event):
        self.active_editor.set_segment_parser(self.segment_parser)
        self.active_editor.view_segment_number(0)

    @on_trait_change('active_editor.segment_parser')
    def _update_checked(self):
        if self.active_editor:
            self.checked = self.active_editor.document.segment_parser == self.segment_parser

class SegmentChoiceGroup(TaskDynamicSubmenuGroup):
    """Dynamic menu group to display the available fonts
    """
    #### 'DynamicSubmenuGroup' interface ######################################

    event_name = 'segments_changed'

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_items(self, event_data=None):
        items = []
        print event_data
        if event_data is not None:
            for i, segment in enumerate(event_data):
                action = UseSegmentAction(segment=segment, segment_number=i)
                items.append(ActionItem(action=action))
            
        return items

class UseSegmentAction(EditorAction):
    segment = Any
    
    segment_number = Int
    
    def _name_default(self):
        return str(self.segment)
    
    def perform(self, event):
        self.active_editor.view_segment_number(self.segment_number)


class IndexRangeAction(EditorAction):
    enabled_name = 'can_copy'
    cmd = None
    
    def _name_default(self):
        return self.cmd.pretty_name
    
    def perform(self, event):
        e = self.active_editor
        cmd = self.cmd(e.segment, e.anchor_start_index, e.anchor_end_index)
        self.active_editor.process_command(cmd)

class ZeroAction(IndexRangeAction):
    cmd = ZeroCommand

class FFAction(IndexRangeAction):
    cmd = FFCommand

class SetHighBitAction(IndexRangeAction):
    cmd = SetHighBitCommand

class ClearHighBitAction(IndexRangeAction):
    cmd = ClearHighBitCommand

class BitwiseNotAction(IndexRangeAction):
    cmd = BitwiseNotCommand

class LeftShiftAction(IndexRangeAction):
    cmd = LeftShiftCommand

class RightShiftAction(IndexRangeAction):
    cmd = RightShiftCommand

class LeftRotateAction(IndexRangeAction):
    cmd = LeftRotateCommand

class RightRotateAction(IndexRangeAction):
    cmd = RightRotateCommand


class IndexRangeValueAction(IndexRangeAction):
    def _name_default(self):
        return self.cmd.pretty_name + "..."
    
    def get_value(self, editor):
        import wx
        dialog = wx.TextEntryDialog(editor.window.control, "Enter byte value: (prefix with 0x or $ for hex)", "Byte Value")

        result = dialog.ShowModal()
        if result == wx.ID_OK:
            text = dialog.GetValue()
            try:
                if text.startswith("0x"):
                    value = int(text[2:], 16)
                elif text.startswith("$"):
                    value = int(text[1:], 16)
                else:
                    value = int(text)
            except (ValueError, TypeError):
                value = None
        dialog.Destroy()
        return value
        
    def show_dialog(self, editor):
        e = editor
        value = self.get_value(editor)
        if value is not None:
            cmd = self.cmd(e.segment, e.anchor_start_index, e.anchor_end_index, value)
            self.active_editor.process_command(cmd)
            
    def perform(self, event):
        GUI.invoke_later(self.show_dialog, self.active_editor)

class SetValueAction(IndexRangeValueAction):
    cmd = SetValueCommand

class OrWithAction(IndexRangeValueAction):
    cmd = OrWithCommand

class AndWithAction(IndexRangeValueAction):
    cmd = AndWithCommand

class XorWithAction(IndexRangeValueAction):
    cmd = XorWithCommand

class RampUpAction(IndexRangeValueAction):
    cmd = RampUpCommand

class RampDownAction(IndexRangeValueAction):
    cmd = RampDownCommand

class AddValueAction(IndexRangeValueAction):
    cmd = AddValueCommand

class SubtractValueAction(IndexRangeValueAction):
    cmd = SubtractValueCommand

class SubtractFromAction(IndexRangeValueAction):
    cmd = SubtractFromCommand

class MultiplyAction(IndexRangeValueAction):
    cmd = MultiplyCommand

class DivideByAction(IndexRangeValueAction):
    cmd = DivideByCommand

class DivideFromAction(IndexRangeValueAction):
    cmd = DivideFromCommand


class PasteAndRepeatAction(EditorAction):
    name = 'Paste and Repeat'
    accelerator = 'Shift+Ctrl+V'
    tooltip = 'Paste and repeat clipboard data until current selection is filled'
    enabled_name = 'can_copy'
    
    def perform(self, event):
        e = self.active_editor
        data_obj = e.get_paste_data_object()
        if data_obj is not None:
            bytes = e.get_numpy_from_data_object(data_obj)
            cmd = PasteAndRepeatCommand(e.segment, e.anchor_start_index, e.anchor_end_index, bytes)
            self.active_editor.process_command(cmd)